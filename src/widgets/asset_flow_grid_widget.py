import PyQt5.QtWidgets as Qwidgets

from .asset_widget import AssetWidget


class AssetFlowGridWidget(Qwidgets.QScrollArea):
    def __init__(self):
        super().__init__()

        # hash -> Asset, dictionary of the assets to be displayed.
        self.assets = {}

        main_widget = Qwidgets.QWidget()
        self.layout = FlowGridLayout()

        self.setWidget(main_widget)

    def show_assets(self, assets: dict):
        self.assets = assets

        for asset in self.assets.values():
            self.layout.addWidget(AssetWidget(asset))


class FlowGridLayout(Qwidgets.QLayout):
    def __init__(self):
        super().__init__()
