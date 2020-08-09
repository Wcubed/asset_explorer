from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QPixmap


class Asset:
    def __init__(self, path: str):
        self.file_info = QFileInfo(path)

        # Pixel map gets loaded and cached on request.
        self.image = None
        # Thumbnail get's generated on request.
        self.thumbnail = None
        self.thumbnail_height = 0

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

    def load_thumbnail_cached(self, height: int) -> QPixmap:
        if self.thumbnail and height == self.thumbnail_height:
            # We already have a thumbnail, and it is the right size.
            return self.thumbnail

        image = self.load_image_cached()
        # Scale with preserved aspect ratio.
        self.thumbnail = image.scaledToHeight(height)
        self.thumbnail_height = height

        return self.thumbnail
