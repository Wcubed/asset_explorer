from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QPixmap


class Asset:
    def __init__(self, path: str):
        self.file_info = QFileInfo(path)

        # Pixel map gets loaded and cached on request.
        self.image = None

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
