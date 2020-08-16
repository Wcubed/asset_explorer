import json
import logging
import os
import pathlib
from concurrent import futures

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

    # How large can the pixmap cache grow? In Mb.
    PIXMAP_MEMORY_CACHE_LIMIT = 200

    # Keys for the configuration dictionary.
    CFG_KEY_VERSION = "version"
    CFG_KEY_ASSET_DIRS = "asset_dirs"
    CFG_KEY_LAST_DIRECTORY = "last_directory"

    def __init__(self):
        super().__init__()

        # The application name influences where the config file is stored.
        Qcore.QCoreApplication.setApplicationName("asset_explorer")

        # pathlib.Path -> AssetDir
        self.asset_dirs = {}

        self.known_tags = set()

        # Application config goes into appdata (or platform equivalent)
        # The asset pack configuration will be saved in their respective directories.
        self.config_dir = Qcore.QStandardPaths.writableLocation(Qcore.QStandardPaths.AppConfigLocation)
        self.config_file = self.config_dir + "/" + self.CONFIG_FILE_NAME

        # Separate thread to load asset directories with.
        self.asset_dir_load_thread = futures.ThreadPoolExecutor()

        # Set a nice high in-memory cache limit for our asset thumbnails.
        # Is in Kb.
        Qgui.QPixmapCache.setCacheLimit(self.PIXMAP_MEMORY_CACHE_LIMIT * 1024)

        # Make sure the on-file thumbnail cache exists.
        cache_dir = Qcore.QStandardPaths.writableLocation(Qcore.QStandardPaths.CacheLocation)
        if not os.path.isdir(cache_dir):
            os.makedirs(cache_dir)

        # ---- Menu ----

        clear_thumbnail_cache_action = Qwidgets.QAction(self.tr("Clear thumbnail cache"), parent=self)
        clear_thumbnail_cache_action.setStatusTip(
            self.tr("Clears the thumbnail cache in memory as well as on the disk."))
        clear_thumbnail_cache_action.triggered.connect(self.clear_thumbnail_caches)

        menu = self.menuBar().addMenu(self.tr("&File"))
        menu.addAction(clear_thumbnail_cache_action)

        # ---- Layout ----

        # Enable the status bar.
        self.statusBar().showMessage("")

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

        new_asset_dir_button = Qwidgets.QPushButton(text=self.tr("Add selected folders"))
        explorer_layout.addWidget(new_asset_dir_button)

        self.asset_dir_list_widget = widgets.AssetDirListWidget(self.asset_dirs)
        self.main_splitter.addWidget(self.asset_dir_list_widget)
        # Asset table shouldn't auto stretch.
        self.main_splitter.setStretchFactor(1, 0)

        self.asset_list_widget = widgets.AssetListWidget()
        self.main_splitter.addWidget(self.asset_list_widget)
        self.main_splitter.setStretchFactor(2, 0)

        # This is for testing the flow grid.
        self.asset_flow_grid = widgets.AssetFlowGridWidget()
        self.main_splitter.addWidget(self.asset_flow_grid)
        self.main_splitter.setStretchFactor(3, 1)

        # Details display
        self.asset_details_widget = widgets.AssetsDetailsWidget()
        self.main_splitter.addWidget(self.asset_details_widget)
        self.main_splitter.setStretchFactor(4, 0)

        # ---- Connections ----

        new_asset_dir_button.clicked.connect(self.add_selected_asset_dirs)
        self.asset_dir_list_widget.selection_changed.connect(self.on_asset_dir_selection_changed)
        self.asset_list_widget.selection_changed.connect(self.on_asset_selection_changed)

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

    def add_selected_asset_dirs(self):
        new_dirs = self.directory_explorer.get_selected_directories()
        abs_dirs = []
        for new_dir in new_dirs:
            abs_dirs.append(pathlib.Path(new_dir.absolutePath()))

        self.add_asset_dirs(abs_dirs)

    def add_asset_dirs(self, dir_paths):
        new_abs_paths = []
        for dir_path in dir_paths:
            # TODO: what if there are duplicates?
            #       or a directory is contained in one we already have, or vice-versa?
            new_asset_dir = data.recursive_load_asset_dir(dir_path)
            self.asset_dirs[new_asset_dir.absolute_path()] = new_asset_dir
            new_abs_paths.append(new_asset_dir.absolute_path())

            # Retrieve any new tags.
            self.known_tags.update(new_asset_dir.known_tags_recursive())

        self.directory_explorer.clear_selection()

        # Save the newly added asset directories.
        self.save_config()

        # Update the asset list.
        for abs_path in new_abs_paths:
            self.asset_dir_list_widget.on_new_asset_dir(abs_path)

        # Update the relevant widgets.
        self.asset_details_widget.add_known_tags(self.known_tags)

    @Qcore.pyqtSlot()
    def on_asset_dir_selection_changed(self):
        # Show the selected asset directories in the asset list.
        selected_dirs = self.asset_dir_list_widget.get_selected_dirs()
        assets = {}
        for asset_dir in selected_dirs:
            assets.update(asset_dir.assets_recursive())

        self.asset_list_widget.show_assets(assets)

        # Testing for the asset flow grid.
        self.asset_flow_grid.show_assets(assets)

    @Qcore.pyqtSlot()
    def on_asset_selection_changed(self):
        assets = self.asset_list_widget.get_selected_assets()
        self.asset_details_widget.show_assets(assets)

    def on_packs_removed(self):
        self.save_config()

    @Qcore.pyqtSlot()
    def clear_thumbnail_caches(self):
        logging.info(self.tr("Clearing thumbnail caches."))

        # Clear the memory cache.
        Qgui.QPixmapCache.clear()

        # Clear the file cache.
        cache_dir = Qcore.QDir(Qcore.QStandardPaths.writableLocation(Qcore.QStandardPaths.CacheLocation))
        cache_dir.removeRecursively()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                logging.info(self.tr("Loading config from: \"{}\"").format(self.config_file))

                # TODO: What to do if loading fails?
                #       currently it will throw an exception.
                config = json.load(f)

                version = config[self.CFG_KEY_VERSION]
                # Check if we know this config version.
                if version != self.CONFIG_VERSION:
                    # TODO: what to do if the versions don't match?
                    logging.info(self.tr(
                        "Unknown config version found: \'{}\', "
                        "expected: \'{}\'. Will attempt to load anyway.").format(version,
                                                                                 self.CONFIG_VERSION))

                # Restore the last directory the explorer was at.
                self.directory_explorer.cd_to_directory(config[self.CFG_KEY_LAST_DIRECTORY])

                # Restore all asset directories.
                asset_dirs = config[self.CFG_KEY_ASSET_DIRS]
                self.add_asset_dirs(asset_dirs)
        except IOError as e:
            # We could not load the file.
            # todo: show an appropriate log message for the reason.
            #       don't show a message if the file simply does not yet exist.
            logging.warning(self.tr("Could not load config file: \"{}\". Reason: {}").format(self.config_file, e))

        # Retrieve all the known tags.
        for asset_dir in self.asset_dirs.values():
            self.known_tags.update(asset_dir.known_tags_recursive())
        self.asset_details_widget.add_known_tags(self.known_tags)

    def save_config(self):
        # TODO: save a config version number, for if we need to convert config formats.
        logging.info(self.tr("Saving config to: \"{}\"").format(self.config_file))

        # Make sure the directories exist.
        if not os.path.isdir(self.config_dir):
            os.makedirs(self.config_dir)

        # Save the individual asset directories.
        asset_dir_paths = []
        for asset_dir in self.asset_dirs.values():
            data.recursive_save_asset_dir(asset_dir)
            asset_dir_paths.append(str(asset_dir.absolute_path()))

        config = {
            self.CFG_KEY_VERSION: self.CONFIG_VERSION,
            self.CFG_KEY_ASSET_DIRS: asset_dir_paths,
            self.CFG_KEY_LAST_DIRECTORY: self.directory_explorer.get_current_directory().absolutePath()
        }

        with open(self.config_file, 'w') as f:
            json.dump(config, f)
