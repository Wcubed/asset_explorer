import PyQt5.QtWidgets as Qwidgets
from PyQt5.QtCore import Qt

from . import asset_widget


class AssetListWidget(Qwidgets.QWidget):
    def __init__(self):
        super().__init__()

        layout = Qwidgets.QVBoxLayout()
        self.setLayout(layout)

        # TODO: Make this a responsive grid layout?
        self.asset_scroller = Qwidgets.QScrollArea()
        # todo: Make the scroll area always as wide as the content.
        self.asset_scroller.horizontalScrollBar().setEnabled(False)
        self.asset_scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.asset_scroller)

        self.asset_view = Qwidgets.QWidget()
        self.asset_layout = Qwidgets.QVBoxLayout()
        self.asset_view.setLayout(self.asset_layout)

        for _ in range(0, 100):
            self.asset_layout.addWidget(asset_widget.AssetWidget())

        self.asset_scroller.setWidget(self.asset_view)
        self.asset_view.show()
