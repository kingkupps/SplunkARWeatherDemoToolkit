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
        self._url = '{host}:{port}/services/collector'.format(host=host, port=port)
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
        weather_data = self._read_weather_data()
        current_time = round(time.time(), 3)
        metrics = []
        for metric_name, value in weather_data.items():
            metrics.append({
                'event': '{}={}'.format(metric_name, value),
                'time': current_time,
                'source': 'ar-weather-demo',
                'index': self._index,
                'fields': {
                    'metric_name': metric_name,
                    '_value': value
                }
            })

        try:
            response = self._session.post(self._url, json=metrics, timeout=5)
            if response.status_code != 200:
                error = response.json()
                error['tip'] = ('For some reason your weather data could not be uploaded. Check https://www.freecodecam'
                                'p.org/news/how-to-write-a-good-software-design-document-66fcf019569c/ under the POST '
                                'section for more details on why this happened.')
                return False, (False, error)
        except Exception as e:
            error = {
                'status': 500,
                'reason': str(e),
                'tip': 'Is there a typo in the Splunk host name? Is it prefixed by \'http://\' or \'https://\'?'
            }
            return False, (False, error)

        return True, (True, weather_data)

    def _read_weather_data(self):
        acceleration = self._sense_hat.get_accelerometer_raw()
        gyroscope = self._sense_hat.get_gyroscope_raw()
        return {
            'temperature': self._sense_hat.get_temperature(),
            'pressure': self._sense_hat.get_pressure(),
            'humidity': self._sense_hat.get_humidity(),
            'acceleration_x': acceleration['x'],
            'acceleration_y': acceleration['y'],
            'acceleration_z': acceleration['z'],
            'gyroscope_x': gyroscope['x'],
            'gyroscope_y': gyroscope['y'],
            'gyroscope_z': gyroscope['z'],
            'direction': self._sense_hat.get_orientation()['yaw']
        }

    def cleanup(self):
        self._session.close()
