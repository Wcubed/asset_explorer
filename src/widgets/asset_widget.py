import PyQt5.QtCore as Qcore
import PyQt5.QtWidgets as Qwidgets

from data import Asset


class AssetWidget(Qwidgets.QWidget):
    # Width and height in px of the displayed images.
    IMAGE_SIZE = 100

    def __init__(self):
        super().__init__()

        self._asset = None

        layout = Qwidgets.QVBoxLayout()
        self.setLayout(layout)

        self._display = Qwidgets.QLabel()
        self._display.setFixedSize(Qcore.QSize(self.IMAGE_SIZE, self.IMAGE_SIZE))
        layout.addWidget(self._display)

        self._name = Qwidgets.QLabel(text="test")
        layout.addWidget(self._name)

    def show_asset(self, asset: Asset):
        """
        By default the widget will not load the image.
        Call this when the asset widget becomes visible.
        """
        self._asset = asset

        self._display.setPixmap(self._asset.load_thumbnail_cached(self.IMAGE_SIZE))
        self._name.setText(self._asset.get_name())
