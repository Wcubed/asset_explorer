from PyQt5.QtCore import QFileInfo, Qt
from PyQt5.QtGui import QPixmap


class Asset:
    def __init__(self, path: str):
        self._file_info = QFileInfo(path)

        # Thumbnail gets generated on request and cached here.
        self._thumbnail = None
        # Size of the square the current thumbnail fits into.
        self._thumbnail_size = 0

        self._hash = hash(self.get_absolute_path())

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
        # TODO: do we want to save thumbnails to disc? Say, to: QStandardPaths::CacheLocation/thumbnails.
        #   We could hash the asset path and use that as the filename.

        # TODO: also, make the thumbnail fit in the width.
        #       so the thumbnail fits in a square.
        #       to that end, don't pass "height" but "size"
        if self._thumbnail and size == self._thumbnail_size:
            # We already have a thumbnail, and it is the right size.
            return self._thumbnail

        image = self.load_image()
        # Scale with preserved aspect ratio, so the image fits in a square with sides of "size".
        # Uses bilinear filtering.
        if image.width() < image.height():
            self._thumbnail = image.scaledToHeight(size, Qt.SmoothTransformation)
        else:
            self._thumbnail = image.scaledToWidth(size, Qt.SmoothTransformation)

        self._thumbnail_size = size

        return self._thumbnail
