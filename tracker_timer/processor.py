import logging
import queue

LOGGER = logging.getLogger(__name__)


def lowpass_filter(last_value, value, alpha=0.95):
    return last_value + (alpha * (value - last_value))


class DataProcessor:
    def __init__(self):
        self._queue = queue.Queue()
        self._should_stop = False

        self._last_filtered_rssi = None

    def start(self):
        LOGGER.info('Starting up...')
        while not self._should_stop:
            self._loop()

        LOGGER.info('Shutting down...')

    def stop(self):
        self._should_stop = True

    def queue_data(self, data):
        """Queues RSSI data to be processed.

        data: a dict in the format of {'timestamp': 0.00, 'rssi': [...]}
        """
        self._queue.put(data)

    def _loop(self):
        data = None
        try:
            data = self._queue.get(block=False)
        except queue.Empty:
            return

        timestamp = data['timestamp']
        rssi = data['rssi']

        filtered_rssi = self._filter_rssi(rssi, self._last_filtered_rssi)
        self._last_filtered_rssi = filtered_rssi

    @staticmethod
    def _filter_rssi(rssi, last_filtered_rssi):
        if not last_filtered_rssi:
            last_filtered_rssi = list(rssi)

        rssi_with_last = zip(rssi, last_filtered_rssi)
        filtered_rssi = [lowpass_filter(l, v) for l, v in rssi_with_last]

        return filtered_rssi

