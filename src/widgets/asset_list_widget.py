import PyQt5.QtCore as Qcore
import PyQt5.QtWidgets as Qwidgets

from data import Asset


class AssetListWidget(Qwidgets.QWidget):
    IMAGE_COL = 0
    NAME_COL = 1

    # Width and height in px of the displayed images.
    IMAGE_SIZE = 100

    def __init__(self):
        super().__init__()

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

        # Make the rows IMAGE_SIZE pixels high.
        self.view.verticalHeader().hide()
        # Height needs to be larger than the image size,
        # because we add a padding of X pixels total (top + bottom) to the items.
        self.view.verticalHeader().setDefaultSectionSize(self.IMAGE_SIZE + 3)

        # Disable editing.
        self.view.setEditTriggers(self.view.NoEditTriggers)

        # Allow multiselect with shift and ctrl. Select full rows.
        self.view.setSelectionMode(self.view.ExtendedSelection)
        self.view.setSelectionBehavior(self.view.SelectRows)

        # Style the table.
        self.view.setShowGrid(False)
        self.view.setStyleSheet("QTableWidget::item { border: 0px; padding-top: 3px; }")

    def show_assets(self, assets: [Asset]):
        # Remove previous displayed assets.
        # TODO: this can probably be done more efficient.
        #       For example by checking if certain assets are already there.
        self.view.setRowCount(0)

        for asset in assets:
            self.view.insertRow(0)
            self.view.setItem(0, self.NAME_COL, Qwidgets.QTableWidgetItem(asset.get_name()))

            # TODO: image loading and thumbnail generation should be done asynchronously.
            item = Qwidgets.QTableWidgetItem()
            item.setData(Qcore.Qt.DecorationRole, asset.load_thumbnail_cached(self.IMAGE_SIZE))
            self.view.setItem(0, self.IMAGE_COL, item)
