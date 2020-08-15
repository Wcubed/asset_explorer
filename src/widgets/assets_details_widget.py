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

        # Default invisible.
        self.setVisible(False)

        layout = Qwidgets.QVBoxLayout()
        self.setLayout(layout)

        # TODO: make this a zoomable and scrollable display?
        #       with an "actual size" button.
        self._display = AspectRatioPixmapLabel()
        layout.addWidget(self._display)

        self._title = Qwidgets.QLabel()
        layout.addWidget(self._title)

        self._tag_list = Qwidgets.QListWidget()
        layout.addWidget(self._tag_list)

        add_tag_row = Qwidgets.QHBoxLayout()
        layout.addLayout(add_tag_row)

        add_tag_row.addWidget(Qwidgets.QLabel(self.tr("Add tag")))

        self._add_tag_box = Qwidgets.QComboBox()
        self._add_tag_box.setEditable(True)
        add_tag_row.addWidget(self._add_tag_box)
        add_tag_row.setStretch(1, 1)

        layout.addStretch(1)

    def show_assets(self, assets: [Asset]):
        self._assets = assets

        self.setVisible(True)

        if len(assets) == 0:
            # No assets to display.
            self.clear_display()
        elif len(assets) == 1:
            # Display a single asset.
            self._display.setPixmap(self._assets[0].load_image())
            self._display.setVisible(True)
            self._title.setText(self._assets[0].name())

            if len(self._assets[0].tags()) > 0:
                self._tag_list.setVisible(True)
            else:
                self._tag_list.setVisible(False)
        else:
            # Display multiple assets.
            self._display.clear()
            self._display.setVisible(False)
            self._title.setText(self.tr("{} assets selected").format(len(assets)))

    def clear_display(self):
        """
        Clears the asset(s) from this widget.
        """
        self.setVisible(False)

        self._display.clear()
        self._title.setText("")

        self._display.setVisible(False)
        self._tag_list.setVisible(False)

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
