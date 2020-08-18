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

    # In milliseconds.
    AUTOSAVE_INTERVAL = 60000

    UNTAGGED_SEARCH_KEY = "UNTAGGED"
    SEARCH_BOX_MINIMUM_WIDTH = 200

    def __init__(self):
        super().__init__()

        # The application name influences where the config file is stored.
        Qcore.QCoreApplication.setApplicationName("asset_explorer")

        # pathlib.Path -> AssetDir
        self.asset_dirs = {}
        # The last directory that the file dialog was in.
        self.last_dialog_directory = pathlib.Path()

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

        # ---- Timers ----

        # Timer so we can check up on the loader every so often.
        self.async_update_timer = Qcore.QTimer()
        self.async_update_timer.setInterval(self.ASYNC_CHECK_INTERVAL)
        self.async_update_timer.timeout.connect(self.check_on_async_loader)

        # Autosave interval.
        # We save the asset info at exit, but we also want to save it regularly in between.
        # Due to the way the AssetDir saving works, only directories with changed assets will actually be saved.
        self.autosave_timer = Qcore.QTimer()
        self.autosave_timer.setInterval(self.AUTOSAVE_INTERVAL)
        # Only save the asset directories on autosave. The global config gets saved as soon as it changes.
        self.autosave_timer.timeout.connect(self.save_asset_dirs)
        self.autosave_timer.start()

        # ---- Menu ----

        add_asset_dirs_action = Qwidgets.QAction(self.tr("Add asset directories"), parent=self)
        add_asset_dirs_action.triggered.connect(self.open_directory_dialog_to_add_asset_directories)

        clear_thumbnail_cache_action = Qwidgets.QAction(self.tr("Clear thumbnail cache"), parent=self)
        clear_thumbnail_cache_action.setStatusTip(
            self.tr("Clears the thumbnail cache in memory as well as on the disk."))
        clear_thumbnail_cache_action.triggered.connect(self.clear_thumbnail_caches)

        menu = self.menuBar().addMenu(self.tr("&File"))
        menu.addAction(add_asset_dirs_action)
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

        self.asset_dir_list_widget = widgets.AssetDirListWidget(self.asset_dirs)
        self.main_splitter.addWidget(self.asset_dir_list_widget)
        # Asset table shouldn't auto stretch.
        self.main_splitter.setStretchFactor(0, 0)

        # ---- Asset list display ----

        asset_list_display = Qwidgets.QWidget()
        asset_list_display_layout = Qwidgets.QVBoxLayout()
        asset_list_display_layout.setContentsMargins(0, 0, 0, 0)
        asset_list_display.setLayout(asset_list_display_layout)
        self.main_splitter.addWidget(asset_list_display)
        self.main_splitter.setStretchFactor(1, 1)

        # Add search and tool bar.
        asset_list_bar = Qwidgets.QWidget()
        asset_list_bar_layout = Qwidgets.QHBoxLayout()
        asset_list_bar_layout.setContentsMargins(0, 0, 0, 0)
        asset_list_bar.setLayout(asset_list_bar_layout)
        asset_list_display_layout.addWidget(asset_list_bar)

        # Add simple tag search widget.
        # TODO: add new tags to this widget when they are added to the known tag list (because we added them to
        #  an asset for the first time.
        #  an asset for the first time.
        self.tag_search_box = Qwidgets.QComboBox()
        self.tag_search_box.setEditable(True)
        self.tag_search_box.setMinimumWidth(self.SEARCH_BOX_MINIMUM_WIDTH)

        # We only want to use the user input as a search option.
        # So don't auto-insert when pressing "return".
        self.tag_search_box.setInsertPolicy(Qwidgets.QComboBox.NoInsert)

        # Make sure we can search for untagged items.
        self.tag_search_box.addItem(self.UNTAGGED_SEARCH_KEY)

        # Search box starts emtpy.
        self.tag_search_box.setCurrentText("")
        asset_list_bar_layout.addWidget(self.tag_search_box)
        asset_list_bar_layout.setStretch(0, 1)

        # Add list / grid switcher button.
        self.list_grid_switch_button = Qwidgets.QPushButton(self.tr("List"))
        asset_list_bar_layout.addWidget(self.list_grid_switch_button)

        # This stack contains all the asset listing views.
        self.asset_list_display_stack = Qwidgets.QStackedWidget()
        asset_list_display_layout.addWidget(self.asset_list_display_stack)

        # The grid must be number 0 in the stack (for the switch function).
        self.asset_flow_grid = widgets.AssetFlowGridWidget()
        self.asset_list_display_stack.addWidget(self.asset_flow_grid)

        # The list must be number 1 in the stack (for the switch function).
        self.asset_list_widget = widgets.AssetListWidget()
        self.asset_list_display_stack.addWidget(self.asset_list_widget)

        # Details display
        self.asset_details_widget = widgets.AssetsDetailsWidget()
        self.main_splitter.addWidget(self.asset_details_widget)
        self.main_splitter.setStretchFactor(2, 0)

        # ---- Connections ----

        self.asset_dir_list_widget.selection_changed.connect(self.on_asset_dir_selection_changed)
        self.asset_list_widget.selection_changed.connect(self.on_asset_selection_changed)
        self.asset_flow_grid.selection_changed.connect(self.on_asset_selection_changed)
        self.list_grid_switch_button.pressed.connect(self.switch_between_grid_and_list_view)

        self.tag_search_box.activated.connect(self.on_selected_search_tag_changed)

        self.asset_details_widget.tag_display().new_tag.connect(self.user_added_new_tag)

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

    def switch_between_grid_and_list_view(self):
        if self.asset_list_display_stack.currentIndex() == 1:
            # Currently displaying the list.
            # Switch to the grid.
            self.asset_list_display_stack.setCurrentIndex(0)
            self.list_grid_switch_button.setText(self.tr("List"))
        else:
            # Currently displaying the grid.
            # Switch to the list.
            self.asset_list_display_stack.setCurrentIndex(1)
            self.list_grid_switch_button.setText(self.tr("Grid"))

    def open_directory_dialog_to_add_asset_directories(self):
        # We use a semi-custom dialog to allow selecting multiple directories.
        # See: https://stackoverflow.com/a/38255958
        dialog = Qwidgets.QFileDialog()
        # Open it where we left off.
        dialog.setDirectory(str(self.last_dialog_directory))
        dialog.setFileMode(Qwidgets.QFileDialog.DirectoryOnly)
        dialog.setOption(Qwidgets.QFileDialog.DontUseNativeDialog, True)
        dir_view = dialog.findChild(Qwidgets.QListView, 'listView')

        # Allow selecting multiple directories.
        if dir_view:
            dir_view.setSelectionMode(Qwidgets.QAbstractItemView.ExtendedSelection)

        tree_view = dialog.findChild(Qwidgets.QTreeView)
        if tree_view:
            tree_view.setSelectionMode(Qwidgets.QAbstractItemView.ExtendedSelection)

        if dialog.exec():
            # Add the selected directories.
            paths = dialog.selectedFiles()

            abs_dirs = []
            for path in paths:
                abs_dirs.append(pathlib.Path(path).absolute())
            self.add_asset_dirs(abs_dirs)

    def add_asset_dirs(self, dir_paths: [pathlib.Path]):
        # Remove duplicates from the list.
        paths = set(dir_paths)

        for dir_path in paths:
            # TODO: what if a directory is contained in one we already have, or vice-versa?
            # Check for duplicates in our directory list.
            if dir_path in self.asset_dirs.keys():
                # Duplicate!
                logging.info(self.tr("Asset dir is already loaded: \"{}\"".format(dir_path)))
                continue

            # Check for duplicates in the scanner queue, or currently active scan.
            if dir_path in self.async_loader.scan_queue() or dir_path == self.async_loader.currently_scanning():
                # Duplicate!
                logging.info(self.tr("Asset dir is already being loaded: \"{}\"".format(dir_path)))
                continue

            # Queue up the new asset directories.
            logging.info(self.tr("Queued new asset directory: \"{}\"".format(dir_path)))
            self.async_loader.queue_scan(dir_path)

        # Check up on the loading every so often.
        self.async_update_timer.start()

    @Qcore.pyqtSlot()
    def check_on_async_loader(self):
        results = self.async_loader.get_maybe_result()

        if results is not None:
            self.on_asset_dir_load_complete(results)

        # Display what is currently being worked on.
        in_progress = self.async_loader.currently_scanning()
        if in_progress is not None:
            # TODO: show it somewhere else than the status bar?
            self.statusBar().showMessage(self.tr("Loading: {}".format(in_progress)))
        else:
            self.statusBar().showMessage(self.tr("Loading complete"))
            # No need to check if nothing is happening.
            self.async_update_timer.stop()

    def on_asset_dir_load_complete(self, new_dir: AssetDir):
        """
        Call when a new asset dir has been loaded.
        :param new_dir: The new `AssetDir`
        """
        self.asset_dirs[new_dir.absolute_path()] = new_dir

        # Remember any new tags.
        self.update_known_tags(new_dir.known_tags_recursive())

        # Update the asset list.
        self.asset_dir_list_widget.on_new_asset_dir(new_dir.absolute_path())

        # If we are done loading: save the newly added asset directory / directories.
        if self.async_loader.queue_size() == 0:
            self.save_config()

    @Qcore.pyqtSlot(str)
    def user_added_new_tag(self, new_tag):
        self.update_known_tags([new_tag])

    def update_known_tags(self, new_tags):
        previous_selected_tag = self.tag_search_box.currentIndex()

        for tag in new_tags:
            if tag not in self.known_tags:
                self.tag_search_box.addItem(tag)
                self.known_tags.add(tag)

        # Update the relevant widgets.
        self.asset_details_widget.add_known_tags(self.known_tags)
        # Make sure the tag search keeps it's current item.
        self.tag_search_box.setCurrentIndex(previous_selected_tag)

    @Qcore.pyqtSlot()
    def on_selected_search_tag_changed(self):
        # When we search for tags, the selection in the asset dir list doesn't matter.
        self.asset_dir_list_widget.clear_selection()

        # Search for assets with a tag.
        search_tag = self.tag_search_box.currentText()
        if search_tag == self.UNTAGGED_SEARCH_KEY:
            search_tag = None

        # TODO: this can be more efficient.
        # Search through all the assets for the ones that have the given tag.
        filtered_assets = {}
        for asset_dir in self.asset_dirs.values():
            assets = asset_dir.assets_recursive()
            for asset in assets.values():
                # Are we looking for untagged or a specific tag?
                if search_tag is None:
                    # Looking for untagged.
                    if len(asset.tags()) == 0:
                        # Found an untagged item.
                        filtered_assets[asset.uuid()] = asset
                else:
                    # Looking for a tag.
                    if search_tag in asset.tags():
                        # Found one.
                        filtered_assets[asset.uuid()] = asset

        self.asset_list_widget.show_assets(filtered_assets)
        self.asset_flow_grid.show_assets(filtered_assets)

    @Qcore.pyqtSlot()
    def on_asset_dir_selection_changed(self):
        # Show the selected asset directories in the asset list.
        selected_dirs = self.asset_dir_list_widget.get_selected_dirs()
        assets = {}
        for asset_dir in selected_dirs:
            assets.update(asset_dir.assets_recursive())

        self.asset_list_widget.show_assets(assets)
        self.asset_flow_grid.show_assets(assets)

    @Qcore.pyqtSlot()
    def on_asset_selection_changed(self):
        assets = []
        if self.asset_list_display_stack.currentIndex() == 1:
            # Currently displaying the list.
            assets = self.asset_list_widget.get_selected_assets()
        else:
            # Currently displaying the grid.
            assets = self.asset_flow_grid.get_selected_assets()
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

        # Remember where the directory dialog left off.
        self.last_dialog_directory = config.last_directory()

        # Queue the loading of the asset directories.
        for asset_dir in config.asset_dirs():
            self.async_loader.queue_scan(asset_dir)

        # Check up on the loading every so often.
        self.async_update_timer.start()

    def save_config(self):
        # First save the program config.
        asset_dirs = list(self.asset_dirs.keys())

        # Also save asset dirs that were yet to be scanned.
        asset_dirs += self.async_loader.scan_queue()
        if self.async_loader.currently_scanning() is not None:
            asset_dirs.append(self.async_loader.currently_scanning())

        # Remember where the directory dialog left off.
        last_dir = self.last_dialog_directory

        config = data.ProgramConfig(asset_dirs, last_dir)
        data.program_config.save_program_config(config, self.config_dir)

        # And then save all the asset directory data.
        self.save_asset_dirs()

    @Qcore.pyqtSlot()
    def save_asset_dirs(self):
        logging.info(self.tr("Saving any changed asset information."))
        for asset_dir in self.asset_dirs.values():
            data.recursive_save_asset_dir(asset_dir)
