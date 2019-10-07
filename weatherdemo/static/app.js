'use strict';

// Form fields
const HOST_FIELD_ID = 'splunk-hostname';
const HEC_TOKEN_FIELD_ID = 'hec-token';
const PORT_FIELD_ID = 'port';
const INDEX_FIELD_ID = 'index';
const POLL_INTERVAL_FIELD_ID = 'poll-interval';
const DISABLE_SSL_VERIFY_CHECK_ID = 'disable-ssl-verify';

// Buttons
const START_POLLING_BUTTON_ID = 'start-polling-button';
const STOP_POLLING_BUTTON_ID = 'stop-polling-button';

// Content
const MOST_RECENT_EVENT_CARD = 'last-event-content';
const WAITING_FOR_DATA_TEXT = 'Waiting for events to start streaming...';


/**
 * Starts and stops the weather event emitter on the Raspberry Pi and displays the most recently published weather
 * event.
 */
class PollingController {

    constructor() {
        this.isPolling = false;
    }

    /**
     * Validates the Splunk info form and triggers weather event polling on the Raspberry Pi should validation succeed.
     */
    startPolling() {
        if (!validateFormValues()) {
            return;
        }
        setCardContent(WAITING_FOR_DATA_TEXT);
        const startUrl = '/start' + getFormValuesAsGetParameters();
        get(startUrl).then(() => {
                document.getElementById(START_POLLING_BUTTON_ID).setAttribute('disabled', 'disabled');
                document.getElementById(STOP_POLLING_BUTTON_ID).removeAttribute('disabled');
                this.isPolling = true;
                this.loadLatestEvent();
            }).catch(reason => {
                console.log('Catch block with reason: ' + reason);
                setCardContent(reason);
            });
    }

    /** Polls every 0.2 seconds for the latest uploaded event and updates recent event card appropriately. */
    loadLatestEvent() {
        get('/last').then(event => {
            console.log('Successful response with content: ' + event);
            if (event !== null) {
                setCardContent(event);
            }
            if (this.isPolling) {
                setTimeout(() => this.loadLatestEvent(), 200);
            }
        }).catch(reason => {
            console.log('Unsuccessful event with content: ' + event);
            setCardContent(reason);
            this.stopPolling();
        });
    }

    /**
     * Prevents further calls to loadLatestEvent until the user clicks Start Polling again, re-enable the start
     * polling button, and disables the stop polling button.
     */
    stopPolling() {
        get('/stop').then(() => {
            this.isPolling = false;
            document.getElementById(START_POLLING_BUTTON_ID).removeAttribute('disabled');
            document.getElementById(STOP_POLLING_BUTTON_ID).setAttribute('disabled', 'disabled');
        }).catch(reason => setCardContent(reason));
    }
}


/**
 * Returns whether the Splunk info form is correctly filled out. If it isn't, each incorrect field will be highlighted
 * in the UI.
 */
function validateFormValues() {
    // TODO: Provide more in-depth info on whether or not the current configuration indicated on the form is valid.
    const checkNonEmpty = (id) => {
        const element = document.getElementById(id);
        const value = element.value;
        if (value === '' || value === null) {
            element.classList.add('is-invalid');
            element.classList.remove('is-valid');
            return false;
        } else {
            element.classList.add('is-valid');
            element.classList.remove('is-invalid');
            return true;
        }
    };
    const hostCheck = checkNonEmpty(HOST_FIELD_ID);
    const tokenCheck = checkNonEmpty(HEC_TOKEN_FIELD_ID);
    return hostCheck && tokenCheck;
}


/**
 * Generates an object with key-value pairs from the start polling form that should be converted to GET URL parameters.
 * Empty form fields are left out.
 */
function getFormValuesAsGetParameters() {
    const addIfPresent = (params, key, id) => {
        const val = document.getElementById(id).value;
        if (val === null || val === '' || val === false || val === undefined) {
            return;
        }
        params.push(key + '=' + encodeURIComponent(val.trim()));
    };
    const params = [];
    addIfPresent(params, 'host', HOST_FIELD_ID);
    addIfPresent(params, 'token', HEC_TOKEN_FIELD_ID);
    addIfPresent(params, 'port', PORT_FIELD_ID);
    addIfPresent(params, 'index', INDEX_FIELD_ID);
    addIfPresent(params, 'upload_interval', POLL_INTERVAL_FIELD_ID);
    if (document.getElementById(DISABLE_SSL_VERIFY_CHECK_ID).checked) {
        params.push('disable_ssl_verify=true');
    }
    return '?' + params.join('&');
}


/** Fills in the recent event card. */
function setCardContent(content) {
    const element = document.getElementById(MOST_RECENT_EVENT_CARD);
    if (typeof content === 'object' && content !== null) {
        element.innerText = JSON.stringify(content, /* replacer= */ null, /* space= */ 4);
        return;
    }
    element.innerText = content;
}


/**
 * Sends a GET request to the given path on the Raspberry Pi server and returns a promise that will resolve with the
 * results of the request.
 *
 * @param path {String} the path on the Raspberry Pi server to send the request to
 * @returns {Promise<JSON>} the response from the request
 */
function get(path) {
    return new Promise((resolve, reject) => {
        const request = new XMLHttpRequest();
        request.onreadystatechange = () => {
            if (request.readyState !== XMLHttpRequest.DONE) {
                return;
            }
            request.status >= 200 && request.status < 300 ? resolve(request.response) : reject(request.response);
        };
        request.responseType = 'json';
        request.open('GET', path);
        request.send();
    });
}


/** Setup all of our event listeners. */
window.addEventListener('load',  () => {
    const pollingController = new PollingController();
    document.getElementById(START_POLLING_BUTTON_ID).addEventListener('click', () => pollingController.startPolling());
    document.getElementById(STOP_POLLING_BUTTON_ID).addEventListener('click', () => pollingController.stopPolling());
});
