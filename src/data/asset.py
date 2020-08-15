import pathlib
import uuid


class Asset:
    # All the file extensions that count as assets.
    # All lowercase.
    ASSET_EXTENSIONS = ['.png']

    def __init__(self, path, asset_uuid=None):
        self._path = pathlib.Path(path).absolute()

        self._uuid = asset_uuid
        if not self._uuid:
            # Asset was not seen before, so generate a new uuid.
            # We use uuid4 because we don't need cryptographically secure uuid's.
            # We just want a random uuid.
            self._uuid = uuid.uuid4()

    def absolute_path(self):
        """
        :return: The absolute path as a `pathlib.Path`.
        """
        return self._path

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
