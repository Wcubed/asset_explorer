from PyQt5.QtCore import QDir


class AssetPack:
    def __init__(self, path: QDir):
        self.path = path
        self.name = path.dirName()
