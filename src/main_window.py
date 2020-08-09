import json
import logging
import os

import PyQt5.QtCore as Qcore
import PyQt5.QtGui as Qgui
import PyQt5.QtWidgets as Qwidgets

import data
import widgets


class MainWindow(Qwidgets.QMainWindow):
    DEFAULT_WINDOW_SIZE = (1000, 800)
    CONFIG_FILE_NAME = "config.json"
    # Version number to keep track of breaking changes in config files.
    CONFIG_VERSION = 1

    # Keys for the configuration dictionary.
    CFG_KEY_VERSION = "config_version"
    CFG_KEY_PACKS = "asset_packs"
    CFG_KEY_LAST_DIRECTORY = "last_directory"

    def __init__(self):
        super().__init__()

        # The application name influences where the config file is stored.
        Qcore.QCoreApplication.setApplicationName("asset_explorer")

        self.data = data.Data()
        # Application config goes into appdata (or platform equivalent)
        # The asset pack configuration will be saved in their respective directories.
        self.config_dir = Qcore.QStandardPaths.writableLocation(Qcore.QStandardPaths.AppConfigLocation)
        self.config_file = self.config_dir + "/" + self.CONFIG_FILE_NAME

        # ---- Layout ----

        central_widget = Qwidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = Qwidgets.QHBoxLayout()
        central_widget.setLayout(layout)

        self.setWindowTitle(self.tr("Asset Explorer"))
        self.resize(self.DEFAULT_WINDOW_SIZE[0], self.DEFAULT_WINDOW_SIZE[1])

        self.main_splitter = Qwidgets.QSplitter()
        layout.addWidget(self.main_splitter)
        self.main_splitter.setHandleWidth(10)

        explorer_column = Qwidgets.QWidget()
        explorer_layout = Qwidgets.QVBoxLayout()
        explorer_layout.setContentsMargins(0, 0, 0, 0)
        explorer_column.setLayout(explorer_layout)
        self.main_splitter.addWidget(explorer_column)
        # Explorer shouldn't auto-stretch.
        self.main_splitter.setStretchFactor(0, 0)

        self.directory_explorer = widgets.FilesystemExplorer()
        explorer_layout.addWidget(self.directory_explorer)

        new_asset_dir_button = Qwidgets.QPushButton(text=self.tr("Add selected folders as packs"))
        explorer_layout.addWidget(new_asset_dir_button)

        self.pack_list_widget = widgets.PackListWidget()
        self.main_splitter.addWidget(self.pack_list_widget)
        # Asset table shouldn't auto stretch.
        self.main_splitter.setStretchFactor(1, 0)

        self.asset_list_widget = widgets.AssetListWidget()
        self.main_splitter.addWidget(self.asset_list_widget)
        self.main_splitter.setStretchFactor(2, 1)

        # ---- Connections ----

        new_asset_dir_button.clicked.connect(self.add_new_asset_packs)
        # Make sure the view updates when the data structure grows.
        self.data.pack_added.connect(self.pack_list_widget.add_pack)
        self.pack_list_widget.selection_changed.connect(self.on_pack_selection_changed)

        # ----

        self.load_config()

    def closeEvent(self, event: Qgui.QCloseEvent) -> None:
        """
        Overloaded close event.
        So we can save our current configuration, before closing.
        """
        self.save_config()

        # Close.
        event.accept()

    def add_new_asset_packs(self):
        new_dirs = self.directory_explorer.get_selected_directories()

        self.data.add_asset_packs(new_dirs)
        self.directory_explorer.clear_selection()

        # Save the newly selected asset packs.
        self.save_config()

    @Qcore.pyqtSlot()
    def on_pack_selection_changed(self):
        # Show the selected asset packs in the asset list.
        selected_packs = self.pack_list_widget.get_selected_packs()
        assets = {}
        for folder in selected_packs:
            assets.update(self.data.get_pack(folder).get_assets())

        self.asset_list_widget.show_assets(assets)

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                logging.info("Loading config from: \"{}\"".format(self.config_file))

                # TODO: What to do if loading fails?
                #       currently it will throw an exception.
                config = json.load(f)

                version = config[self.CFG_KEY_VERSION]
                # Check if we know this config version.
                if version != self.CONFIG_VERSION:
                    # TODO: what to do if the versions don't match?
                    logging.info(
                        "Unknown config version found: \'{}\', "
                        "expected: \'{}\'. Will attempt to load anyway.".format(version,
                                                                                self.CONFIG_VERSION))

                # Restore all asset packs.
                asset_packs = config[self.CFG_KEY_PACKS]
                for pack in asset_packs:
                    self.data.add_asset_pack(Qcore.QDir(pack))

                # Restore the last directory the explorer was at.
                self.directory_explorer.cd_to_directory(config[self.CFG_KEY_LAST_DIRECTORY])
        except IOError as e:
            # We could not load the file.
            # todo: show an appropriate log message for the reason.
            #       don't show a message if the file simply does not yet exist.
            logging.warning("Could not load config file: \"{}\". Reason: {}".format(self.config_file, e))

    def save_config(self):
        # TODO: save a config version number, for if we need to convert config formats.
        logging.info("Saving config to: \"{}\"".format(self.config_file))

        # Make sure the directories exist.
        if not os.path.isdir(self.config_dir):
            os.makedirs(self.config_dir)

        config = {
            self.CFG_KEY_VERSION: self.CONFIG_VERSION,
            self.CFG_KEY_PACKS: list(self.data.get_packs().keys()),
            self.CFG_KEY_LAST_DIRECTORY: self.directory_explorer.get_current_directory().absolutePath()
        }

        with open(self.config_file, 'w') as f:
            json.dump(config, f)
