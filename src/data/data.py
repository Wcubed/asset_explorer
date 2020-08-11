import logging

import PyQt5.QtCore as Qcore

from data import AssetPack


class Data(Qcore.QObject):
    # Emitted when a new asset pack has been added.
    # (pack_hash)
    pack_added = Qcore.pyqtSignal(str)
    packs_removed = Qcore.pyqtSignal()

    def __init__(self):
        super().__init__()

        # path hash -> AssetPack, dictionary.
        self._asset_packs = {}

    def add_asset_pack(self, pack_path: Qcore.QDir):
        # TODO(WWE): Check if the directory is not a subdirectory of one we already have.
        #   or a parent directory.
        #   return an exception when that happens.

        new_pack = AssetPack(pack_path)

        # Make sure this isn't a duplicate.
        if new_pack.get_hash() in self._asset_packs.keys():
            # It's a duplicate.
            logging.info("Duplicate pack \"{}\" is already loaded.".format(new_pack.get_path()))
            # We don't want to add this one.
            return

        self._asset_packs[new_pack.get_hash()] = new_pack

        # TODO: do this asynchronously, and with a progress bar?
        new_pack.scan_pack_directory()

        logging.info(
            "Added asset pack \"{}\" from: \"{}\"".format(new_pack.get_name(), new_pack.get_path()))

        self.pack_added.emit(new_pack.get_hash())

    def add_asset_packs(self, pack_paths: [Qcore.QDir]):
        for pack in pack_paths:
            self.add_asset_pack(pack)

    def get_pack(self, pack_hash: str) -> AssetPack:
        return self._asset_packs[pack_hash]

    def get_packs(self) -> dict:
        return self._asset_packs

    def remove_packs(self, pack_hashes: [str]):
        for pack_hash in pack_hashes:
            if pack_hash in self._asset_packs:
                pack = self.get_pack(pack_hash)
                logging.info("Removing pack: \"{}\"".format(pack.get_name()))

                del self._asset_packs[pack_hash]

        self.packs_removed.emit()
