import PyQt5.QtCore as Qcore
import PyQt5.QtWidgets as Qwidgets

from .asset_widget import AssetWidget


class AssetFlowGridWidget(Qwidgets.QScrollArea):
    def __init__(self):
        super().__init__()

        # hash -> Asset, dictionary of the assets to be displayed.
        self._assets = {}

        main_widget = Qwidgets.QWidget()
        # TODO: fill in actual asset widget values.
        self._layout = FlowGridLayout(200, 200)

        self.setWidget(main_widget)

    def show_assets(self, assets: dict):
        self._assets = assets

        for asset in self._assets.values():
            self._layout.addWidget(AssetWidget(asset))


class FlowGridLayout(Qwidgets.QLayout):
    """
    Lays out widgets in a grid. Each widget is of equal size.
    When the layout is given more horizontal space, widgets flow up to fill the new area.
    """

    def __init__(self, item_width: int, item_height: int):
        super().__init__()

        self._item_width = item_width
        self._item_height = item_height

        # List of QLayoutItems
        self._items = []

        # TODO: The notes from here: https://doc.qt.io/qt-5/layout.html#further-notes

    def __del__(self):
        # According to https://doc.qt.io/qt-5/layout.html
        # the QLayoutItems will not nicely disappear on their own.
        # At least not in C++. I am not sure if this is also the case with the python library.
        self._items.clear()

    def addItem(self, new_item: Qwidgets.QLayoutItem) -> None:
        self._items.append(new_item)

    def count(self) -> int:
        return len(self._items)

    def setGeometry(self, rect: Qcore.QRect) -> None:
        # TODO
        pass

    def sizeHint(self) -> Qcore.QSize:
        # TODO
        pass

    def minimumSize(self) -> Qcore.QSize:
        # TODO
        pass

    def itemAt(self, index: int) -> Qwidgets.QLayoutItem:
        return self._items[index]

    def takeAt(self, index: int) -> Qwidgets.QLayoutItem:
        return self._items.pop(index)
