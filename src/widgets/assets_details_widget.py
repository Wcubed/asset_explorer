import PyQt5.QtWidgets as Qwidgets

from data import Asset


class AssetsDetailsWidget(Qwidgets.QWidget):
    """
    Displays the details of one or several assets.
    Displays the large image when a single asset is selected.
    """

    def __init__(self):
        super().__init__()

        self._assets = None

        layout = Qwidgets.QVBoxLayout()
        self.setLayout(layout)

        # TODO: make this a zoomable and scrollable display?
        #       with an "actual size" button.
        self._display = AspectRatioPixmapLabel()
        layout.addWidget(self._display)

        self._title = Qwidgets.QLabel()
        layout.addWidget(self._title)

        layout.addStretch(1)

    def show_assets(self, assets: [Asset]):
        self._assets = assets

        if len(assets) == 0:
            self.clear_display()
        elif len(assets) == 1:
            self._display.setPixmap(self._assets[0].load_image())
            self._title.setText(self._assets[0].get_name())
        else:
            self._display.clear()
            self._title.setText(self.tr("{} assets selected").format(len(assets)))

    def clear_display(self):
        """
        Clears the asset(s) from this widget.
        """
        self._display.clear()
        self._title.setText("")

        self._assets = None


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
