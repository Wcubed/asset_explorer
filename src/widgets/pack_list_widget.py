import PyQt5.QtCore as Qcore
import PyQt5.QtWidgets as Qwidgets


class PackListWidget(Qwidgets.QWidget):
    NAME_COL = 0
    COUNT_COL = 1
    PATH_COL = 2

    selection_changed = Qcore.pyqtSignal()

    def __init__(self):
        super().__init__()

        layout = Qwidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # layout.addWidget(widgets.QLabel(text=self.tr("Asset packs")))

        self.view = Qwidgets.QTableWidget()
        layout.addWidget(self.view)

        # Setup the headers.
        self.view.insertColumn(self.NAME_COL)
        self.view.setHorizontalHeaderItem(self.NAME_COL, Qwidgets.QTableWidgetItem(self.tr("Name")))

        self.view.insertColumn(self.COUNT_COL)
        self.view.setHorizontalHeaderItem(self.COUNT_COL, Qwidgets.QTableWidgetItem(self.tr("Assets")))
        self.view.setColumnWidth(self.COUNT_COL, 50)

        self.view.insertColumn(self.PATH_COL)
        self.view.setHorizontalHeaderItem(self.PATH_COL, Qwidgets.QTableWidgetItem(self.tr("Path")))
        self.view.horizontalHeader().setSectionResizeMode(self.PATH_COL, Qwidgets.QHeaderView.Stretch)

        self.view.verticalHeader().hide()

        # Disable editing.
        self.view.setEditTriggers(self.view.NoEditTriggers)

        # Allow multiselect with shift and ctrl. Select full rows.
        self.view.setSelectionMode(self.view.ExtendedSelection)
        self.view.setSelectionBehavior(self.view.SelectRows)

        self.view.itemSelectionChanged.connect(self.on_selection_changed)

    @Qcore.pyqtSlot(str, int, Qcore.QDir)
    def add_pack(self, name: str, asset_count: int, path: Qcore.QDir):
        self.view.insertRow(0)
        self.view.setItem(0, self.NAME_COL, Qwidgets.QTableWidgetItem(name))

        self.view.setItem(0, self.COUNT_COL, Qwidgets.QTableWidgetItem(str(asset_count)))

        # TODO: right align this, and then cut the path off with "..." on the left?
        path_item = Qwidgets.QTableWidgetItem(path.absolutePath())
        self.view.setItem(0, self.PATH_COL, path_item)

    @Qcore.pyqtSlot()
    def on_selection_changed(self):
        self.selection_changed.emit()

    def get_selected_packs(self) -> [Qcore.QDir]:
        selection = []

        # Get the directories of the selections.
        for item in self.view.selectedItems():
            if item.column() == self.PATH_COL:
                selection.append(Qcore.QDir(item.text()))

        return selection
