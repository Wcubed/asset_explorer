import PyQt5.QtWidgets as Qwidgets


class AssetListWidget(Qwidgets.QWidget):
    IMAGE_COL = 0
    NAME_COL = 1

    def __init__(self):
        super().__init__()

        layout = Qwidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.view = Qwidgets.QTableWidget()
        layout.addWidget(self.view)

        self.view.insertColumn(self.IMAGE_COL)
        self.view.setHorizontalHeaderItem(self.IMAGE_COL, Qwidgets.QTableWidgetItem(""))

        self.view.insertColumn(self.NAME_COL)
        self.view.setHorizontalHeaderItem(self.NAME_COL, Qwidgets.QTableWidgetItem("Name"))
        self.view.horizontalHeader().setSectionResizeMode(self.NAME_COL, Qwidgets.QHeaderView.Stretch)

        self.view.verticalHeader().hide()

        self.view.setEditTriggers(self.view.NoEditTriggers)

        # Disable editing.
        self.view.setEditTriggers(self.view.NoEditTriggers)

        # Allow multiselect with shift and ctrl. Select full rows.
        self.view.setSelectionMode(self.view.ExtendedSelection)
        self.view.setSelectionBehavior(self.view.SelectRows)
