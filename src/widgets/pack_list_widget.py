import PyQt5.QtCore as core
import PyQt5.QtWidgets as widgets


class PackListWidget(widgets.QWidget):
    NAME_COL = 0
    COUNT_COL = 1
    PATH_COL = 2

    def __init__(self):
        super().__init__()

        layout = widgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        layout.addWidget(widgets.QLabel(text=self.tr("Asset packs")))

        self.view = widgets.QTableWidget()
        layout.addWidget(self.view)

        # Setup the headers.
        self.view.insertColumn(self.NAME_COL)
        self.view.setHorizontalHeaderItem(self.NAME_COL, widgets.QTableWidgetItem(self.tr("Name")))

        self.view.insertColumn(self.COUNT_COL)
        self.view.setHorizontalHeaderItem(self.COUNT_COL, widgets.QTableWidgetItem(self.tr("Assets")))
        self.view.setColumnWidth(self.COUNT_COL, 50)

        self.view.insertColumn(self.PATH_COL)
        self.view.setHorizontalHeaderItem(self.PATH_COL, widgets.QTableWidgetItem(self.tr("Path")))
        self.view.horizontalHeader().setSectionResizeMode(self.PATH_COL, widgets.QHeaderView.Stretch)

        self.view.verticalHeader().hide()

        # Disable editing.
        self.view.setEditTriggers(self.view.NoEditTriggers)

        # Allow multiselect with shift and ctrl. Select full rows.
        self.view.setSelectionMode(self.view.ExtendedSelection)
        self.view.setSelectionBehavior(self.view.SelectRows)

    @core.pyqtSlot(str, int, core.QDir)
    def add_pack(self, name: str, asset_count: int, path: core.QDir):
        self.view.insertRow(0)
        self.view.setItem(0, self.NAME_COL, widgets.QTableWidgetItem(name))

        self.view.setItem(0, self.COUNT_COL, widgets.QTableWidgetItem(str(asset_count)))

        # TODO: right align this, and then "..." on the left?
        path_item = widgets.QTableWidgetItem(path.absolutePath())
        self.view.setItem(0, self.PATH_COL, path_item)
