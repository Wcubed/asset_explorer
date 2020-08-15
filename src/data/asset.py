import pathlib
import uuid


class Asset:
    # All the file extensions that count as assets.
    # All lowercase.
    ASSET_EXTENSIONS = ['.png']

    def __init__(self, path, asset_uuid=None):
        self._path = pathlib.Path(path).absolute()

        self._uuid = asset_uuid
        self._dirty = False

        if not self._uuid:
            # Asset was not seen before, so generate a new uuid.
            # We use uuid4 because we don't need cryptographically secure uuid's.
            # We just want a random uuid.
            self._uuid = uuid.uuid4()
            self._dirty = True

    def is_dirty(self):
        """
        And asset is dirty if it has been updated since the last save.
        :return:
        """
        return self._dirty

    def was_saved(self):
        """
        Call after saving the asset. Marks it as clean again.
        """
        self._dirty = False

    def absolute_path(self):
        """
        :return: The absolute path as a `pathlib.Path`.
        """
        return self._path

    def relative_path(self, relative_to: pathlib.Path):
        return self._path.relative_to(relative_to)

    def uuid(self):
        """
        :return: The unique uuid of this asset.
        """
        return self._uuid

    @staticmethod
    def is_asset(path) -> bool:
        """
        :param path: The path to check.
        :return: True if the path is an asset, false if not.
        """
        _path = pathlib.Path(path)
        return _path.is_file() and _path.suffix in Asset.ASSET_EXTENSIONS
