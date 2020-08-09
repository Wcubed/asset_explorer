import logging

from PyQt5.QtCore import QDir, QDirIterator

from data import Asset


class AssetPack:
    """
    Accepted asset file extensions.
    """
    FILE_EXTENSIONS = ["*.png"]

    def __init__(self, path: QDir):
        self.path = path
        self.name = path.dirName()

        self.assets = {}

    def scan_pack_directory(self):
        """
        Scans the asset pack directory for assets.
        Removes old ones and adds new ones.
        # TODO: do we want to support moving subdirectories / renaming png's?
                So that when we detect that an item has disappeared, that we ask if it has been moved / renamed?
                That way, one wouldn't loose the tags / other settings on it.
        """

        self.assets = {}

        files = QDirIterator(self.path.absolutePath(), self.FILE_EXTENSIONS, QDir.Files, QDirIterator.Subdirectories)

        while files.hasNext():
            path = files.next()
            asset = Asset(path)

            self.assets[asset.get_absolute_path()] = asset

        logging.info("Found {} assets in pack \"{}\"".format(len(self.assets), self.name))

    def get_asset_count(self) -> int:
        return len(self.assets.keys())

    def get_assets(self) -> [Asset]:
        return self.assets
