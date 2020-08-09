import logging

import PyQt5.QtWidgets as widgets
from PyQt5.QtCore import QDirIterator, QDir

import data
from widgets import filesystem_explorer, asset_dirs

ASSET_FILE_EXTENSIONS = ["*.png"]


class MainWindow(widgets.QWidget):
    def __init__(self):
        super().__init__()

        self.data = data.Data()

        # ---- Layout ----

        layout = widgets.QHBoxLayout()
        self.setLayout(layout)

        self.setWindowTitle(self.tr("Asset Explorer"))

        explorer_column = widgets.QWidget()
        explorer_layout = widgets.QVBoxLayout()
        explorer_layout.setContentsMargins(0, 0, 0, 0)
        explorer_column.setLayout(explorer_layout)
        layout.addWidget(explorer_column)

        self.directory_explorer = filesystem_explorer.FilesystemExplorer()
        explorer_layout.addWidget(self.directory_explorer)

        new_asset_dir_button = widgets.QPushButton(text=self.tr("Add selected"))
        new_asset_dir_button.clicked.connect(self.add_new_asset_folder)
        explorer_layout.addWidget(new_asset_dir_button)

        asset_dir_column = widgets.QWidget()
        asset_dir_layout = widgets.QVBoxLayout()
        asset_dir_layout.setContentsMargins(0, 0, 0, 0)
        asset_dir_column.setLayout(asset_dir_layout)
        layout.addWidget(asset_dir_column)

        self.asset_dirs = asset_dirs.AssetDirs()
        asset_dir_layout.addWidget(self.asset_dirs)

    def add_new_asset_folder(self):
        new_dirs = self.directory_explorer.get_selected_directories()

        self.data.add_asset_dirs(new_dirs)

    def scan_asset_directory(self, path):
        # TODO: this should probably be put in the DATA class.
        files = QDirIterator(path, ASSET_FILE_EXTENSIONS, QDir.Files, QDirIterator.Subdirectories)

        while files.hasNext():
            file = files.next()
            logging.info(file)
