import hashlib
import logging
import os

from PyQt5.QtCore import QFileInfo, Qt, QStandardPaths
from PyQt5.QtGui import QPixmap


class Asset:
    def __init__(self, path: str):
        self._file_info = QFileInfo(path)

        # TODO: do we want to make this an application specific location?
        self._thumbnail_cache_dir = QStandardPaths.writableLocation(QStandardPaths.CacheLocation)

        # Thumbnail gets generated on request and cached here.
        self._thumbnail = None
        # Size of the square the current thumbnail fits into.
        self._thumbnail_size = 0

        # We use the `hexdigest` representation instead of the raw bytes, so we can output it as a string.
        # Which is needed in, for example, tables and the on-disk thumbnail cache.
        # The reason for `hashlib.md5` instead of the python `hash` function is that the built-in function is
        # randomized every session for security purposes.
        # We want consistent, non-security hashes.
        self._hash = hashlib.md5(self._file_info.absoluteFilePath().encode()).hexdigest()

    def get_hash(self):
        """
        Returns the filepath-based hash, which identifies this asset.
        """
        return self._hash

    def get_name(self) -> str:
        return self._file_info.fileName()

    def get_absolute_path(self) -> str:
        return self._file_info.absoluteFilePath()

    def load_image(self) -> QPixmap:
        # We don't cache the full sized image, so that we don't use multiple gigabytes of memory after a while.
        # TODO: do something if it goes wrong.
        image = QPixmap(self._file_info.absoluteFilePath())
        return image

    def load_thumbnail_cached(self, size: int) -> QPixmap:
        if self._thumbnail and size == self._thumbnail_size:
            # We already have a thumbnail in memory, and it is the right size.
            return self._thumbnail
        else:
            # Cache files are named: <hash>_<size>.png
            cache_file_path = self._thumbnail_cache_dir + "/" + self._hash + "_" + str(size) + ".png"
            if os.path.isfile(cache_file_path):
                # We already have a thumbnail of this size cached on disk.
                logging.debug("from disk cache")
                self._thumbnail = QPixmap(cache_file_path)
            else:
                image = self.load_image()
                # Scale with preserved aspect ratio, so the image fits in a square with sides of "size".
                # Uses bilinear filtering.
                if image.width() < image.height():
                    self._thumbnail = image.scaledToHeight(size, Qt.SmoothTransformation)
                else:
                    self._thumbnail = image.scaledToWidth(size, Qt.SmoothTransformation)

                # Save the thumbnail to disk.
                self._thumbnail.save(cache_file_path, "png")

        self._thumbnail_size = size

        return self._thumbnail
