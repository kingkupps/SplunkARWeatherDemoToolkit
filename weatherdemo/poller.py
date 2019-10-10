import queue
import requests
import sense_hat
import threading
import time


class PollingThread(threading.Thread):

    def __init__(self, **kwargs):
        super(PollingThread, self).__init__(**kwargs)
        self._lock = threading.Lock()
        self._should_stop = False
        self._queue = queue.Queue()

    def step(self):
        """
        Implements a single iteration of the polling thread. This should return a tuple of the form (bool, object) where
        bool determines whether to continue pooling and object can be consumed by other threads by calling self.poll().
        """
        raise NotImplementedError()

    def interval(self):
        """Returns the time in seconds between in step call."""
        raise NotImplementedError()

    def cleanup(self):
        """(Optional) Does any teardown or cleanup once the thread is done running."""
        pass

    def poll(self, default=None):
        """Returns the oldest result of self.step() or None if no default if no results are ready yet."""
        if self._queue.empty():
            return default
        return self._queue.get()

    def stop(self):
        """Makes sure that this thread finishes after the current call to self.step() is complete."""
        self._lock.acquire()
        self._should_stop = True
        self._lock.release()

    def is_cancelled(self):
        """Returns whether this thread has been cancelled."""
        self._lock.acquire()
        result = self._should_stop
        self._lock.release()
        return result

    def run(self):
        """
        Repeatedly runs self.step() with a wait of self.interval() seconds in between calls until the first element in
        the returned tuple is False. After the loop is finished self.cleanup is called.
        """
        while not self.is_cancelled():
            should_continue, value_to_post = self.step()
            self._queue.put(value_to_post)
            if not should_continue:
                break
            time.sleep(self.interval())
        self.cleanup()


class WeatherListener(PollingThread):

    def __init__(self, host, token, port=8088, disable_ssl_verify=False, index='ar-weather-demo', upload_interval=0.5):
        super(WeatherListener, self).__init__()
        self._url = '{host}:{port}/services/collector/event'.format(host=host, port=port)
        self._index = index
        self._upload_interval = upload_interval

        self._sense_hat = sense_hat.SenseHat()

        self._session = requests.Session()
        self._session.verify = not disable_ssl_verify
        self._session.max_redirects = 1
        self._session.headers.update({'Authorization': 'Splunk ' + token})

        # For debugging
        self.name = 'weather-polling-thread-' + str(id(self))

    def interval(self):
        return self._upload_interval

    def step(self):
        """Retrieves weather data from the Sense Hat and uploads the results to Splunk via HEC."""
        event = {
            'time': round(time.time(), 3),
            'index': self._index,
            'source': 'ar-weather-demo',
            'event': self._read_weather_data()
        }
        try:
            response = self._session.post(self._url, json=event, timeout=5)
            if response.status_code != 200:
                error = {
                    'status': response.status_code,
                    'reason': response.reason
                }
                if response.status_code == 403:
                    error['tip'] = 'Are you using the right HEC token?'
                elif response.status_code == 400:
                    error['tip'] = 'Are you uploading to an allowed index?'
                return False, (False, error)
        except Exception as e:
            error = {
                'status': 500,
                'reason': str(e),
                'tip': 'Are you connecting to the correct HEC port? Does the hostname start with http:// or https://?'
            }
            return False, (False, error)

        return True, (True, event)

    def _read_weather_data(self):
        temp = self._sense_hat.get_temperature()
        orientation = self._sense_hat.get_orientation()
        return {
            'temperature': {
                'celsius': round(temp),
                'fahrenheit': round((1.8 * temp) + 32)
            },
            'pressure': self._sense_hat.get_pressure(),
            'humidity': self._sense_hat.get_humidity(),
            'acceleration': self._sense_hat.get_accelerometer_raw(),
            'gyroscope': self._sense_hat.get_gyroscope_raw(),
            'compass': orientation,
            'direction': orientation['yaw']
        }

    def cleanup(self):
        self._session.close()
