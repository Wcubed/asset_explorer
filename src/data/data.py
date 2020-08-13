import collections
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

        # path hash -> Asset, ordered dictionary of the assets.
        # The dictionary is ordered to make the assets display in the same order every time and in every view.
        self._asset_packs = collections.OrderedDict()

    def add_asset_pack(self, pack_path: Qcore.QDir):
        # TODO(WWE): Check if the directory is not a subdirectory of one we already have.
        #   or a parent directory.
        #   return an exception when that happens.

        # TODO: maybe we dont' want to scan every file on start? just use the saved asset list (when we have it)?
        #       Or scan it in a separate thread?

        new_pack = AssetPack(pack_path)

        # Make sure this isn't a duplicate.
        if new_pack.get_hash() in self._asset_packs.keys():
            # It's a duplicate.
            logging.info("Duplicate pack \"{}\" is already loaded.".format(new_pack.get_path()))
            # We don't want to add this one.
            return

        self._asset_packs[new_pack.get_hash()] = new_pack

        # Does this already have a config?
        if not new_pack.load_config_from_disk():
            # TODO: do this asynchronously, and with a progress bar?
            #       and do we want to re-scan on startup?
            new_pack.scan_pack_directory()
            # TODO: At what other points do we want to save the configuration?
            new_pack.save_config_to_disk()

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
