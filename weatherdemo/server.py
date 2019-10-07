import flask
import json
import logging
import threading

from weatherdemo import poller


app = flask.Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler('weather-demo.log', mode='w+'))


class PollingThreadManager(object):

    def __init__(self):
        self._lock = threading.Lock()
        self._current_thread = None

    @property
    def current(self):
        """Returns a reference to the currently running weather emitter thread."""
        self._lock.acquire()
        thread = self._current_thread
        self._lock.release()
        return thread

    def spawn(self, host, token, port=8088, disable_ssl_verify=False, index='main', upload_interval=0.5):
        """Creates and starts a new weather emitter thread with the given settings (mostly for HEC)."""
        self._lock.acquire()
        if self._current_thread:
            self._current_thread.stop()
        new_thread = poller.WeatherListener(host, token, port=port, disable_ssl_verify=disable_ssl_verify, index=index,
                                            upload_interval=upload_interval)
        new_thread.start()
        new_thread_name = new_thread.name
        self._current_thread = new_thread
        self._lock.release()

        return new_thread_name


thread_manager = PollingThreadManager()


@app.route('/')
def home():
    """Serves the polling UI."""
    return flask.render_template('index.html')


@app.route('/start', methods=['GET'])
def start():
    """Starts a new weather emitter thread and includes the newly created thread name in the response for debugging."""
    params = flask.request.args
    if 'host' not in params or 'token' not in params:
        return flask.Response(status=400, content_type='application/json', response=json.dumps({
            'status': 400,
            'reason': 'Request must include a Splunk hostname and an HEC token to begin polling.'
        }))

    thread_name = thread_manager.spawn(
        params['host'],
        params['token'],
        port=int(params.get('port', 8088)),
        disable_ssl_verify=True if params.get('disable_ssl_verify') == 'true' else False,
        index=params.get('index', 'main'),
        upload_interval=float(params.get('upload_interval', 0.5)))
    return flask.Response(status=200, content_type='application/json', response=json.dumps({
        'status': 200,
        'thread_name': thread_name
    }))


@app.route('/stop', methods=["GET"])
def stop():
    """Cancels the active weather emitter thread."""
    weather_thread = thread_manager.current
    if weather_thread:
        weather_thread.stop()
    return flask.Response(status=200)


# TODO: It's probably more appropriate to implement this via websocket.
@app.route('/last', methods=['GET'])
def last():
    """
    Returns the last event uploaded by the active weather emitter thread if there is one. If there is no event, an
    empty 204 response wll be returned. Any errors from the weather emitter thread will be propagated through various
    4XX responses. If the response body is not empty, it will be JSON formatted.
    """
    weather_thread = thread_manager.current
    if not weather_thread:
        return flask.Response(status=400, content_type='application/json', response=json.dumps({
            'status': 400,
            'error': 'The weather event emitter has not been started.'
        }))

    ok, event = weather_thread.poll(default=(True, None))
    if not event:
        return flask.Response(status=204)
    status = 200 if ok else 400
    return flask.Response(status=status, response=json.dumps(event, sort_keys=True), content_type='application/json')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=False)
