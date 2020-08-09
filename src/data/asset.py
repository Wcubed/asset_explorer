from PyQt5.QtCore import QFileInfo


class Asset:
    def __init__(self, path: str):
        self.file_info = QFileInfo(path)

    def get_name(self) -> str:
        return self.file_info.fileName()
