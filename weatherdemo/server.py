import flask
import functools
import json
import threading

from weatherdemo import poller


app = flask.Flask(__name__)


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

    def spawn(self, **kwargs):
        """Creates and starts a new weather emitter thread with the given settings (mostly for HEC)."""
        self._lock.acquire()
        try:
            if self._current_thread:
                self._current_thread.stop()
            new_thread = poller.WeatherListener(**kwargs)
            new_thread.start()
            self._current_thread = new_thread
        finally:
            self._lock.release()


thread_manager = PollingThreadManager()


def propagate_exceptions(handler):
    @functools.wraps(handler)
    def decorate(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except Exception as e:
            return flask.Response(status=500, content_type='application/json', response=json.dumps({
                'status': 500,
                'reason': str(e)
            }))
    return decorate


@app.route('/')
@propagate_exceptions
def home():
    """Serves the polling UI."""
    return flask.render_template('index.html')


@app.route('/start', methods=['GET'])
@propagate_exceptions
def start():
    """Starts a new weather emitter thread and includes the newly created thread name in the response for debugging."""
    params = flask.request.args
    if 'host' not in params or 'token' not in params:
        return flask.Response(status=400, content_type='application/json', response=json.dumps({
            'status': 400,
            'reason': 'Request must include a Splunk hostname and an HEC token to begin polling.'
        }))

    thread_manager.spawn(host=params['host'], token=params['token'], port=int(params.get('port', 8088)),
                         disable_ssl_verify=True if params.get('disable_ssl_verify') == 'true' else False,
                         index=params.get('index', 'ar-weather-demo'),
                         upload_interval=float(params.get('upload_interval', 0.5)))
    return flask.Response(status=200)


@app.route('/stop', methods=['GET'])
@propagate_exceptions
def stop():
    """Cancels the active weather emitter thread."""
    weather_thread = thread_manager.current
    if weather_thread:
        weather_thread.stop()
    return flask.Response(status=200)


@app.route('/last', methods=['GET'])
@propagate_exceptions
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
    if ok and not event:
        return flask.Response(status=204)
    status = 200 if ok else 400
    return flask.Response(status=status, response=json.dumps(event, sort_keys=True), content_type='application/json')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=False)
