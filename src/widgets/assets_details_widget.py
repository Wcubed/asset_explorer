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
        self._display = AspectRatioPixmapWidget()
        layout.addWidget(self._display)

        self._title = Qwidgets.QLabel()
        layout.addWidget(self._title)

        self._copy_button_row = Qwidgets.QWidget()
        _copy_button_layout = Qwidgets.QHBoxLayout()
        _copy_button_layout.setContentsMargins(0, 0, 0, 0)
        self._copy_button_row.setLayout(_copy_button_layout)
        layout.addWidget(self._copy_button_row)

        _copy_image_path_button = Qwidgets.QPushButton(self.tr("Copy image path"))
        _copy_button_layout.addWidget(_copy_image_path_button)

        _copy_folder_path_button = Qwidgets.QPushButton(self.tr("Copy folder path"))
        _copy_button_layout.addWidget(_copy_folder_path_button)

        self._tag_display = TagDisplay()
        layout.addWidget(self._tag_display)

        layout.addStretch(1)

        _copy_image_path_button.pressed.connect(self.on_copy_image_path_pressed)
        _copy_folder_path_button.pressed.connect(self.on_copy_folder_path_pressed)

    def show_assets(self, assets: [Asset]):
        self._assets = assets

        self._tag_display.show_tags_of_assets(assets)

        self.setVisible(True)

        if len(assets) == 0:
            # No assets to display.
            self.clear_display()
        elif len(assets) == 1:
            # Display a single asset.
            self._display.set_pixmap(self._assets[0].load_image())
            self._display.setVisible(True)
            self._copy_button_row.setVisible(True)
            self._title.setText(self._assets[0].name())
        else:
            # Display multiple assets.
            self._display.clear()
            self._display.setVisible(False)
            self._copy_button_row.setVisible(False)
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

    def tag_display(self):
        return self._tag_display

    @Qcore.pyqtSlot()
    def on_copy_image_path_pressed(self):
        # Only available when there is one asset selected.
        if len(self._assets) == 1:
            clipboard = Qwidgets.QApplication.clipboard()
            # We copy the absolute path.
            clipboard.setText(str(self._assets[0].absolute_path()))

    @Qcore.pyqtSlot()
    def on_copy_folder_path_pressed(self):
        # Only available when there is one asset selected.
        if len(self._assets) == 1:
            clipboard = Qwidgets.QApplication.clipboard()
            # We copy the absolute folder path.
            clipboard.setText(str(self._assets[0].absolute_path().parent))


class AspectRatioPixmapWidget(Qwidgets.QWidget):
    """
    A QPixmap display that will keep the image's aspect ratio when resizing.
    When it has no image, it will be 0 pixels high.
    """

    def __init__(self):
        super().__init__()

        layout = Qwidgets.QHBoxLayout()
        self.setLayout(layout)
        # The stretch on both sides of the image makes sure it is centered with the right width.
        # TODO: actually make this work! For small images it works, but for larger ones they still stretch.
        layout.addStretch(1)
        layout.addSpacing(10)

        self._label = AspectRatioPixmapLabel()
        layout.addWidget(self._label)
        layout.setStretch(1, 0)

        layout.addStretch(1)

    def set_pixmap(self, pixmap):
        self._label.setPixmap(pixmap)

    def clear(self):
        self._label.clear()


class AspectRatioPixmapLabel(Qwidgets.QLabel):
    """
    Use AspectRatioPixmapWidget instead of this one directly.
    If you use this label directly, it will stretch in the width when
    it's actual image is higher than it can fit given the width.

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
    new_tag = Qcore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self._assets = []
        self._known_tags = set()
        # The tags currently in the tag list.
        self._displayed_tags = set()

        # ---- Layout ----

        layout = Qwidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self._tag_list = Qwidgets.QListWidget()
        # Allow multiple selections, with shift and ctrl.
        self._tag_list.setSelectionMode(self._tag_list.ExtendedSelection)
        self._tag_list.setSpacing(5)
        layout.addWidget(self._tag_list)

        add_tag_row = Qwidgets.QHBoxLayout()
        layout.addLayout(add_tag_row)

        add_tag_row.addWidget(Qwidgets.QLabel(self.tr("Add tag")))

        self._add_tag_box = Qwidgets.QComboBox()
        self._add_tag_box.setEditable(True)
        # Don't auto-insert when pressing "return".
        self._add_tag_box.setInsertPolicy(Qwidgets.QComboBox.NoInsert)
        add_tag_row.addWidget(self._add_tag_box)
        add_tag_row.setStretch(1, 1)

        self._remove_tag_button = Qwidgets.QPushButton(self.tr("Remove selected tags"))
        self._remove_tag_button.setEnabled(False)
        layout.addWidget(self._remove_tag_button)

        # ---- Connections ----

        # Act when a user either selects or enters a tag.
        self._add_tag_box.activated.connect(self.on_add_tag_input)
        self._add_tag_box.lineEdit().returnPressed.connect(self.on_add_tag_input)

        # Change the button state when the selection changes.
        self._tag_list.itemSelectionChanged.connect(self.on_selection_changed)

        # Remove tags when the button is pressed.
        self._remove_tag_button.clicked.connect(self.on_remove_tag_button_pressed)

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
        self._tag_list.clear()

        self._assets = assets

        # TODO: see which tags are shared by all,
        #       and display those differently.
        tags = set()
        for asset in self._assets:
            tags.update(asset.tags())

        # Put the tags in the tag display.
        for tag in tags:
            self._tag_list.addItem(Qwidgets.QListWidgetItem(tag))
        self._displayed_tags = tags

    @Qcore.pyqtSlot()
    def on_add_tag_input(self):
        # TODO: add autocomplete.
        # Get the tag, and clear the box.
        # Tags are always lowercase.
        tag = self._add_tag_box.currentText().lower()
        self._add_tag_box.setCurrentText("")

        # Is it a new tag?
        if tag not in self._known_tags:
            self._known_tags.add(tag)
            self._add_tag_box.addItem(tag)

        # Update the assets with the new tag.
        for asset in self._assets:
            asset.add_tag(tag)

        # Update the display with the new tag.
        if tag not in self._displayed_tags:
            self._tag_list.addItem(Qwidgets.QListWidgetItem(tag))
            # Let others know that this tag is new.
            self.new_tag.emit(tag)

    @Qcore.pyqtSlot()
    def on_remove_tag_button_pressed(self):
        selected_indexes = self._tag_list.selectedIndexes()

        for index in selected_indexes:
            tag = self._tag_list.itemFromIndex(index).text()
            # Remove the tags from the assets.
            for asset in self._assets:
                asset.remove_tag(tag)

            # Remove the tag from the list display.
            self._tag_list.takeItem(index.row())

    @Qcore.pyqtSlot()
    def on_selection_changed(self):
        # Remove button is only enabled when there are actually items selected.
        enabled = len(self._tag_list.selectedIndexes()) > 0
        self._remove_tag_button.setEnabled(enabled)
