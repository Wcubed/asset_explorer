import logging
import math
import typing

import PyQt5.QtCore as Qcore
import PyQt5.QtGui as Qgui
import PyQt5.QtWidgets as Qwidgets

from .asset_widget import AssetWidget


class AssetFlowGridWidget(Qwidgets.QFrame):
    # Scroll 2 items at a time if we can vertically display
    # more items than this.
    SCROLL_2_PER_TICK_LIMIT = 4

    # Scroll 3 items at a time if we can vertically display
    # more items than this.
    SCROLL_3_PER_TICK_LIMIT = 8

    def __init__(self):
        super().__init__()

        # hash -> Asset, dictionary of the assets to be displayed.
        self._assets = {}
        # [y][x] grid of asset widgets.
        self._asset_grid = []
        self._item_width = AssetWidget.WIDTH
        self._item_height = AssetWidget.HEIGHT

        # How many items we can currently fit in the view area.
        self._items_in_width = 0
        self._items_in_height = 0

        # Which row is the one we are currently scrolled to.
        # e.g. the top row in the grid.
        # (We don't actually scroll the grid, we scroll the data,
        # but the concept is the same)
        self._scroll_row = 0
        # What is the maximum top row we can scroll to,
        # before we get a full row of whitespace at the bottom?
        # The last, potentially cut off, row doesn't count as whitespace.
        self._max_scroll_row = 0

        # ---- Layout ----

        self.setFrameShape(Qwidgets.QFrame.StyledPanel)

        self._layout = Qwidgets.QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.setLayout(self._layout)

        # Add a scroll area to allow for overflow.
        # We are not actually going to use the area's scrollbars,
        # because by default they scroll the widgets,
        # and we want to scroll the data while leaving the actual widgets where they are.
        scroll_area = Qwidgets.QScrollArea()
        scroll_area.setFrameShape(Qwidgets.QFrame.NoFrame)

        scroll_area.setVerticalScrollBarPolicy(Qcore.Qt.ScrollBarAlwaysOff)
        scroll_area.setHorizontalScrollBarPolicy(Qcore.Qt.ScrollBarAlwaysOff)
        scroll_area.setWidgetResizable(True)
        # We will filter scroll events for the scroll area.
        scroll_area.viewport().installEventFilter(self)
        self._layout.addWidget(scroll_area)

        # Create the container that keeps our asset grid widget from growing bigger than it's contents.
        # TODO: there must be a better way to do this.
        spacer_widget = Qwidgets.QWidget()
        spacer_widget.setStyleSheet("background: white;")
        spacer_layout = Qwidgets.QGridLayout()
        spacer_widget.setLayout(spacer_layout)
        scroll_area.setWidget(spacer_widget)

        spacer_layout.setContentsMargins(0, 0, 0, 0)
        spacer_layout.setSpacing(0)
        # The widget grid will be at (0, 0), which should not stretch.
        spacer_layout.setRowStretch(0, 0)
        spacer_layout.setRowStretch(1, 1)
        spacer_layout.setColumnStretch(0, 0)
        spacer_layout.setColumnStretch(1, 1)

        # Create the widget that will contain the asset grid.
        self._asset_grid_widget = Qwidgets.QWidget()
        self._asset_layout = Qwidgets.QGridLayout()
        self._asset_grid_widget.setLayout(self._asset_layout)

        self._asset_layout.setContentsMargins(0, 0, 0, 0)
        self._asset_layout.setSpacing(0)
        spacer_layout.addWidget(self._asset_grid_widget, 0, 0)

        self._scrollbar = Qwidgets.QScrollBar(Qcore.Qt.Vertical)
        self._layout.addWidget(self._scrollbar)

        # Our minimum size is 1 asset + horizontal scrollbar
        self.setMinimumWidth(self._item_width + self._scrollbar.minimumWidth())
        self.setMinimumHeight(self._item_height)

        # TODO: Fill with as much asset widgets as needed to fill the size, but no more.
        #   and adjust scrollbar to match how many didn't fit.
        # TODO: when the user scrolls, we don't actually scroll the asset widgets.
        #       we simply set new assets to the existing widgets.

    def show_assets(self, assets: dict):
        self._assets = assets
        self._update_display()

    def _update_display(self):
        # Start displaying assets at the place we are currently scrolled to.
        asset_index = int(self._scroll_row) * self._items_in_width
        assets = list(self._assets.values())

        for row in self._asset_grid:
            for widget in row:
                if asset_index < len(assets):
                    widget.show_asset(assets[asset_index])
                    asset_index += 1
                else:
                    # No more assets to fill with.
                    widget.remove_asset()

    def resizeEvent(self, event: Qgui.QResizeEvent) -> None:
        super().resizeEvent(event)

        grid_width = event.size().width() - self._scrollbar.width()
        grid_height = event.size().height()

        # Don't overflow horizontally (floor).
        new_items_in_width = math.floor(grid_width / self._item_width)
        # Do overflow vertically down (ceil).
        # This is an extra hint (next to the scrollbar...) to the user that they can scroll this vertically.
        new_items_in_height = math.ceil(grid_height / self._item_height)

        # We do not remove excess horizontal or vertical widgets.
        # As the fact that we generated them means that we needed them once,
        # and that means we might have to use them again. (That, and it doesn't cost that much to keep them).

        # Add any extra widgets that now fit.
        for y in range(0, new_items_in_height):
            if y >= len(self._asset_grid):
                self._asset_grid.append([])
                # No stretching.
                self._asset_layout.setRowStretch(y, 0)

            for x in range(0, new_items_in_width):
                if x >= len(self._asset_grid[y]):
                    new_widget = AssetWidget()
                    self._asset_grid[y].append(new_widget)
                    self._asset_layout.addWidget(new_widget, y, x, alignment=Qcore.Qt.AlignLeft)
                    # No stretching
                    self._asset_layout.setColumnStretch(x, 0)

        # Remove unneeded vertical widgets.
        # From bottom to top, to make sure we don't walk over things we just deleted.
        for extra_y in reversed(range(new_items_in_height, len(self._asset_grid))):
            for widget in self._asset_grid[extra_y]:
                self._asset_layout.removeWidget(widget)
                widget.deleteLater()
            del self._asset_grid[extra_y]

        # Remove unneeded horizontal widgets.
        for row in self._asset_grid:
            # From right to left, to make sure we don't walk over things we just deleted.
            for extra_x in reversed(range(new_items_in_width, len(row))):
                widget = row[extra_x]
                self._asset_layout.removeWidget(widget)
                widget.deleteLater()

                del row[extra_x]

        # This is how many rows displaying all the items at the same time would take.
        total_number_of_rows = math.ceil(len(self._assets.values()) / new_items_in_width)
        # Make sure we don't scroll past the last items.
        # The extra +1 is because we allow the last row to be clipped, so we want to scroll 1 more.
        self._max_scroll_row = total_number_of_rows - new_items_in_height + 1

        self._items_in_width = new_items_in_width
        self._items_in_height = new_items_in_height

        # Update which assets go where.
        self._update_display()

    def eventFilter(self, source: Qcore.QObject, event: Qcore.QEvent) -> bool:
        # Catch the mouse wheel event.
        if event.type() == Qcore.QEvent.Wheel:
            # TODO: support finer scrolling. Some mouses scroll with smaller deltas.
            # Most mice scroll in steps of 15 degrees.
            # The angle is given in 8ths of a degree.
            # Therefore: 120.
            steps = event.angleDelta().y() / 120

            # Inverse scrolling.
            self.scroll(0, -int(steps))
            # Catch the event.
            event.accept()
            logging.debug(steps)
            return True
        # Propagate all other events.
        return False

    def scroll(self, dx: int, dy: int) -> None:
        """
        Widget only scrolls in the y direction.
        :param dx:
        :param dy: Amount of items to scroll.
        Will scroll faster the more items we can display vertically.
        :return:
        """
        if self._items_in_height > self.SCROLL_3_PER_TICK_LIMIT:
            dy = 3 * dy
        elif self._items_in_height > self.SCROLL_2_PER_TICK_LIMIT:
            dy = 2 * dy

        self._scroll_row = min(max(self._scroll_row + dy, 0), self._max_scroll_row)
        self._update_display()


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
