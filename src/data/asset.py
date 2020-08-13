import hashlib
import os

from PyQt5.QtCore import QFileInfo, Qt, QStandardPaths
from PyQt5.QtGui import QPixmap, QPixmapCache


class Asset:
    """
    Keeps track of all the data associated with an asset.
    Can load images and generate / cache thumbnails on request.
    The thumbnails are stored in the global QPixmapCache with the hash as their key.
    """

    def __init__(self, path: str):
        self._file_info = QFileInfo(path)

        # TODO: do we want to make this an application specific location?
        self._thumbnail_cache_dir = QStandardPaths.writableLocation(QStandardPaths.CacheLocation)

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

    def get_relative_path(self, relative_to) -> str:
        return relative_to.relativeFilePath(self._file_info.absoluteFilePath())

    def load_image(self) -> QPixmap:
        # We don't cache the full sized image, so that we don't use multiple gigabytes of memory after a while.
        # TODO: do something if it goes wrong.
        image = QPixmap(self._file_info.absoluteFilePath())
        return image

    def load_thumbnail_cached(self, size: int) -> QPixmap:
        thumbnail_key = self._hash + "_" + str(size)
        # See if the thumbnail is already (or still) in the cache.
        # Returns `None` if it isn't.
        thumbnail = QPixmapCache.find(thumbnail_key)

        if thumbnail:
            # We already have a thumbnail in memory, and it is the right size.
            return thumbnail
        else:
            # Cache files are named: <hash>_<size>.png
            cache_file_path = self._thumbnail_cache_dir + "/" + thumbnail_key + ".png"
            if os.path.isfile(cache_file_path):
                # We already have a thumbnail of this size cached on disk.
                thumbnail = QPixmap(cache_file_path)
            else:
                image = self.load_image()
                # Scale with preserved aspect ratio, so the image fits in a square with sides of "size".
                # Uses bilinear filtering.
                if image.width() < image.height():
                    thumbnail = image.scaledToHeight(size, Qt.SmoothTransformation)
                else:
                    thumbnail = image.scaledToWidth(size, Qt.SmoothTransformation)

                # Save the thumbnail to disk.
                thumbnail.save(cache_file_path, "png")

            # Add the newly loaded / generated thumbnail to the cache.
            QPixmapCache.insert(thumbnail_key, thumbnail)

        return thumbnail
