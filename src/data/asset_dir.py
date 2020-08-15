import json
import pathlib

from data import Asset


class AssetDir:
    CONFIG_FILE_NAME = ".asset_dir.json"

    # Config keys.
    CFG_ASSETS = "assets"
    CFG_ASSET_UUID = "uuid"

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

    def save(self):
        """
        Recursively saves the json file for this directory, and all subdirectories.
        Only actually updates a directory's file if any of the assets was marked as dirty.
        Only creates json files in directories with assets.
        :return:
        """
        # Are any assets dirty? Then we save this directory.
        save = False
        for asset in self._assets.values():
            if asset.is_dirty():
                save = True
                break

        assets_dict = {}
        for asset in self._assets.values():
            asset_dict = {
                self.CFG_ASSET_UUID: str(asset.uuid()),
            }
            assets_dict[str(asset.relative_path(self._path))] = asset_dict

        config_dict = {
            self.CFG_ASSETS: assets_dict,
        }

        with open(self._path.joinpath(self.CONFIG_FILE_NAME), 'w') as f:
            json.dump(config_dict, f)

        # Always check the subdirectories.
        for subdir in self._subdirs.values():
            subdir.save()

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
