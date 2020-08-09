import logging

import PyQt5.QtCore as Qcore

from data import AssetPack


class Data(Qcore.QObject):
    """
    Emitted when a new asset pack has been added.
    (name, asset_count, pack_directory)
    """
    pack_added = Qcore.pyqtSignal(str, int, Qcore.QDir)

    def __init__(self):
        super().__init__()

        self._asset_packs = {}

    def add_asset_pack(self, pack_path: Qcore.QDir):
        # TODO(WWE): Check if the directory is not a subdirectory of one we already have.
        #   or a parent directory.
        #   return an exception when that happens.

        # Make sure this isn't a duplicate.
        if pack_path.absolutePath() in self._asset_packs.keys():
            # It's a duplicate.
            logging.info("The folder \"{}\" is already loaded as an asset pack.".format(pack_path.absolutePath()))
            # We don't want to add this one.
            return

        new_pack = AssetPack(pack_path)

        self._asset_packs[pack_path.absolutePath()] = new_pack

        # TODO: do this asynchronously, and with a progress bar?
        new_pack.scan_pack_directory()

        logging.info("Added asset pack \"{}\" from: \"{}\"".format(new_pack.name, new_pack.path.absolutePath()))

        self.pack_added.emit(new_pack.name, new_pack.get_asset_count(), new_pack.path)

    def add_asset_packs(self, pack_paths: [Qcore.QDir]):
        for pack in pack_paths:
            self.add_asset_pack(pack)

    def get_pack(self, path: Qcore.QDir) -> AssetPack:
        # TODO: throw exception if we don't have that pack.
        return self._asset_packs[path.absolutePath()]

    def get_packs(self) -> dict:
        return self._asset_packs
