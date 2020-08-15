import json
import pathlib
import uuid

from data import Asset


class AssetDir:
    CONFIG_FILE_NAME = ".asset_dir.json"
    # For keeping track of breaking changes.
    CONFIG_VERSION = 1

    # Config keys.
    CFG_VERSION = "version"
    CFG_ASSETS = "assets"
    CFG_ASSET_UUID = "uuid"
    CFG_ASSET_TAGS = "tags"

    def __init__(self, path, subdirs: dict, assets: dict):
        """
        :param path: Absolute path to this directory.
        :param subdirs: List of subdirectories in this directory.
        :param assets: uuid -> Asset dictionary of assets in this directory.
        """
        self._path = pathlib.Path(path).absolute()
        self._subdirs = subdirs
        self._assets = assets

    def name(self):
        return self._path.name

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

    def asset_count(self):
        return len(self._assets)

    def assets_recursive(self):
        """
        :return: All the assets contained in this directory and all of the recursive subdirectories.
        """
        assets = self._assets
        for subdir in self._subdirs.values():
            assets.update(subdir.assets_recursive())
        return assets

    def asset_count_recursive(self):
        count = self.asset_count()
        for subdir in self._subdirs.values():
            count += subdir.asset_count_recursive()

        return count

    def known_tags_recursive(self) -> set:
        """
        Retrieves all the tags known to the assets in this subtree.
        """
        tags = set()

        # Get the tags of the assets in this directory.
        for asset in self._assets.values():
            tags.update(asset.tags())

        # Get all the tags from the subdirectories.
        for subdir in self._subdirs.values():
            tags.update(subdir.known_tags_recursive())

        return tags

    def save(self):
        """
        Recursively saves the json file for this directory, and all subdirectories.
        Only actually updates a directory's file if any of the assets was marked as dirty.
        Only creates json files in directories with assets.
        :return:
        """
        # TODO: for some reason, when tags are added to an item in a subdirectory of this,
        #       somehow those items will also be saved in this directory. Find out why.

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

                # Save tags if there are any.
                if len(asset.tags()) > 0:
                    asset_dict[self.CFG_ASSET_TAGS] = list(asset.tags())

                assets_dict[str(asset.relative_path(self._path))] = asset_dict

            config_dict = {
                self.CFG_VERSION: self.CONFIG_VERSION,
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
                for asset_path, asset_dict in assets_dict.items():
                    absolute_path = _path.joinpath(asset_path).absolute()

                    asset_uuid = uuid.UUID(asset_dict[AssetDir.CFG_ASSET_UUID])
                    # Add tags if there are any.
                    tags = set()
                    if AssetDir.CFG_ASSET_TAGS in asset_dict:
                        for tag in asset_dict[AssetDir.CFG_ASSET_TAGS]:
                            # Tags are always lowercase.
                            tags.add(tag.lower())

                    new_asset = Asset(absolute_path, asset_uuid=asset_uuid, tags=tags)

                    assets[asset_uuid] = new_asset

                    asset_paths.append(absolute_path)
        except IOError:
            # TODO: what if we can't access the file, but we know it's there?
            #   The file not existing is not an error. Because then it is a new directory.
            pass
        except json.decoder.JSONDecodeError:
            # TODO: what do we do when a key we expect to be there is not there?
            #       Or something else went wrong?
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
                absolute_path = item.absolute()
                if absolute_path not in asset_paths:
                    # Found a new asset in this directory, that was not in the config file.
                    new_asset = Asset(absolute_path)
                    assets[new_asset.uuid()] = new_asset

        # TODO: What do we do with assets that were in the save file, but now are not?

        return AssetDir(path, subdirs, assets)
