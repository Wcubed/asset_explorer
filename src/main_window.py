import logging

import PyQt5.QtWidgets as widgets
from PyQt5.QtCore import QDirIterator, QDir

import data
from widgets.directory_explorer import DirectoryExplorer

ASSET_FILE_EXTENSIONS = ["*.png"]


class MainWindow(widgets.QWidget):
    def __init__(self):
        super().__init__()

        self.data = data.Data()

        # ---- Layout ----

        layout = widgets.QVBoxLayout()
        self.setLayout(layout)

        self.setWindowTitle(self.tr("Asset Explorer"))

        directory_explorer = DirectoryExplorer()
        layout.addWidget(directory_explorer)

        new_asset_dir_button = widgets.QPushButton(text=self.tr("New"))
        new_asset_dir_button.clicked.connect(self.add_new_asset_folder)
        layout.addWidget(new_asset_dir_button)

    def add_new_asset_folder(self):
        new_dir = widgets.QFileDialog.getExistingDirectory(parent=self, caption=self.tr("Select an asset folder"),
                                                           options=widgets.QFileDialog.DontResolveSymlinks)

        if new_dir == "":
            return

        self.data.add_asset_dir(new_dir)

    def scan_asset_directory(self, path):
        # TODO: this should probably be put in the DATA class.
        files = QDirIterator(path, ASSET_FILE_EXTENSIONS, QDir.Files, QDirIterator.Subdirectories)

        while files.hasNext():
            file = files.next()
            logging.info(file)
