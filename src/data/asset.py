from PyQt5.QtCore import QFileInfo, Qt
from PyQt5.QtGui import QPixmap


class Asset:
    def __init__(self, path: str):
        self.file_info = QFileInfo(path)

        # Pixel map gets loaded and cached on request.
        self.image = None
        # Thumbnail get's generated on request.
        self.thumbnail = None
        # Size of the square the current thumbnail fits into.
        self.thumbnail_size = 0

    def get_name(self) -> str:
        return self.file_info.fileName()

    def load_image_cached(self) -> QPixmap:
        if self.image:
            return self.image
        else:
            # Load the image.
            # TODO: do something if it goes wrong.
            self.image = QPixmap(self.file_info.absoluteFilePath())
            return self.image

    def load_thumbnail_cached(self, size: int) -> QPixmap:
        # TODO: do we want to save thumbnails to disc? Say, to: QStandardPaths::CacheLocation/thumbnails.
        #   We could hash the asset path and use that as the filename.

        # TODO: also, make the thumbnail fit in the width.
        #       so the thumbnail fits in a square.
        #       to that end, don't pass "height" but "size"
        if self.thumbnail and size == self.thumbnail_size:
            # We already have a thumbnail, and it is the right size.
            return self.thumbnail

        image = self.load_image_cached()
        # Scale with preserved aspect ratio, so the image fits in a square with sides of "size".
        # Uses bilinear filtering.
        if image.width() < image.height():
            self.thumbnail = image.scaledToHeight(size, Qt.SmoothTransformation)
        else:
            self.thumbnail = image.scaledToWidth(size, Qt.SmoothTransformation)

        self.thumbnail_size = size

        return self.thumbnail
