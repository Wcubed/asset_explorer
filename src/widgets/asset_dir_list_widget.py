import pathlib

import PyQt5.QtCore as Qcore
import PyQt5.QtWidgets as Qwidgets

from data import AssetDir


class AssetDirListWidget(Qwidgets.QWidget):
    NAME_COL = 0
    COUNT_COL = 1
    PATH_COL = 2

    NAME_COL_WIDTH = 200
    COUNT_COL_WIDTH = 50

    selection_changed = Qcore.pyqtSignal()

    def __init__(self, asset_dirs: {}):
        super().__init__()

        # pathlib.Path -> AssetDir
        self.asset_dirs = asset_dirs

        layout = Qwidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Show name, count, and some extra to hint that the full path is also there.
        self.setMinimumWidth(self.NAME_COL_WIDTH + self.COUNT_COL_WIDTH + 30)

        self.view = Qwidgets.QTableWidget()
        layout.addWidget(self.view)

        # Setup the headers.
        self.view.insertColumn(self.NAME_COL)
        self.view.setHorizontalHeaderItem(self.NAME_COL, Qwidgets.QTableWidgetItem(self.tr("Name")))
        self.view.setColumnWidth(self.NAME_COL, self.NAME_COL_WIDTH)

        self.view.insertColumn(self.COUNT_COL)
        self.view.setHorizontalHeaderItem(self.COUNT_COL, Qwidgets.QTableWidgetItem(self.tr("Assets")))
        self.view.setColumnWidth(self.COUNT_COL, self.COUNT_COL_WIDTH)

        self.view.insertColumn(self.PATH_COL)
        self.view.setHorizontalHeaderItem(self.PATH_COL, Qwidgets.QTableWidgetItem(self.tr("Path")))
        self.view.horizontalHeader().setSectionResizeMode(self.PATH_COL, Qwidgets.QHeaderView.Stretch)

        self.view.verticalHeader().hide()

        # Disable editing.
        self.view.setEditTriggers(self.view.NoEditTriggers)

        # Allow multiselect with shift and ctrl. Select full rows.
        self.view.setSelectionMode(self.view.ExtendedSelection)
        self.view.setSelectionBehavior(self.view.SelectRows)

        self.remove_button = Qwidgets.QPushButton(text=self.tr("Remove selected packs"))
        self.remove_button.setEnabled(False)
        layout.addWidget(self.remove_button)

        # ---- Connections ----
        # Update the view when new packs are added.
        self.view.itemSelectionChanged.connect(self.on_selection_changed)
        self.remove_button.clicked.connect(self.on_remove_button_pressed)

    def on_new_asset_dir(self, path: pathlib.Path):
        asset_dir = self.asset_dirs[path]

        self.view.insertRow(0)
        self.view.setItem(0, self.NAME_COL, Qwidgets.QTableWidgetItem(asset_dir.name()))

        self.view.setItem(0, self.COUNT_COL, Qwidgets.QTableWidgetItem(str(asset_dir.asset_count_recursive())))

        # TODO: right align this, and then cut the path off with "..." on the left?
        path_item = Qwidgets.QTableWidgetItem(str(asset_dir.absolute_path()))
        self.view.setItem(0, self.PATH_COL, path_item)

        # Sort the table based on the names.
        self.view.sortItems(self.NAME_COL, Qcore.Qt.AscendingOrder)

    @Qcore.pyqtSlot()
    def on_remove_button_pressed(self):
        remove_rows = []
        remove_dirs = []

        for item in self.view.selectedItems():
            if item.column() == self.NAME_COL:
                path = self.view.item(item.row(), self.PATH_COL).text()

                remove_dirs.append(pathlib.Path(path))
                remove_rows.append(item.row())

        # Clear the selection, so that removing rows does not trigger updates of `on_selection_changed`.
        self.view.clearSelection()

        # Remove the rows after iterating over the selection, so we don't delete while iterating.
        # Remove them from bottom to top, otherwise the indexes are no longer valid because the rest of the rows
        # will move up.
        remove_rows.sort(reverse=True)
        for row in remove_rows:
            self.view.removeRow(row)

        for remove_dir in remove_dirs:
            del self.asset_dirs[remove_dir]

    @Qcore.pyqtSlot()
    def on_selection_changed(self):
        if len(self.get_selected_dirs()) == 0:
            self.remove_button.setEnabled(False)
        else:
            self.remove_button.setEnabled(True)

        self.selection_changed.emit()

    def get_selected_dirs(self) -> [AssetDir]:
        selection = []

        # Get the paths of the selections.
        for item in self.view.selectedItems():
            if item.column() == self.PATH_COL:
                path = pathlib.Path(item.text())
                selection.append(self.asset_dirs[path])

        return selection
