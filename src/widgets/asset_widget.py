import PyQt5.QtWidgets as Qwidgets


class AssetWidget(Qwidgets.QWidget):
    def __init__(self):
        super().__init__()

        layout = Qwidgets.QVBoxLayout()
        self.setLayout(layout)

        self.name = Qwidgets.QLabel("Text!")
        layout.addWidget(self.name)
