import math
import typing

import PyQt5.QtCore as Qcore
import PyQt5.QtGui as Qgui
import PyQt5.QtWidgets as Qwidgets

from .asset_widget import AssetWidget


class AssetFlowGridWidget(Qwidgets.QFrame):
    def __init__(self, item_width: int, item_height: int):
        super().__init__()

        # hash -> Asset, dictionary of the assets to be displayed.
        self._assets = {}
        # [y][x] grid of asset widgets.
        self._asset_grid = []
        self._item_width = item_width
        self._item_height = item_height

        self._last_items_in_width = 0

        # ---- Layout ----

        self.setFrameShape(Qwidgets.QFrame.StyledPanel)

        self._layout = Qwidgets.QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)

        self._asset_grid_widget = Qwidgets.QWidget()
        self._asset_layout = Qwidgets.QGridLayout()
        self._asset_grid_widget.setLayout(self._asset_layout)
        self._layout.addWidget(self._asset_grid_widget)
        self._layout.setStretch(0, 1)

        test_label = Qwidgets.QLabel(text="bladiebla")
        self._asset_layout.addWidget(test_label, 0, 0)

        self._scrollbar = Qwidgets.QScrollBar(Qcore.Qt.Vertical)
        self._layout.addWidget(self._scrollbar)
        self._layout.setStretch(1, 0)

        # Our minimum size is 1 asset + horizontal scrollbar
        self.setMinimumWidth(self._item_width + self._scrollbar.minimumWidth())
        self.setMinimumHeight(self._item_height)

        # TODO: Fill with as much asset widgets as needed to fill the size, but no more.
        #   and adjust scrollbar to match how many didn't fit.
        # TODO: when the user scrolls, we don't actually scroll the asset widgets.
        #       we simply set new assets to the existing widgets.

    def show_assets(self, assets: dict):
        self._assets = assets

    def resizeEvent(self, event: Qgui.QResizeEvent) -> None:
        super().resizeEvent(event)

        # Don't overflow horizontally (floor).
        items_in_width = math.floor(event.size().width() / self._item_width)
        # Do overflow vertically down (ceil).
        items_in_height = math.ceil(event.size().height() / self._item_height)

        # We do not remove excess horizontal or vertical widgets.
        # As the fact that we generated them means that we needed them once,
        # and that means we might have to use them again. (That, and it doesn't cost that much to keep them).

        # Add any extra widgets that now fit.
        for y in range(0, items_in_height):
            if y >= len(self._asset_grid):
                self._asset_grid.append([])

            for x in range(0, items_in_width):
                if x >= len(self._asset_grid[y]):
                    new_widget = AssetWidget()
                    self._asset_grid[y].append(new_widget)
                    self._asset_layout.addWidget(new_widget, y, x)

        self._last_items_in_width = items_in_width


class FlowGridLayout(Qwidgets.QLayout):
    """
    Lays out widgets in a grid. Each widget is of equal size.
    When the layout is given more horizontal space, widgets flow up to fill the new area.
    """

    def __init__(self, item_width: int, item_height: int):
        super().__init__()

        self._item_width = item_width
        self._item_height = item_height

        # Our height is dependent on our width.
        self._cache_dirty = True
        self._cached_width = 0
        # How many items fit in the cached width.
        self._cached_items_in_width = 0
        self._cached_height_for_width = 0

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

        self.invalidate()

    def itemAt(self, index: int) -> typing.Optional[Qwidgets.QLayoutItem]:
        if index < 0 or index >= self.count():
            return None
        else:
            return self._items[index]

    def takeAt(self, index: int) -> typing.Optional[Qwidgets.QLayoutItem]:
        self.invalidate()

        if index < 0 or index >= self.count():
            return None
        else:
            return self._items.pop(index)

    def clear(self):
        """Remove all widgets."""
        for item in self._items:
            item.widget().deleteLater()

        self._items.clear()

        self.invalidate()

    def count(self) -> int:
        return len(self._items)

    def invalidate(self) -> None:
        super().invalidate()
        self._cache_dirty = True

    def setGeometry(self, rect: Qcore.QRect) -> None:
        super().setGeometry(rect)

        if len(self._items) == 0 or rect.width() == 0 or rect.height() == 0:
            return

        # TODO: take into account `spacing()`
        # The `heightForWidth` function also updates the necessary caches.
        # So after this call the `self._cached_items_in_width` is up-to-date.
        self.heightForWidth(rect.width())

        for i, item in enumerate(self._items):
            x = rect.x() + ((i % self._cached_items_in_width) * self._item_width)
            y = rect.y() + (math.floor(i / self._cached_items_in_width) * self._item_height)

            item_rect = Qcore.QRect(x, y, self._item_width, self._item_height)
            item.setGeometry(item_rect)

    def hasHeightForWidth(self) -> bool:
        # Our height is dependent on our width.
        return True

    def heightForWidth(self, width: int) -> int:
        if self._cache_dirty or self._cached_width != width:
            # Cache invalid.
            self._cached_width = width

            # How many items can we fit in the given width?
            # We do not scale the items, so we have to round down.
            items_in_width = math.floor(width / self._item_width)

            if items_in_width != self._cached_items_in_width or items_in_width == 0:
                if items_in_width == 0:
                    # We want to display a minimum of 1 item.
                    items_in_width = 1

                # The items to fit in the width have also changed.
                # Therefore the height cache is also invalid.
                self._cached_items_in_width = items_in_width
                self._cached_height_for_width = math.ceil(
                    self.count() / self._cached_items_in_width) * self._item_height

            return self._cached_height_for_width
        else:
            # Cache is still valid.
            return self._cached_height_for_width

    def sizeHint(self) -> Qcore.QSize:
        # TODO: take into account `spacing()`
        if len(self._items) == 0:
            return Qcore.QSize(0, 0)

        if self._cached_items_in_width == 0:
            # Either this is the first time this got called,
            # Or we have been resized below the minimum width.
            # Either way, notify the caller that this is the size we need at the very least.
            return self.minimumSize()

        width = self._cached_items_in_width * self._item_width
        height = self.heightForWidth(width)

        return Qcore.QSize(width, height)

    def minimumSize(self) -> Qcore.QSize:
        # TODO: take into account `spacing()`
        if self._cached_items_in_width == 0:
            # Either this is the first time this got called,
            # Or we got squeezed in a small width area.
            # Either way: minimum width is 1 item wide.
            width = self._item_width
            height = self.heightForWidth(width)
            return Qcore.QSize(width, height)

        # TODO can we assume the cache is ok here?
        # The minimum width is 1 item, but the minimum height is dependent on the width we are given.
        return Qcore.QSize(self._item_width, self._cached_height_for_width)
