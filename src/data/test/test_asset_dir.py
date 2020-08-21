import os
import pathlib

import pytest

import data

UNSCANNED_DIR = "unscanned_asset_dir"
SWORDS_DIR = "unscanned_asset_dir/swords"


@pytest.fixture
def files_dir(fs):
    """
    Creates a fake filesystem with the `files` directory in it, and cd's into it.
    :return:
    """
    files_dir = pathlib.Path(__file__).parent.joinpath("files")

    fs.add_real_directory(files_dir)
    os.chdir(files_dir)

    return fs


def test_returns_absolute_path(files_dir):
    """
    Test if the a new AssetDir returns an absolute path.
    """
    unscanned_dir = pathlib.Path(UNSCANNED_DIR)
    unscanned_absolute = unscanned_dir.absolute()

    asset_dir = data.recursive_load_asset_dir(unscanned_dir)

    assert asset_dir.absolute_path() == unscanned_absolute


def test_unscanned_finds_correct_subdirs(files_dir):
    """
    Test if a new AssetDir properly lists the subdirectories that have assets
    when loading a previously unscanned directory.
    """
    unscanned_dir = pathlib.Path(UNSCANNED_DIR)

    asset_dir = data.recursive_load_asset_dir(unscanned_dir)

    subdirs = asset_dir.subdirs().keys()

    # Directories with assets should be listed.
    swords_dir = pathlib.Path("swords")
    swords_transparent = pathlib.Path("swords_transparent")
    assert swords_dir in subdirs
    assert swords_transparent in subdirs

    # Directories that have assets somewhere in their directory tree should be listed.
    deep_nested_assets = pathlib.Path("deep_nested_assets")
    assert deep_nested_assets in subdirs

    # Directories with no assets should not be listed.
    swords_sources = pathlib.Path("swords_sources")
    empty_dir = pathlib.Path("empty_dir")
    non_assets = pathlib.Path("non_assets")
    assert swords_sources not in subdirs
    assert empty_dir not in subdirs
    assert non_assets not in subdirs

    # Directories that have subdirectories, but there are no assets anywhere in them,
    # should not be listed.
    dir_with_empty_subdirs = pathlib.Path("dir_with_emtpy_subdirs")
    assert dir_with_empty_subdirs not in subdirs


def test_unscanned_find_assets(files_dir):
    """
    Test if the AssetDir properly lists the assets in a directory.
    """
    swords_dir = pathlib.Path(SWORDS_DIR)
    asset_dir = data.recursive_load_asset_dir(swords_dir)

    expected_assets = ["square_crossed.png", "tall.png", "wide.png"]

    assert asset_dir.asset_count() == len(expected_assets)

    found_assets = []
    for asset in asset_dir.assets().values():
        relative_path = asset.relative_path(asset_dir.absolute_path())
        found_assets.append(str(relative_path))

        # Asset is new, so it should be marked as dirty.
        assert asset.is_dirty()

    for expected_asset in expected_assets:
        assert expected_asset in found_assets


def test_assets_recursive(files_dir):
    """
    Test if the `all_assets_recursive()` function returns the correct amount of assets.
    """
    unscanned_dir = pathlib.Path(UNSCANNED_DIR)
    asset_dir = data.recursive_load_asset_dir(unscanned_dir)

    assert asset_dir.asset_count_recursive() == 7


def test_unscanned_save_creates_file(files_dir):
    """
    Test if the AssetDir saves a config file when scanning and saving an unscanned directory.
    """
    swords_dir = pathlib.Path(SWORDS_DIR)
    asset_dir = data.recursive_load_asset_dir(swords_dir)

    data.recursive_save_asset_dir(asset_dir)

    # Check if the file got saved.
    config_file = swords_dir.joinpath(data.load_scan_save.CONFIG_FILE_NAME)
    assert config_file.is_file()


def test_save_and_load(files_dir):
    """
    Checks if saving and then loading an asset dir will have the assets marked as clean.
    """
    swords_dir = pathlib.Path(SWORDS_DIR)
    asset_dir = data.recursive_load_asset_dir(swords_dir)

    data.recursive_save_asset_dir(asset_dir)

    from_file = data.recursive_load_asset_dir(swords_dir)

    assert from_file.asset_count() == 3

    # The assets should now not be dirty, as we loaded them from the config file.
    for asset in from_file.assets().values():
        assert not asset.is_dirty()

# TODO test recursive loading.
