import json
import pathlib

from data import Asset


class AssetDir:
    CONFIG_FILE_NAME = ".asset_dir.json"
    # For keeping track of breaking changes.
    CONFIG_VERSION = 1

    # Config keys.
    CFG_VERSION = "version"
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

    def assets_recursive(self):
        """
        :return: All the assets contained in this directory and all of the recursive subdirectories.
        """
        assets = self._assets
        for subdir in self._subdirs.values():
            assets.update(subdir.assets_recursive())
        return assets

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

        if save:
            assets_dict = {}
            for asset in self._assets.values():
                asset_dict = {
                    self.CFG_ASSET_UUID: str(asset.uuid()),
                }
                assets_dict[str(asset.relative_path(self._path))] = asset_dict

            config_dict = {
                self.CFG_VERSION: self.CFG_VERSION,
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
        # Keep track of which asset paths we already know of.
        asset_paths = []
        try:
            with open(_path.joinpath(AssetDir.CONFIG_FILE_NAME), 'r') as f:
                config = json.load(f)

                if config[AssetDir.CFG_VERSION] != AssetDir.CONFIG_VERSION:
                    # TODO: what to do if the config version does not match.
                    pass

                assets_dict = config[AssetDir.CFG_ASSETS]

                # Load all the assets from the file.
                for path, asset_dict in assets_dict.items():
                    asset_uuid = asset_dict[AssetDir.CFG_ASSET_UUID]
                    new_asset = Asset(path, asset_uuid=asset_uuid)

                    assets[asset_uuid] = new_asset
                    asset_paths.append(path)
        except IOError:
            # TODO: what if we can't access the file, but we know it's there?
            #   The file not existing is not an error. Because then it is a new directory.
            pass
        except KeyError:
            # TODO: what do we do when a key we expect to be there is not there?
            pass

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
                # Do we already know of this asset?
                if str(item.relative_to(_path)) not in asset_paths:
                    # Found a new asset in this directory, that was not in the config file.
                    new_asset = Asset(item)
                    assets[new_asset.uuid()] = new_asset

        # TODO: What do we do with assets that were in the save file, but now are not?

        return AssetDir(path, subdirs, assets)
