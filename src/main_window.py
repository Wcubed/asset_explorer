import logging

from PyQt5.QtCore import QDirIterator, QDir
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QListWidget

import data

ASSET_FILE_EXTENSIONS = ["*.png"]


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.data = data.Data()

        # ---- Layout ----

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.setWindowTitle(self.tr("Asset Explorer"))

        asset_dir_widget = QListWidget()
        layout.addWidget(asset_dir_widget)

        new_asset_dir_button = QPushButton(text=self.tr("New"))
        new_asset_dir_button.clicked.connect(self.add_new_asset_folder)
        layout.addWidget(new_asset_dir_button)

    def add_new_asset_folder(self):
        new_dir = QFileDialog.getExistingDirectory(parent=self, caption=self.tr("Select an asset folder"),
                                                   options=QFileDialog.DontResolveSymlinks)

        if new_dir == "":
            return

        self.data.add_asset_dir(new_dir)

    def scan_asset_directory(self, path):
        # TODO: this should probably be put in the DATA class.
        files = QDirIterator(path, ASSET_FILE_EXTENSIONS, QDir.Files, QDirIterator.Subdirectories)

        while files.hasNext():
            file = files.next()
            logging.info(file)
