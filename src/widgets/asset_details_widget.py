import PyQt5.QtWidgets as Qwidgets

from data import Asset


class AssetDetailsWidget(Qwidgets.QWidget):
    def __init__(self):
        super().__init__()

        self._asset = None

        layout = Qwidgets.QVBoxLayout()
        self.setLayout(layout)

        # TODO: make this a zoomable and scrollable display?
        #       with an "actual size" button.
        self._display = AspectRatioPixmapLabel()
        layout.addWidget(self._display)

        self._name = Qwidgets.QLabel(text="test")
        layout.addWidget(self._name)

        layout.addStretch(1)

    def show_asset(self, asset: Asset):
        """
        By default the widget will not load the image.
        Call this when the asset widget becomes visible.
        """
        self._asset = asset

        self._display.setPixmap(self._asset.load_image())
        self._name.setText(self._asset.get_name())

    def remove_asset(self):
        """
        Clears the asset from this widget.
        """
        if self._asset:
            self._display.clear()
            self._asset = None


class AspectRatioPixmapLabel(Qwidgets.QLabel):
    """
    A QLabel displaying a QPixmap.
    Except that it will keep the aspect ratio of the image intact on resizing.
    It can also be resized smaller than the images original resolution.
    When it has no image, it will be 0 pixels high.
    """

    def __init__(self):
        super().__init__()

        self.setScaledContents(True)
        self.setSizePolicy(Qwidgets.QSizePolicy.Expanding, Qwidgets.QSizePolicy.Expanding)
        self.setMinimumSize(10, 10)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        pixmap = self.pixmap()

        if pixmap:
            return int(pixmap.height() * (width / pixmap.width()))
        else:
            return 0
