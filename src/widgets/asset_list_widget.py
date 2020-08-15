import uuid

import PyQt5.QtCore as Qcore
import PyQt5.QtGui as Qgui
import PyQt5.QtWidgets as Qwidgets

from data import Asset


class AssetListWidget(Qwidgets.QWidget):
    IMAGE_COL = 0
    NAME_COL = 1
    UUID_COL = 2

    # Width and height in px of the displayed images.
    IMAGE_SIZE = 100

    selection_changed = Qcore.pyqtSignal()

    def __init__(self):
        super().__init__()

        # uuid -> Asset, ordered dictionary of the assets to be displayed.
        self.assets = {}

        # ---- layout ----

        layout = Qwidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.view = Qwidgets.QTableWidget()
        layout.addWidget(self.view)

        self.view.insertColumn(self.IMAGE_COL)
        self.view.setHorizontalHeaderItem(self.IMAGE_COL, Qwidgets.QTableWidgetItem(""))
        # The image column needs to be a bit wider than the image size,
        # because for some reason qt finds it a good idea to have a small padding on the left of the column.
        self.view.setColumnWidth(self.IMAGE_COL, self.IMAGE_SIZE + 10)

        self.view.insertColumn(self.NAME_COL)
        self.view.setHorizontalHeaderItem(self.NAME_COL, Qwidgets.QTableWidgetItem("Name"))
        self.view.horizontalHeader().setSectionResizeMode(self.NAME_COL, Qwidgets.QHeaderView.Stretch)

        # The asset uuid column is only for internal use.
        self.view.insertColumn(self.UUID_COL)
        self.view.setColumnHidden(self.UUID_COL, True)

        # Make the rows IMAGE_SIZE pixels high.
        self.view.verticalHeader().hide()
        # Height needs to be larger than the image size,
        # because we add a padding of X pixels total (top + bottom) to the items.
        self.view.verticalHeader().setDefaultSectionSize(self.IMAGE_SIZE + 3)

        # Disable editing.
        self.view.setEditTriggers(self.view.NoEditTriggers)

        # Select full rows.
        self.view.setSelectionBehavior(self.view.SelectRows)

        # Allow multiple selection via shift and ctrl.
        self.view.setSelectionMode(self.view.ExtendedSelection)

        # Style the table.
        self.view.setShowGrid(False)
        self.view.setStyleSheet("QTableWidget::item { border: 0px; padding-top: 3px; }")

        # ---- Connections ----

        # When visible items change, we want to load their thumbnails.
        self.view.verticalScrollBar().valueChanged.connect(self.on_scrollbar_value_changed)
        self.view.itemSelectionChanged.connect(self.on_selection_changed)

    def show_assets(self, assets: dict):
        # Remove previous displayed assets.
        # TODO: this can probably be done more efficient.
        #       For example by checking if certain assets are already there.
        self.view.setRowCount(0)
        # Always scroll to the top when displaying a new list of assets.
        self.view.scrollToTop()

        self.assets = assets

        for asset in assets.values():
            # Insert at the bottom, to keep the ordering of the assets intact.
            new_row_id = self.view.rowCount()
            self.view.insertRow(new_row_id)
            self.view.setItem(new_row_id, self.NAME_COL, Qwidgets.QTableWidgetItem(asset.name()))
            self.view.setItem(new_row_id, self.UUID_COL, Qwidgets.QTableWidgetItem(str(asset.uuid())))
            # The thumbnails will be loaded when the item is visible.

        self.load_visible_asset_thumbnails()

    def get_selected_assets(self) -> [Asset]:
        assets = []
        for index in self.view.selectedIndexes():
            if index.column() == self.IMAGE_COL:
                asset_uuid = uuid.UUID(self.view.item(index.row(), self.UUID_COL).text())
                assets.append(self.assets[asset_uuid])

        return assets

    def resizeEvent(self, event: Qgui.QResizeEvent) -> None:
        # Make sure any newly visible items have their image thumbnail loaded.
        self.load_visible_asset_thumbnails()

    @Qcore.pyqtSlot()
    def on_scrollbar_value_changed(self):
        self.load_visible_asset_thumbnails()

    @Qcore.pyqtSlot()
    def on_selection_changed(self):
        self.selection_changed.emit()

    def load_visible_asset_thumbnails(self):
        """
        Loads and applies only the thumbnails from the visible items.
        """
        if self.view.rowCount() == 0:
            # The rest of the function stumbles when the table is empty.
            # (due to bottom_visible_plus_one)
            return

        top_visible_row = self.view.indexAt(self.view.rect().topLeft()).row()
        bottom_visible_row = self.view.indexAt(self.view.rect().bottomLeft()).row()

        # Check if we have hit the bottom
        # Needed because qt shows "bottom visible row" as -1 when we are all the way at the end.
        # And because it will somehow show as "0" when the items fit into the table without scrolling.
        if bottom_visible_row == -1 or bottom_visible_row == 0:
            bottom_visible_row = self.view.rowCount() - 1

        # Up to and including the bottom visible row.
        bottom_visible_plus_one = bottom_visible_row + 1

        for row in range(top_visible_row, bottom_visible_plus_one):
            # Load the thumbnail.
            asset_uuid = self.view.item(row, self.UUID_COL).text()
            asset = self.assets[uuid.UUID(asset_uuid)]

            # TODO: image loading and thumbnail generation should be done asynchronously.
            item = Qwidgets.QTableWidgetItem()
            item.setData(Qcore.Qt.DecorationRole, asset.load_thumbnail_cached(self.IMAGE_SIZE))
            self.view.setItem(row, self.IMAGE_COL, item)
