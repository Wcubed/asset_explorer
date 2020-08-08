import PyQt5.QtWidgets as widgets


class AssetDirs(widgets.QWidget):
    def __init__(self):
        super().__init__()

        layout = widgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        layout.addWidget(widgets.QLabel(text=self.tr("Asset directories")))

        self.view = widgets.QTreeView()
        layout.addWidget(self.view)
