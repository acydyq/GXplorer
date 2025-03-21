import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QComboBox, QLineEdit, QPushButton,
    QFileSystemModel, QMessageBox
)
from PyQt5.QtCore import Qt, QItemSelectionModel, QSortFilterProxyModel

class CustomTreeView(QTreeView):
    """Custom tree view with right-click and space bar selection functionality."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSelectionMode(QTreeView.ExtendedSelection)  # Allow multiple selections
        self.setSelectionBehavior(QTreeView.SelectRows)  # Ensure full-row selection
        self.persistent_selection = set()  # Track selections

        # Custom selection styling
        self.setStyleSheet("""
            QTreeView::item:selected {
                background-color: white;
                color: black;
            }
        """)

    def contextMenuEvent(self, event):
        """Right-click to add/remove item from selection."""
        index = self.indexAt(event.pos())
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

    def keyPressEvent(self, event):
        """Pressing space bar adds/removes an item from selection."""
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
        else:
            super().keyPressEvent(event)

    def focusInEvent(self, event):
        """Update the last active panel when this pane gains focus."""
        super().focusInEvent(event)
        main_window = self.parent().main_window
        main_window.last_active_panel = self.parent()  # Set to this panel
        # Clear selection of the opposite pane
        if self is main_window.left_panel.tree:
            main_window.right_panel.tree.clear_selection()
        else:
            main_window.left_panel.tree.clear_selection()

    def clear_selection(self):
        """Clears selection when navigating away or switching panes."""
        self.persistent_selection.clear()
        self.selectionModel().clearSelection()
        self.viewport().update()

    def restore_selection(self):
        """Restore persistent selections when navigating directories."""
        sm = self.selectionModel()
        for index in self.persistent_selection:
            if index.isValid():
                sm.select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        self.viewport().update()

class FileExplorerPanel(QWidget):
    """File explorer panel with persistent selection for right-clicked and space-bar items."""
    def __init__(self, start_path, main_window):
        super().__init__()
        self.main_window = main_window  # Reference to main window
        self.current_path = start_path
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Drive Combo Box
        self.drive_combo = QComboBox()
        self.drive_combo.setFocusPolicy(Qt.NoFocus)
        import string
        drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
        self.drive_combo.addItems(drives)
        self.drive_combo.currentIndexChanged.connect(self.on_drive_changed)

        # Path Input and Search
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(self.current_path)
        self.path_edit.setFocusPolicy(Qt.NoFocus)
        self.path_edit.returnPressed.connect(self.on_path_entered)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search...")
        self.search_edit.textChanged.connect(self.on_search_changed)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.search_edit)

        # Go and Up Buttons
        self.go_button = QPushButton("Go")
        self.go_button.setFocusPolicy(Qt.NoFocus)
        self.go_button.clicked.connect(self.on_path_entered)
        self.up_button = QPushButton("Up")
        self.up_button.setFocusPolicy(Qt.NoFocus)
        self.up_button.clicked.connect(self.go_up)

        # Layout for Controls
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.drive_combo)
        top_layout.addLayout(path_layout)
        top_layout.addWidget(self.go_button)
        top_layout.addWidget(self.up_button)
        layout.addLayout(top_layout)

        # Tree View with Selection Memory
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.tree = CustomTreeView(self)
        self.tree.setModel(self.proxy_model)
        self.tree.setRootIndex(self.proxy_model.mapFromSource(self.model.index(self.current_path)))
        self.tree.setColumnWidth(0, 300)
        self.tree.setSortingEnabled(True)
        layout.addWidget(self.tree)
        self.setLayout(layout)

    def on_drive_changed(self, index):
        """Handles drive selection."""
        drive = self.drive_combo.itemText(index)
        self.navigate_to_path(drive)

    def on_path_entered(self):
        """Handles path input changes."""
        path = self.path_edit.text()
        self.navigate_to_path(path)

    def go_up(self):
        """Navigates up one directory level."""
        parent_dir = os.path.dirname(self.current_path)
        if parent_dir:
            self.navigate_to_path(parent_dir)

    def navigate_to_path(self, path):
        """Changes directory in the file explorer."""
        if os.path.exists(path):
            self.current_path = path
            self.path_edit.setText(path)
            source_index = self.model.index(path)
            proxy_index = self.proxy_model.mapFromSource(source_index)
            self.tree.setRootIndex(proxy_index)
            self.tree.restore_selection()  # Restore right-click and space-bar selections

    def on_search_changed(self, text):
        """Filters the displayed files based on search input."""
        self.proxy_model.setFilterFixedString(text)

    def set_focus_to_first_item(self):
        """Sets focus to the first file in the directory."""
        def try_set_focus():
            first_index = self.proxy_model.index(0, 0, self.tree.rootIndex())
            if first_index.isValid():
                self.tree.setCurrentIndex(first_index)
                self.tree.setFocus(Qt.OtherFocusReason)
            else:
                self.model.directoryLoaded.connect(lambda p: try_set_focus())
        try_set_focus()