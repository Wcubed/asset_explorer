import logging

import PyQt5.QtCore as Qcore
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

        self._tag_display = TagDisplay()
        layout.addWidget(self._tag_display)

        layout.addStretch(1)

    def show_assets(self, assets: [Asset]):
        self._assets = assets

        self._tag_display.show_tags_of_assets(assets)

        self.setVisible(True)

        if len(assets) == 0:
            # No assets to display.
            self.clear_display()
        elif len(assets) == 1:
            # Display a single asset.
            self._display.setPixmap(self._assets[0].load_image())
            self._display.setVisible(True)
            self._title.setText(self._assets[0].name())
        else:
            # Display multiple assets.
            self._display.clear()
            self._display.setVisible(False)
            self._title.setText(self.tr("{} assets selected").format(len(assets)))

    def add_known_tags(self, known_tags):
        self._tag_display.add_known_tags(known_tags)

    def clear_display(self):
        """
        Clears the asset(s) from this widget.
        """
        self.setVisible(False)

        self._display.clear()
        self._title.setText("")

        self._display.setVisible(False)

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


class TagDisplay(Qwidgets.QWidget):

    def __init__(self):
        super().__init__()

        self._assets = []
        self._known_tags = set()

        layout = Qwidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        add_tag_row = Qwidgets.QHBoxLayout()
        layout.addLayout(add_tag_row)

        add_tag_row.addWidget(Qwidgets.QLabel(self.tr("Add tag")))

        self._add_tag_box = Qwidgets.QComboBox()
        self._add_tag_box.setEditable(True)
        # Don't auto-insert when pressing "return".
        self._add_tag_box.setInsertPolicy(Qwidgets.QComboBox.NoInsert)
        add_tag_row.addWidget(self._add_tag_box)
        add_tag_row.setStretch(1, 1)

        for tag in self._known_tags:
            self._add_tag_box.addItem(tag)

        # ---- Connections ----

        # Act when a user either selects or enters a tag.
        self._add_tag_box.activated.connect(self.on_tag_selected)
        self._add_tag_box.lineEdit().returnPressed.connect(self.on_tag_selected)

    def add_known_tags(self, known_tags):
        # Append currently unknown tags to the selection box.
        for tag in known_tags:
            if tag not in self._known_tags:
                self._add_tag_box.addItem(tag)

        self._known_tags.update(known_tags)
        # When a tag is added, it is sometimes immediately selected in the box.
        # This makes sure it stays empty unless the user says otherwise.
        self._add_tag_box.setCurrentText("")

    def show_tags_of_assets(self, assets: [Asset]):
        self._assets = assets

    @Qcore.pyqtSlot()
    def on_tag_selected(self):
        # TODO: add autocomplete.
        # Get the tag, and clear the box.
        tag = self._add_tag_box.currentText()
        self._add_tag_box.setCurrentText("")

        # Is it a new tag?
        if tag not in self._known_tags:
            self._known_tags.add(tag)
            self._add_tag_box.addItem(tag)

        # Update the assets with the new tag.
        for asset in self._assets:
            asset.add_tag(tag)

        logging.debug("New tag: {}".format(tag))
