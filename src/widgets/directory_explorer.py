import PyQt5.QtWidgets as widgets
from PyQt5.QtCore import QDir


class DirectoryExplorer(widgets.QWidget):
    def __init__(self):
        super().__init__()

        # Start in the current application directory.
        self.current_directory = QDir.current()

        layout = widgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        row_frame = widgets.QFrame()
        row_layout = widgets.QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_frame.setLayout(row_layout)
        layout.addWidget(row_frame)

        # "Up one directory" button.
        up_dir_button = widgets.QPushButton(text="..")
        up_dir_button.setMaximumWidth(30)
        up_dir_button.clicked.connect(self.cd_up_one_directory)
        row_layout.addWidget(up_dir_button)

        # Current directory label.
        # TODO, show right aligned full path, and elipsis the left side when it doesn't fit?
        self.current_dir_label = widgets.QLabel(text="/" + self.current_directory.dirName())
        row_layout.addWidget(self.current_dir_label)

        # Show a filesystem tree with only the directories.
        self.model = widgets.QFileSystemModel()
        self.model.setRootPath(self.current_directory.absolutePath())
        self.model.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)

        self.view = widgets.QTreeView()
        self.view.setModel(self.model)
        self.view.setRootIndex(self.model.index(self.current_directory.absolutePath()))
        self.view.setExpandsOnDoubleClick(False)
        # Hide the 'type', 'size' and 'date-modified' columns.
        self.view.setColumnHidden(1, True)
        self.view.setColumnHidden(2, True)
        self.view.setColumnHidden(3, True)

        layout.addWidget(self.view)

    def cd_up_one_directory(self):
        """
        Moves the tree view up one directory.
        """
        self.current_directory.cdUp()

        # Update the UI to match.
        self.current_dir_label.setText("/" + self.current_directory.dirName())
        self.model.setRootPath(self.current_directory.absolutePath())
        self.view.setRootIndex(self.model.index(self.current_directory.absolutePath()))
