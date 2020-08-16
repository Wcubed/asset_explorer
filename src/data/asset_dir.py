import pathlib


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
        # Make a new dictionary, otherwise we change which assets we hold.
        assets = dict(self._assets)
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
