import PyQt5.QtCore as Qcore
import PyQt5.QtGui as Qgui
import PyQt5.QtWidgets as Qwidgets

from data import Asset


class AssetFlowGridItemWidget(Qwidgets.QWidget):
    # Width and height in px of the displayed images.
    IMAGE_SIZE = 100
    MARGIN = 4

    WIDTH = IMAGE_SIZE + MARGIN * 2
    HEIGHT = IMAGE_SIZE + MARGIN * 2

    # Fires when the left mouse button is pressed.
    # Sends along x and y position in the grid, along with the asset index in the flow grid.
    left_mouse_pressed = Qcore.pyqtSignal(int, int, int)

    def __init__(self, grid_x, grid_y):
        super().__init__()

        self._asset = None

        # Which index does the asset displayed have in the flow grid?
        # Necessary for selections.
        self._asset_index = 0
        # Where in the physical grid this widget is located.
        self._grid_x = grid_x
        self._grid_y = grid_y

        layout = Qwidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.setSizePolicy(Qwidgets.QSizePolicy.Fixed, Qwidgets.QSizePolicy.Fixed)

        self._display = Qwidgets.QLabel()
        self._display.setContentsMargins(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        self._display.setFixedSize(Qcore.QSize(self.IMAGE_SIZE, self.IMAGE_SIZE))
        layout.addWidget(self._display)

    def show_asset(self, asset: Asset, asset_index: int):
        """
        By default the widget will not load the image.
        Call this when the asset widget becomes visible.
        """
        self._asset = asset
        self._asset_index = asset_index

        self._display.setPixmap(self._asset.load_thumbnail_cached(self.IMAGE_SIZE))

    def clear_display(self):
        """
        Clears the asset from this widget.
        """
        if self._asset:
            self._display.clear()
            self._asset = None
            self._asset_index = 0

    def set_selected(self, selected: bool):
        # TODO: use the QPallete defined selection color.
        # TODO: Show the selection around the image, not just behind it.
        #    (or maybe not even behind it and only just around it.)
        if selected:
            self.setStyleSheet("background-color: blue;")
        else:
            self.setStyleSheet("")

    def mousePressEvent(self, event: Qgui.QMouseEvent) -> None:
        # If we have an asset, we should react to left click selection events.
        if self._asset is not None and event.button() == Qcore.Qt.LeftButton:
            self.left_mouse_pressed.emit(self._grid_x, self._grid_y, self._asset_index)
