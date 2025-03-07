import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QComboBox, QLineEdit, QPushButton,
    QFileSystemModel, QMenu, QMessageBox
)
from PyQt5.QtCore import Qt, QItemSelectionModel, QSortFilterProxyModel

# Custom tree view with persistent selection (styling removed)
class CustomTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSelectionMode(QTreeView.ExtendedSelection)  # Allow multiple selections
        self.setSelectionBehavior(QTreeView.SelectRows)     # Ensure full-row selection
        self.persistent_selection = set()                   # Track selections

    def keyPressEvent(self, event):
        """Toggle selection with space bar without affecting focus."""
        if event.key() == Qt.Key_Space:
            index = self.currentIndex()
            if index.isValid():
                sm = self.selectionModel()
                if sm.isSelected(index):
                    sm.select(index, QItemSelectionModel.Deselect | QItemSelectionModel.Rows)
                    self.persistent_selection.discard(index)
                else:
                    sm.select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
                    self.persistent_selection.add(index)
                self.viewport().update()
                event.accept()
            # Do NOT call super() to preserve currentIndex (focus)
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Support right-click selection toggling."""
        index = self.indexAt(event.pos())
        if event.button() == Qt.RightButton and index.isValid():
            sm = self.selectionModel()
            if sm.isSelected(index):
                sm.select(index, QItemSelectionModel.Deselect | QItemSelectionModel.Rows)
                self.persistent_selection.discard(index)
            else:
                sm.select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
                self.persistent_selection.add(index)
            self.viewport().update()
            event.accept()
        else:
            super().mousePressEvent(event)

    def focusOutEvent(self, event):
        """Maintain selection when focus leaves the widget."""
        self.restore_selection()
        super().focusOutEvent(event)

    def restore_selection(self):
        """Restore persistent selections."""
        sm = self.selectionModel()
        for index in self.persistent_selection:
            if index.isValid():  # Check validity to avoid stale indices
                sm.select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        self.viewport().update()

# File explorer panel with standard styling
class FileExplorerPanel(QWidget):
    def __init__(self, start_path):
        super().__init__()
        self.current_path = start_path
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Drive combo box
        self.drive_combo = QComboBox()
        self.drive_combo.setFocusPolicy(Qt.NoFocus)
        import string
        drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
        self.drive_combo.addItems(drives)
        self.drive_combo.currentIndexChanged.connect(self.on_drive_changed)

        # Path edit and search
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(self.current_path)
        self.path_edit.setFocusPolicy(Qt.NoFocus)
        self.path_edit.returnPressed.connect(self.on_path_entered)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search...")
        self.search_edit.textChanged.connect(self.on_search_changed)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.search_edit)

        # Go and Up buttons
        self.go_button = QPushButton("Go")
        self.go_button.setFocusPolicy(Qt.NoFocus)
        self.go_button.clicked.connect(self.on_path_entered)
        self.up_button = QPushButton("Up")
        self.up_button.setFocusPolicy(Qt.NoFocus)
        self.up_button.clicked.connect(self.go_up)

        # Layout for controls
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.drive_combo)
        top_layout.addLayout(path_layout)
        top_layout.addWidget(self.go_button)
        top_layout.addWidget(self.up_button)
        layout.addLayout(top_layout)

        # Tree view with standard model
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterKeyColumn(0)  # Filter on the name column
        self.tree = CustomTreeView()
        self.tree.setModel(self.proxy_model)
        self.tree.setRootIndex(self.proxy_model.mapFromSource(self.model.index(self.current_path)))
        self.tree.setColumnWidth(0, 300)
        self.tree.setSortingEnabled(True)
        layout.addWidget(self.tree)
        self.setLayout(layout)
        self.tree.setFocus()  # Ensure tree gets key events

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
            source_index = self.model.index(path)
            proxy_index = self.proxy_model.mapFromSource(source_index)
            self.tree.setRootIndex(proxy_index)

    def on_search_changed(self, text):
        self.proxy_model.setFilterFixedString(text)

    def set_focus_to_first_item(self):
        def try_set_focus():
            first_index = self.proxy_model.index(0, 0, self.tree.rootIndex())
            if first_index.isValid():
                self.tree.setCurrentIndex(first_index)
                self.tree.setFocus(Qt.OtherFocusReason)
            else:
                self.model.directoryLoaded.connect(lambda p: try_set_focus())
        try_set_focus()