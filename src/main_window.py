import logging
import os
import pathlib

import PyQt5.QtCore as Qcore
import PyQt5.QtGui as Qgui
import PyQt5.QtWidgets as Qwidgets

import data
import widgets
from data import AssetDir


class MainWindow(Qwidgets.QMainWindow):
    DEFAULT_WINDOW_SIZE = (1000, 800)

    # How large can the pixmap cache grow? In Mb.
    PIXMAP_MEMORY_CACHE_LIMIT = 200

    # How often should we check up on our async loader?
    # In milliseconds.
    ASYNC_CHECK_INTERVAL = 200

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

        # Set a nice high in-memory cache limit for our asset thumbnails.
        # Is in Kb.
        Qgui.QPixmapCache.setCacheLimit(self.PIXMAP_MEMORY_CACHE_LIMIT * 1024)

        # Make sure the on-file thumbnail cache exists.
        cache_dir = Qcore.QStandardPaths.writableLocation(Qcore.QStandardPaths.CacheLocation)
        if not os.path.isdir(cache_dir):
            os.makedirs(cache_dir)

        self.async_loader = data.AsyncLoader()
        # Timer so we can check up on the loader every so often.
        self.async_update_timer = Qcore.QTimer()
        self.async_update_timer.setInterval(self.ASYNC_CHECK_INTERVAL)
        self.async_update_timer.timeout.connect(self.check_on_async_loader)

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
        for dir_path in dir_paths:
            # TODO: what if there are duplicates?
            #       or a directory is contained in one we already have, or vice-versa?
            # Queue up the new asset directories.
            logging.info(self.tr("Queued scan: \"{}\"".format(dir_path)))
            self.async_loader.queue_scan(dir_path)

        # Check up on the loading every so often.
        self.async_update_timer.start()

        self.directory_explorer.clear_selection()

    @Qcore.pyqtSlot()
    def check_on_async_loader(self):
        results = self.async_loader.get_maybe_result()

        if results is not None:
            self.on_asset_dir_load_complete(results)

        # Display what is currently being worked on.
        in_progress = self.async_loader.currently_scanning()
        if in_progress is not None:
            # TODO: show it somewhere else than the status bar?
            self.statusBar().showMessage(self.tr("Scanning: {}".format(in_progress)))
        else:
            self.statusBar().clearMessage()
            # No need to check if nothing is happening.
            self.async_update_timer.stop()

    def on_asset_dir_load_complete(self, new_dir: AssetDir):
        """
        Call when a new asset dir has been loaded.
        :param new_dir: The new `AssetDir`
        """
        self.asset_dirs[new_dir.absolute_path()] = new_dir

        # Remember any new tags.
        self.known_tags.update(new_dir.known_tags_recursive())

        # Save the newly added asset directory.
        self.save_config()

        # Update the asset list.
        self.asset_dir_list_widget.on_new_asset_dir(new_dir.absolute_path())

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
        config = data.program_config.load_program_config(self.config_dir)

        if config is None:
            # Config could not be loaded.
            # Create a default config.
            config = data.ProgramConfig()

        self.directory_explorer.cd_to_directory(config.last_directory())

        # Queue the loading of the asset directories.
        for asset_dir in config.asset_dirs():
            self.async_loader.queue_scan(asset_dir)

        # Check up on the loading every so often.
        self.async_update_timer.start()

    def save_config(self):
        # First save the program config.
        asset_dirs = self.asset_dirs.keys()
        last_dir = self.directory_explorer.get_current_directory().absolutePath()

        config = data.ProgramConfig(asset_dirs, last_dir)
        data.program_config.save_program_config(config, self.config_dir)

        # And then save all the asset directory data.
        for asset_dir in self.asset_dirs.values():
            data.recursive_save_asset_dir(asset_dir)
