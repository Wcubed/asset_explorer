import pathlib

from data import Asset


class AssetDir:
    def __init__(self, path, subdirs: dict, assets: dict):
        """
        :param path: Absolute path to this directory.
        :param subdirs: List of subdirectories in this directory.
        :param assets: uuid -> Asset dictionary of assets in this directory.
        """
        self._path = pathlib.Path(path).absolute()
        self._subdirs = subdirs
        self._assets = assets

    def absolute_path(self):
        """
        :return: The absolute path as a `pathlib.Path`.
        """
        return self._path

    def subdirs(self):
        """
        :return: A dictionary of all subdirectories (`AssetDir`) that contain assets.
                 The keys are the relative paths as `pathlib.Path`.
        """
        return self._subdirs

    def assets(self):
        """
        :return: A dictionary containing all the `Assets` that are directly in this folder.
                 The keys are the assets uuid.
        """
        return self._assets

    @staticmethod
    def load(path):
        # TODO: load from the .asset_dir.json file, if it exists.

        _path = pathlib.Path(path)

        assets = {}
        subdirs = {}
        for item in _path.iterdir():
            if item.is_dir():
                # Recursively load the subdirectories.
                new_subdir = AssetDir.load(item)

                # Only actually record the directory, if the directory tree contains any assets.
                if len(new_subdir.assets()) > 0 or len(new_subdir.subdirs()) > 0:
                    rel_path = item.relative_to(_path)
                    subdirs[rel_path] = new_subdir
            elif Asset.is_asset(item):
                # Found a new asset in this directory.
                new_asset = Asset(item)
                assets[new_asset.uuid()] = new_asset

        return AssetDir(path, subdirs, assets)
