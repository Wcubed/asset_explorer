import pathlib
import uuid

from PyQt5.QtCore import QStandardPaths, Qt
from PyQt5.QtGui import QPixmap, QPixmapCache


class Asset:
    # All the file extensions that count as assets.
    # All lowercase.
    ASSET_EXTENSIONS = ['.png']

    def __init__(self, path, asset_uuid=None):
        self._path = pathlib.Path(path).absolute()

        self._uuid = asset_uuid
        self._dirty = False

        if not self._uuid:
            # Asset was not seen before, so generate a new uuid.
            # We use uuid4 because we don't need cryptographically secure uuid's.
            # We just want a random uuid.
            self._uuid = uuid.uuid4()
            self._dirty = True

        self._thumbnail_cache_dir = pathlib.Path(QStandardPaths.writableLocation(QStandardPaths.CacheLocation))

    def name(self):
        return self._path.name

    def is_dirty(self):
        """
        And asset is dirty if it has been updated since the last save.
        :return:
        """
        return self._dirty

    def was_saved(self):
        """
        Call after saving the asset. Marks it as clean again.
        """
        self._dirty = False

    def absolute_path(self):
        """
        :return: The absolute path as a `pathlib.Path`.
        """
        return self._path

    def relative_path(self, relative_to: pathlib.Path):
        return self._path.relative_to(relative_to)

    def uuid(self):
        """
        :return: The unique uuid of this asset.
        """
        return self._uuid

    @staticmethod
    def is_asset(path) -> bool:
        """
        :param path: The path to check.
        :return: True if the path is an asset, false if not.
        """
        _path = pathlib.Path(path)
        return _path.is_file() and _path.suffix.lower() in Asset.ASSET_EXTENSIONS

    def load_image(self) -> QPixmap:
        # We don't cache the full sized image, so that we don't use multiple gigabytes of memory after a while.
        # TODO: do something if it goes wrong.
        image = QPixmap(str(self.absolute_path()))
        return image

    def load_thumbnail_cached(self, size: int) -> QPixmap:
        thumbnail_key = str(self._uuid) + "_" + str(size)
        # See if the thumbnail is already (or still) in the cache.
        # Returns `None` if it isn't.
        thumbnail = QPixmapCache.find(thumbnail_key)

        if thumbnail:
            # We already have a thumbnail in memory, and it is the right size.
            return thumbnail
        else:
            # Cache files are named: <hash>_<size>.png
            cache_file_path = self._thumbnail_cache_dir.joinpath(thumbnail_key).joinpath(".png")
            if cache_file_path.is_file():
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
                thumbnail.save(str(cache_file_path), "png")

            # Add the newly loaded / generated thumbnail to the cache.
            QPixmapCache.insert(thumbnail_key, thumbnail)

        return thumbnail
