import PyQt5.QtCore as core


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
        self._asset_packs.append(pack_path)
        self.pack_added.emit(pack_path.dirName(), pack_path)

    def add_asset_packs(self, pack_paths: [core.QDir]):
        for pack in pack_paths:
            self.add_asset_pack(pack)
