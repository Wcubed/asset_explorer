import PyQt5.QtCore as core
import PyQt5.QtWidgets as widgets


class AssetPacks(widgets.QWidget):
    NAME_COL = 0
    PATH_COL = 1

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
        self.view.insertColumn(self.PATH_COL)
        self.view.setHorizontalHeaderItem(self.PATH_COL, widgets.QTableWidgetItem(self.tr("Path")))
        self.view.horizontalHeader().setSectionResizeMode(1, widgets.QHeaderView.Stretch)

    @core.pyqtSlot(str, core.QDir)
    def add_pack(self, name: str, path: core.QDir):
        self.view.insertRow(0)
        self.view.setItem(0, self.NAME_COL, widgets.QTableWidgetItem(name))
        self.view.setItem(0, self.PATH_COL, widgets.QTableWidgetItem(path.absolutePath()))
