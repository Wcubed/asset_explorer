import json
import logging

from PyQt5.QtCore import QDir, QDirIterator

from data import Asset


class AssetPack:
    """
    Accepted asset file extensions.
    """
    FILE_EXTENSIONS = ["*.png"]

    CONFIG_FILE_NAME = "asset_pack.json"
    # Version number to keep track of breaking changes in config files.
    CONFIG_VERSION = 1
    # Keys for the configuration dictionary.
    CFG_KEY_VERSION = "config_version"
    CFG_KEY_ASSETS = "assets"

    def __init__(self, path: QDir):
        self._path = path
        self._config_file = path.absoluteFilePath(self.CONFIG_FILE_NAME)

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

    def load_config_from_disk(self) -> bool:
        """
        :return: `True` when load succeeded, `False` on an error.
        """
        self._assets = {}

        try:
            with open(self._config_file, 'r') as f:
                logging.info("Loading asset pack from: \"{}\"".format(self._config_file))
                config = json.load(f)

                version = config[self.CFG_KEY_VERSION]
                # Check if we know this config version.
                if version != self.CONFIG_VERSION:
                    # TODO: what to do if the versions don't match?
                    logging.info(
                        "Unknown config version found: \'{}\', "
                        "expected: \'{}\'. Will attempt to load anyway.".format(version, self.CONFIG_VERSION))

                asset_paths = config[self.CFG_KEY_ASSETS]
                for asset_path in asset_paths:
                    absolute_path = self._path.absoluteFilePath(asset_path)
                    new_asset = Asset(absolute_path)
                    self._assets[new_asset.get_hash()] = new_asset

                return True

        except IOError:
            # TODO: show an appropriate error message?
            #       if the file does not exist, that is only an error if our
            #       global config told us this pack should exist.
            return False

    def save_config_to_disk(self):
        # List of asset paths relative to the top-level pack directory.
        assets = []
        for asset in self._assets.values():
            relative_path = asset.get_relative_path(self._path)
            assets.append(relative_path)

        config = {
            self.CFG_KEY_VERSION: self.CONFIG_VERSION,
            self.CFG_KEY_ASSETS: assets,
        }

        with open(self._config_file, 'w') as f:
            json.dump(config, f)
