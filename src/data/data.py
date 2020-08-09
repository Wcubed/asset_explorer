import PyQt5.QtCore as core

from . import asset_pack


class Data(core.QObject):
    """
    Emitted when a new asset pack has been added.
    (name, pack_directory)
    """
    pack_added = core.pyqtSignal(str, core.QDir)

    def __init__(self):
        super().__init__()

        self._asset_packs = []

    def add_asset_pack(self, pack_path: core.QDir):
        # TODO(WWE): Check if the directory is not a subdirectory of one we already have.
        #   or a duplicate directory.
        #   or a parent directory.
        #   return an exception when that happens.
        new_pack = asset_pack.AssetPack(pack_path)

        self._asset_packs.append(new_pack)
        self.pack_added.emit(new_pack.name, new_pack.path)

    def add_asset_packs(self, pack_paths: [core.QDir]):
        for pack in pack_paths:
            self.add_asset_pack(pack)
