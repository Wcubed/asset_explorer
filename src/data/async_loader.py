import pathlib
from concurrent import futures

import data


class AsyncLoader:
    """
    Utility class that hands off the loading and scanning of asset directories to an other thread.
    """

    def __init__(self):
        # List of asset directories to scan.
        self._dirs_to_scan = []

        # Asynchronous executor.
        # Only 1 worker, because we are working on the file system.
        self._executor = futures.ThreadPoolExecutor(max_workers=1)

        # Directory that is currently being scanned.
        self._currently_scanning = None
        # The future associated with the current scan.
        self._future = None

    def queue_scan(self, directory):
        """
        Add a new directory to the scan queue.
        Immediately starts the scan if there is nothing else queued.
        :param directory:
        """
        self._dirs_to_scan.append(pathlib.Path(directory))
        self._maybe_start_next_scan()

    def get_maybe_result(self):
        """
        Retrieves the result from a finished scan, or `None` when it is not finished.
        Also starts the next scan.
        :return: `AssetDir` when a scan is done. `None` when it isn't.
        """
        if self._future is None or not self._future.done():
            return None

        result = self._future.result()
        self._future = None
        self._currently_scanning = None

        self._maybe_start_next_scan()
        return result

    def currently_scanning(self):
        """
        :return: The directory that is currently being scanned. `None` if we are not scanning anything.
        """
        return self._currently_scanning

    def queue_size(self):
        return len(self._dirs_to_scan)

    def _maybe_start_next_scan(self):
        """
        Starts a next scan if there is no scan running, and there is something queued.
        :return:
        """
        if self._future is not None:
            # Busy, or waiting for someone to get the result. can't start a new scan.
            return

        # Start the next scan.
        if len(self._dirs_to_scan) > 0:
            self._currently_scanning = self._dirs_to_scan.pop()
            # Start the next scan.
            self._future = self._executor.submit(data.recursive_load_asset_dir, self._currently_scanning)
