import PyQt5.QtCore as Qcore
import PyQt5.QtWidgets as Qwidgets

import data
import widgets


class MainWindow(Qwidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.data = data.Data()

        # ---- Layout ----

        layout = Qwidgets.QHBoxLayout()
        self.setLayout(layout)

        self.setWindowTitle(self.tr("Asset Explorer"))

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

    def add_new_asset_packs(self):
        new_dirs = self.directory_explorer.get_selected_directories()

        self.data.add_asset_packs(new_dirs)
        self.directory_explorer.clear_selection()

    @Qcore.pyqtSlot()
    def on_pack_selection_changed(self):
        # Show the selected asset packs in the asset list.
        selected_packs = self.pack_list_widget.get_selected_packs()
        assets = []
        for folder in selected_packs:
            assets += self.data.get_pack(folder).get_assets()

        self.asset_list_widget.show_assets(assets)
