import json
import logging
import pathlib

CONFIG_FILE_NAME = "config.json"
# Version number to keep track of breaking changes in config files.
CONFIG_VERSION = 1

# Keys for the configuration dictionary.
CFG_KEY_VERSION = "version"
CFG_KEY_ASSET_DIRS = "asset_dirs"
CFG_KEY_LAST_DIRECTORY = "last_directory"


class ProgramConfig:
    def __init__(self, asset_dirs=None, last_directory=""):
        if asset_dirs is None:
            asset_dirs = []

        self._asset_dirs = list(asset_dirs)
        self._last_directory = pathlib.Path(last_directory)

    def set_asset_dirs(self, asset_dirs):
        """
        :param asset_dirs: Paths of the asset directories.
        :return:
        """
        self._asset_dirs = list(asset_dirs)

    def asset_dirs(self):
        return self._asset_dirs

    def last_directory(self):
        return self._last_directory

    def set_last_directory(self, new_dir):
        self._last_directory = pathlib.Path(new_dir)


def load_program_config(directory):
    """
    Will attempt to load the config file from the given directory.
    :param directory: The directory to load the file from.
    :return: `ProgramConfig` when successful, `None` when something went wrong.
    # TODO: do we want to throw an exception instead?
    """

    file_path = pathlib.Path(directory).joinpath(CONFIG_FILE_NAME)

    try:
        with open(file_path, 'r') as f:
            logging.info("Loading config from: \"{}\"".format(file_path))

            # TODO: What to do if loading fails?
            #       currently it will throw an exception.
            config = json.load(f)

            version = config[CFG_KEY_VERSION]
            # Check if we know this config version.
            if version != CONFIG_VERSION:
                # TODO: what to do if the versions don't match?
                logging.info(
                    "Unknown config version found: \'{}\', "
                    "expected: \'{}\'. Will attempt to load anyway.".format(version,
                                                                            CONFIG_VERSION))

            # Load the last directory the explorer was at.
            last_directory = config[CFG_KEY_LAST_DIRECTORY]

            # Load all asset directories.
            asset_dirs = config[CFG_KEY_ASSET_DIRS]

            return ProgramConfig(asset_dirs, last_directory)
    except IOError as e:
        # We could not load the file.
        # todo: show an appropriate log message for the reason.
        #       don't show a message if the file simply does not yet exist.
        logging.warning("Could not load config file: \"{}\". Reason: {}".format(file_path, e))
        return None
    except json.decoder.JSONDecodeError as e:
        logging.warning("Could not load config file: \"{}\". Reason: {}".format(file_path, e))
        return None


def save_program_config(config: ProgramConfig, directory):
    """
    Saves the given config to the provided directory.
    :param config:
    :param directory:
    :return:
    """
    directory_path = pathlib.Path(directory)
    file_path = directory_path.joinpath(CONFIG_FILE_NAME)

    logging.info("Saving config to: \"{}\"".format(file_path))

    # Make sure the directories exist.
    if not directory_path.is_dir():
        directory_path.mkdir(parents=True)

    # pathlib.Path is not json serializable,
    # so we convert them to strings.
    asset_dir_paths = []
    for asset_dir in config.asset_dirs():
        asset_dir_paths.append(str(asset_dir))
    last_dir = str(config.last_directory())

    config = {
        CFG_KEY_VERSION: CONFIG_VERSION,
        CFG_KEY_ASSET_DIRS: asset_dir_paths,
        CFG_KEY_LAST_DIRECTORY: last_dir
    }

    with open(file_path, 'w') as f:
        json.dump(config, f)
