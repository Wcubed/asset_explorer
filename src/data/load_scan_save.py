import json
import logging
import pathlib
import uuid

from data import AssetDir, Asset

CONFIG_FILE_NAME = ".asset_dir.json"
# For keeping track of breaking changes.
CONFIG_VERSION = 1

# Asset dir config keys.
CFG_VERSION = "version"
# Asset config keys.
CFG_ASSETS = "assets"
CFG_ASSET_UUID = "uuid"
CFG_ASSET_TAGS = "tags"


def recursive_load_asset_dir(path) -> AssetDir:
    """
    Loads an AssetDir from the given path.
    When a config file exists, it will attempt to load that first, and then scan the directory for any new
    assets.
    # TODO: also scan for assets that we have seen, but are no longer there.
    """

    _path = pathlib.Path(path)

    assets = {}
    # Keep track of which asset paths we already know of.
    asset_paths = []
    try:
        with open(_path.joinpath(CONFIG_FILE_NAME), 'r') as f:
            config = json.load(f)

            if config[CFG_VERSION] != CONFIG_VERSION:
                # TODO: what to do if the config version does not match.
                pass

            assets_dict = config[CFG_ASSETS]

            # Load all the assets from the file.
            for asset_path, asset_dict in assets_dict.items():
                # First, check if the asset path only consists of a file name.
                if str(pathlib.Path(asset_path).parent) != ".":
                    # The asset is not immediately in this directory.
                    # Ignore it, it will be listed in it's containing directory's config file.
                    logging.debug(
                        "Asset in config is not in this directory. Ignoring it. (\"{}\" is not in \"{}\").".format(
                            asset_path,
                            _path))
                    continue

                absolute_path = _path.joinpath(asset_path).absolute()

                asset_uuid = uuid.UUID(asset_dict[CFG_ASSET_UUID])
                # Add tags if there are any.
                tags = set()
                if CFG_ASSET_TAGS in asset_dict:
                    for tag in asset_dict[CFG_ASSET_TAGS]:
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
            new_subdir = recursive_load_asset_dir(item)

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


def recursive_save_asset_dir(asset_dir: AssetDir):
    """
    Recursively saves the json file for the given AssetDir, and all subdirectories.
    Only actually updates a directory's file if any of the assets was marked as dirty.
    Only creates json files in directories with assets.
    :return:
    """

    # Are any assets dirty? Then we save this directory.
    save = False
    for asset in asset_dir.assets().values():
        if asset.is_dirty():
            save = True
            break

    if save:
        assets_dict = {}
        for asset in asset_dir.assets().values():
            asset_dict = {
                CFG_ASSET_UUID: str(asset.uuid()),
            }

            # Save tags if there are any.
            if len(asset.tags()) > 0:
                asset_dict[CFG_ASSET_TAGS] = list(asset.tags())

            assets_dict[str(asset.relative_path(asset_dir.absolute_path()))] = asset_dict

        config_dict = {
            CFG_VERSION: CONFIG_VERSION,
            CFG_ASSETS: assets_dict,
        }

        with open(asset_dir.absolute_path().joinpath(CONFIG_FILE_NAME), 'w') as f:
            json.dump(config_dict, f)

    # Always check the subdirectories.
    for subdir in asset_dir.subdirs().values():
        recursive_save_asset_dir(subdir)
