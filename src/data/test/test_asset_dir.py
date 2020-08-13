import os
import pathlib

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

import data


@pytest.fixture
def files_dir():
    """
    Creates a fake filesystem with the `files` directory in it, and cd's to it.
    :return:
    """
    files_dir = pathlib.Path(__file__).parent.joinpath("files")

    fs = FakeFilesystem()
    fs.add_real_directory(files_dir)
    os.chdir(files_dir)


def test_returns_absolute_path(files_dir):
    """
    Test if the a new AssetDir returns an absolute path.
    """
    unscanned_dir = pathlib.Path("unscanned_asset_dir")
    unscanned_absolute = unscanned_dir.absolute()

    asset_dir = data.AssetDir.load(unscanned_dir)

    assert asset_dir.absolute_path() == unscanned_absolute


def test_unscanned_returns_subdirs(files_dir):
    """
    Test if a new AssetDir properly lists the subdirectories that have assets
    when loading a previously unscanned directory.
    :return:
    """
    unscanned_dir = pathlib.Path("unscanned_asset_dir")
    unscanned_absolute = unscanned_dir.absolute()

    asset_dir = data.AssetDir.load(unscanned_dir)

    subdirs = asset_dir.subdirs()

    swords_dir = unscanned_absolute.joinpath("swords")
    swords_transparent = unscanned_absolute.joinpath("swords_transparent")
    swords_sources = unscanned_absolute.joinpath("swords_sources")
    empty_dir = unscanned_absolute.joinpath("empty_dir")

    assert swords_dir in subdirs
    assert swords_transparent in subdirs

    # Directories with no assets should not be listed.
    assert swords_sources not in subdirs
    assert empty_dir not in subdirs

# TODO: test if it loaded the assets.
# TODO: test recursive load.
