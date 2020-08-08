class Data:
    def __init__(self):
        self._asset_dirs = []

    def add_asset_dir(self, new_dir: str):
        # TODO(WWE): Check if the directory is not a subdirectory of one we already have.
        #   or a duplicate directory.
        #   or a parent directory.
        #   return an exception when that happens.
        self._asset_dirs.append(new_dir)
