import pathlib


class AssetDir:
    def __init__(self, path, subdirs, assets):
        """
        :param path: Absolute path to this directory.
        :param subdirs: List of subdirectories in this directory.
        :param assets: uuid -> Asset dictionary of assets in this directory.
        """
        self._path = pathlib.Path(path).absolute()
        self._subdirs = subdirs
        self._assets = assets

    def absolute_path(self):
        return self._path

    def subdirs(self):
        return self._subdirs

    def assets(self):
        return self._assets

    @staticmethod
    def load(path):
        return AssetDir(path, [], {})
