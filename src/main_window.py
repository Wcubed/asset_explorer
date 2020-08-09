import PyQt5.QtWidgets as widgets

import data
from widgets import filesystem_explorer, pack_list_widget


class MainWindow(widgets.QWidget):
    def __init__(self):
        super().__init__()

        self.data = data.Data()

        # ---- Layout ----

        layout = widgets.QHBoxLayout()
        self.setLayout(layout)

        self.setWindowTitle(self.tr("Asset Explorer"))

        self.main_splitter = widgets.QSplitter()
        layout.addWidget(self.main_splitter)
        self.main_splitter.setHandleWidth(10)

        explorer_column = widgets.QWidget()
        explorer_layout = widgets.QVBoxLayout()
        explorer_layout.setContentsMargins(0, 0, 0, 0)
        explorer_column.setLayout(explorer_layout)
        self.main_splitter.addWidget(explorer_column)
        # Explorer shouldn't auto-stretch.
        self.main_splitter.setStretchFactor(0, 0)

        self.directory_explorer = filesystem_explorer.FilesystemExplorer()
        explorer_layout.addWidget(self.directory_explorer)

        new_asset_dir_button = widgets.QPushButton(text=self.tr("Add selected folders as packs"))
        new_asset_dir_button.clicked.connect(self.add_new_asset_packs)
        explorer_layout.addWidget(new_asset_dir_button)

        self.asset_dirs = pack_list_widget.PackListWidget()
        self.main_splitter.addWidget(self.asset_dirs)
        self.main_splitter.setStretchFactor(1, 1)

        # Make sure the view updates when the data structure grows.
        self.data.pack_added.connect(self.asset_dirs.add_pack)

    def add_new_asset_packs(self):
        new_dirs = self.directory_explorer.get_selected_directories()

        self.data.add_asset_packs(new_dirs)
        self.directory_explorer.clear_selection()
