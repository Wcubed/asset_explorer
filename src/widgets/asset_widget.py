import PyQt5.QtCore as Qcore
import PyQt5.QtWidgets as Qwidgets

from data import Asset


class AssetWidget(Qwidgets.QWidget):
    # Width and height in px of the displayed images.
    IMAGE_SIZE = 100

    def __init__(self, asset: Asset):
        super().__init__()

        self._asset = asset

        layout = Qwidgets.QVBoxLayout()
        self.setLayout(layout)

        self._display = Qwidgets.QLabel()
        self._display.setFixedSize(Qcore.QSize(self.IMAGE_SIZE, self.IMAGE_SIZE))
        layout.addWidget(self._display)

        self._name = Qwidgets.QLabel(self._asset.get_name())
        layout.addWidget(self._name)

    def load_and_show_image(self):
        """
        By default the widget will not load the image.
        Call this when the asset widget becomes visible.
        """
        self._display.setPixmap(self._asset.load_thumbnail_cached(self.IMAGE_SIZE))
