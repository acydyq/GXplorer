import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QComboBox, QLineEdit, QPushButton,
    QFileSystemModel, QMessageBox
)
from PyQt5.QtCore import Qt, QSortFilterProxyModel

class FileExplorerPanel(QWidget):
    def __init__(self, start_path):
        super().__init__()
        self.current_path = start_path
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Drive Selector
        self.drive_combo = QComboBox()
        self.drive_combo.addItems(self.get_available_drives())
        self.drive_combo.currentIndexChanged.connect(self.on_drive_changed)

        # Path Input & Search
        self.path_edit = QLineEdit(self.current_path)
        self.path_edit.returnPressed.connect(self.on_path_entered)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search...")
        self.search_edit.textChanged.connect(self.on_search_changed)

        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.on_path_entered)
        self.up_button = QPushButton("Up")
        self.up_button.clicked.connect(self.go_up)

        layout.addWidget(self.drive_combo)
        layout.addWidget(self.path_edit)
        layout.addWidget(self.search_edit)
        layout.addWidget(self.go_button)
        layout.addWidget(self.up_button)

        # File Browser
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.tree = QTreeView()
        self.tree.setModel(self.proxy_model)
        self.tree.setRootIndex(self.proxy_model.mapFromSource(self.model.index(self.current_path)))
        self.tree.setSortingEnabled(True)

        layout.addWidget(self.tree)
        self.setLayout(layout)

    def get_available_drives(self):
        import string
        return [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]

    def on_drive_changed(self, index):
        drive = self.drive_combo.itemText(index)
        self.navigate_to_path(drive)

    def on_path_entered(self):
        path = self.path_edit.text()
        self.navigate_to_path(path)

    def go_up(self):
        parent_dir = os.path.dirname(self.current_path)
        if parent_dir:
            self.navigate_to_path(parent_dir)

    def navigate_to_path(self, path):
        if os.path.exists(path):
            self.current_path = path
            self.path_edit.setText(path)
            self.tree.setRootIndex(self.proxy_model.mapFromSource(self.model.index(path)))

    def on_search_changed(self, text):
        self.proxy_model.setFilterFixedString(text)

    def refresh(self):
        self.navigate_to_path(self.current_path)
