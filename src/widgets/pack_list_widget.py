import PyQt5.QtCore as Qcore
import PyQt5.QtWidgets as Qwidgets

from data import Data, AssetPack


class PackListWidget(Qwidgets.QWidget):
    NAME_COL = 0
    COUNT_COL = 1
    PATH_COL = 2
    HASH_COL = 3

    selection_changed = Qcore.pyqtSignal()

    def __init__(self, data: Data):
        super().__init__()

        # Reference to the asset pack data.
        self.data = data

        layout = Qwidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # layout.addWidget(widgets.QLabel(text=self.tr("Asset packs")))

        self.view = Qwidgets.QTableWidget()
        layout.addWidget(self.view)

        # Setup the headers.
        self.view.insertColumn(self.NAME_COL)
        self.view.setHorizontalHeaderItem(self.NAME_COL, Qwidgets.QTableWidgetItem(self.tr("Name")))
        self.view.setColumnWidth(self.NAME_COL, 150)

        self.view.insertColumn(self.COUNT_COL)
        self.view.setHorizontalHeaderItem(self.COUNT_COL, Qwidgets.QTableWidgetItem(self.tr("Assets")))
        self.view.setColumnWidth(self.COUNT_COL, 50)

        self.view.insertColumn(self.PATH_COL)
        self.view.setHorizontalHeaderItem(self.PATH_COL, Qwidgets.QTableWidgetItem(self.tr("Path")))
        self.view.horizontalHeader().setSectionResizeMode(self.PATH_COL, Qwidgets.QHeaderView.Stretch)

        # Hash column is used internally to identify the packs, therefore not visible.
        self.view.insertColumn(self.HASH_COL)
        self.view.setColumnHidden(self.HASH_COL, True)

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
        self.data.pack_added.connect(self.on_new_pack)
        self.view.itemSelectionChanged.connect(self.on_selection_changed)

    @Qcore.pyqtSlot(int)
    def on_new_pack(self, pack_hash: int):
        pack = self.data.get_pack(pack_hash)

        self.view.insertRow(0)
        self.view.setItem(0, self.NAME_COL, Qwidgets.QTableWidgetItem(pack.get_name()))

        self.view.setItem(0, self.COUNT_COL, Qwidgets.QTableWidgetItem(str(pack.get_asset_count())))

        # TODO: right align this, and then cut the path off with "..." on the left?
        path_item = Qwidgets.QTableWidgetItem(pack.get_path())
        self.view.setItem(0, self.PATH_COL, path_item)

        self.view.setItem(0, self.HASH_COL, Qwidgets.QTableWidgetItem(str(pack.get_hash())))

    @Qcore.pyqtSlot()
    def on_selection_changed(self):
        if len(self.get_selected_packs()) == 0:
            self.remove_button.setEnabled(False)
        else:
            self.remove_button.setEnabled(True)

        self.selection_changed.emit()

    def get_selected_packs(self) -> [AssetPack]:
        selection = []

        # Get the directories of the selections.
        for item in self.view.selectedItems():
            if item.column() == self.NAME_COL:
                # Hash column is hidden, therefore not selectable.
                # So we have to retrieve the data like this.
                pack_hash = self.view.item(item.row(), self.HASH_COL).text()
                selection.append(self.data.get_pack(int(pack_hash)))

        return selection
