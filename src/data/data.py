import logging

import PyQt5.QtCore as core

from . import asset_pack


class Data(core.QObject):
    """
    Emitted when a new asset pack has been added.
    (name, asset_count, pack_directory)
    """
    pack_added = core.pyqtSignal(str, int, core.QDir)

    def __init__(self):
        super().__init__()

        self._asset_packs = []

    def add_asset_pack(self, pack_path: core.QDir):
        # TODO(WWE): Check if the directory is not a subdirectory of one we already have.
        #   or a parent directory.
        #   return an exception when that happens.

        # Make sure this isn't a duplicate.
        for pack in self._asset_packs:
            if pack.path == pack_path:
                # It's a duplicate.
                logging.info("The folder \"{}\" is already loaded as an asset pack.".format(pack_path.absolutePath()))
                # We don't want to add this one.
                return

        new_pack = asset_pack.AssetPack(pack_path)

        self._asset_packs.append(new_pack)

        # TODO: do this asynchronously, and with a progress bar?
        new_pack.scan_pack_directory()

        logging.info("Added asset pack \"{}\" from: \"{}\"".format(new_pack.name, new_pack.path.absolutePath()))

        self.pack_added.emit(new_pack.name, new_pack.get_asset_count(), new_pack.path)

    def add_asset_packs(self, pack_paths: [core.QDir]):
        for pack in pack_paths:
            self.add_asset_pack(pack)
