import logging

from PyQt5.QtCore import QDir, QDirIterator

from data import Asset


class AssetPack:
    """
    Accepted asset file extensions.
    """
    FILE_EXTENSIONS = ["*.png"]

    def __init__(self, path: QDir):
        self._path = path
        # Qt does not seem to like the large numbers `hash` generates, so we make it a string instead.
        # Not as efficient, but works for our purposes,
        # as we need to use it as a string in some places anyways (tables for example).
        self._hash = str(hash(self.get_path()))
        self._name = path.dirName()

        self._assets = {}

    def scan_pack_directory(self):
        """
        Scans the asset pack directory for assets.
        Removes old ones and adds new ones.
        # TODO: do we want to support moving subdirectories / renaming png's?
                So that when we detect that an item has disappeared, that we ask if it has been moved / renamed?
                That way, one wouldn't loose the tags / other settings on it.
        """

        self._assets = {}

        files = QDirIterator(self._path.absolutePath(), self.FILE_EXTENSIONS, QDir.Files, QDirIterator.Subdirectories)

        while files.hasNext():
            path = files.next()
            asset = Asset(path)

            self._assets[asset.get_hash()] = asset

        logging.info("Found {} assets in pack \"{}\"".format(len(self._assets), self._name))

    def get_asset_count(self) -> int:
        return len(self._assets)

    def get_assets(self) -> [Asset]:
        return self._assets

    def get_hash(self):
        return self._hash

    def get_path(self):
        return self._path.absolutePath()

    def get_name(self):
        return self._name
