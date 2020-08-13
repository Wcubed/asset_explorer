import math

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

        # hash -> Asset, ordered dictionary of the assets to be displayed.
        self._assets = {}
        # [y][x] grid of asset widgets.
        self._asset_grid = []
        self._item_width = AssetWidget.WIDTH
        self._item_height = AssetWidget.HEIGHT

        # How many items we can currently fit in the view area.
        self._items_in_width = 0
        self._items_in_height = 0

        # Which asset index is the one we are currently scrolled to?
        # This asset will always be displayed in the top row of the grid.
        self._asset_index_in_top_row = 0
        # Which row is currently the top one?
        self._top_scroll_row = 0
        # What is the maximum top row we can scroll to
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
        # TODO: there must be a better way to do this instead of nesting many widgets.
        #       It works though.
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
        self._scrollbar.setMinimum(0)
        self._layout.addWidget(self._scrollbar)

        # Our minimum size is 1 asset + horizontal scrollbar
        # We can't just use "minimumWidth" on the scrollbar, since it is apparently allowed to be 0 wide.
        self.setMinimumWidth(self._item_width + self._scrollbar.sizeHint().width())
        self.setMinimumHeight(self._item_height)

        # ---- Connections ----
        self._scrollbar.valueChanged.connect(self.on_scrollbar_value_changed)

    def show_assets(self, assets: dict):
        self._assets = assets

        # Scroll up when displaying new assets.
        self._scrollbar.setValue(0)

        self._calculate_grid_layout()
        self._update_display()

    def _update_display(self):
        self._scrollbar.setMaximum(self._max_scroll_row)
        # Keep the asset we were scrolled to in the top row.
        self._scrollbar.setValue(math.floor(self._asset_index_in_top_row / self._items_in_width))

        # Start displaying assets at the place we are currently scrolled to.
        asset_index = self._top_scroll_row * self._items_in_width
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

        # Recalculate all the values with the new size.
        self._calculate_grid_layout()

        # We do not remove excess horizontal or vertical widgets.
        # As the fact that we generated them means that we needed them once,
        # and that means we might have to use them again. (That, and it doesn't cost that much to keep them).

        # Add any extra widgets that now fit.
        for y in range(0, self._items_in_height):
            if y >= len(self._asset_grid):
                self._asset_grid.append([])
                # No stretching.
                self._asset_layout.setRowStretch(y, 0)

            for x in range(0, self._items_in_width):
                if x >= len(self._asset_grid[y]):
                    new_widget = AssetWidget()
                    self._asset_grid[y].append(new_widget)
                    self._asset_layout.addWidget(new_widget, y, x, alignment=Qcore.Qt.AlignLeft)
                    # No stretching
                    self._asset_layout.setColumnStretch(x, 0)

        # Remove unneeded vertical widgets.
        # From bottom to top, to make sure we don't walk over things we just deleted.
        for extra_y in reversed(range(self._items_in_height, len(self._asset_grid))):
            for widget in self._asset_grid[extra_y]:
                self._asset_layout.removeWidget(widget)
                widget.deleteLater()
            del self._asset_grid[extra_y]

        # Remove unneeded horizontal widgets.
        for row in self._asset_grid:
            # From right to left, to make sure we don't walk over things we just deleted.
            for extra_x in reversed(range(self._items_in_width, len(row))):
                widget = row[extra_x]
                self._asset_layout.removeWidget(widget)
                widget.deleteLater()

                del row[extra_x]

        # Update which assets go where.
        self._update_display()

    def _calculate_grid_layout(self):
        """
        Calculates all the values that are needed for the proper layout of the grid.
        """
        grid_width = self.width() - self._scrollbar.width()
        grid_height = self.height()

        # Don't overflow horizontally (floor).
        self._items_in_width = math.floor(grid_width / self._item_width)
        # We don't display less than 1 item in the width.
        self._items_in_width = max(self._items_in_width, 1)

        # Do overflow vertically down (ceil).
        # This is an extra hint (next to the scrollbar...) to the user that they can scroll this vertically.
        self._items_in_height = math.ceil(grid_height / self._item_height)

        # This is how many rows displaying all the items at the same time would take.
        total_number_of_rows = math.ceil(len(self._assets.values()) / self._items_in_width)
        # Make sure we don't scroll past the last items.
        # The extra +1 is because we allow the last row to be clipped, so we want to scroll 1 more.
        self._max_scroll_row = max(total_number_of_rows - self._items_in_height + 1, 0)

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
            return True
        # Propagate all other events.
        return False

    @Qcore.pyqtSlot(int)
    def on_scrollbar_value_changed(self, row_value: int):
        # Only re-calculate the asset we are scrolled to, if the last one is no longer in the top row.
        # This allows us to resize the screen and always keep a certain asset at the top.
        if row_value != math.floor(self._asset_index_in_top_row / self._items_in_width):
            # Which asset index is at the top left?
            self._asset_index_in_top_row = max(0, min(row_value, self._max_scroll_row)) * self._items_in_width

        self._top_scroll_row = row_value
        self._update_display()

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

        # The scrollbar works per row, not per asset.
        new_value = max(0, min(self._top_scroll_row + dy, self._max_scroll_row))
        # Set the scrollbar position, and let the `valueChanged` signal take care of the rest.
        self._scrollbar.setValue(new_value)
