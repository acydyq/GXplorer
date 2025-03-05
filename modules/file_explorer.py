import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QComboBox, QLineEdit, QPushButton,
    QFileSystemModel, QStyledItemDelegate, QStyleOptionViewItem, QStyle, QMenu, QMessageBox
)
from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtGui import QColor, QBrush, QPainter

# Custom delegate to force correct focus and selection rendering.
class CustomItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        """Custom paint function to force correct colors for focus and selection."""
        view = option.widget  # The QTreeView
        selection_model = view.selectionModel()

        # Determine focus and selection state
        is_focused = view.currentIndex().row() == index.row()
        is_selected = selection_model.isSelected(index) if selection_model else False

        new_option = QStyleOptionViewItem(option)

        # 1. If both Focused & Selected → Red text on Cyan Background
        if is_focused and is_selected:
            painter.fillRect(option.rect, QColor("cyan"))
            new_option.palette.setColor(new_option.palette.Text, QColor("red"))

        # 2. If only Focused → Black text on Cyan Background
        elif is_focused:
            painter.fillRect(option.rect, QColor("cyan"))
            new_option.palette.setColor(new_option.palette.Text, QColor("black"))

        # 3. If only Selected → Black text on Red Background
        elif is_selected:
            painter.fillRect(option.rect, QColor("red"))
            new_option.palette.setColor(new_option.palette.Text, QColor("black"))

        # Paint the default item with the modified options.
        super().paint(painter, new_option, index)

# Custom file system model for file-type colors.
class CustomFileSystemModel(QFileSystemModel):
    def data(self, index, role):
        if role == Qt.TextAlignmentRole and index.column() == 1:
            return Qt.AlignLeft | Qt.AlignVCenter
        elif role == Qt.ForegroundRole:
            file_path = self.filePath(index)
            if os.path.isdir(file_path):
                return QColor("#00FFFF")  # Directories = CYAN
            extension = os.path.splitext(file_path)[1].lower()
            # Executables = HOT PINK
            if extension in ['.exe', '.bat', '.sh']:
                return QColor("#FF69B4")
            extension_color = {
                '.py': "#00BFFF",  # Electric Blue
                '.txt': "#00FFFF",  # Neon Cyan
                '.html': "#FF00FF",  # Neon Magenta
                '.css': "#FF00FF",
                '.zip': "#8A2BE2",  # Deep Purple
                '.png': "#FF4500",  # Cyber Orange
                '.mp4': "#CCFF00",  # Acid Yellow
                '.pdf': "#FF2400",  # Vibrant Red
                '.json': "#FF69B4",  # Config files
            }
            return QColor(extension_color.get(extension, "#FFA500"))  # Default = BRIGHT ORANGE
        return super().data(index, role)

# Custom tree view with correct space bar selection and full-row focus
class CustomTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSelectionMode(QTreeView.ExtendedSelection)  # Allow multiple selections.
        self.setSelectionBehavior(QTreeView.SelectRows)  # Ensure full-row selection.
        self.setItemDelegate(CustomItemDelegate())  # Apply the custom delegate.

    def keyPressEvent(self, event):
        """Properly toggle space bar selection across the full row."""
        if event.key() == Qt.Key_Space:
            index = self.currentIndex()
            if index.isValid():
                sm = self.selectionModel()
                # Toggle full-row selection
                if sm.isSelected(index):
                    sm.select(index, QItemSelectionModel.Deselect | QItemSelectionModel.Rows)
                else:
                    sm.select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
                self.viewport().update()
            event.accept()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Allow right-clicking to toggle selection properly."""
        index = self.indexAt(event.pos())
        if event.button() == Qt.RightButton and index.isValid():
            sm = self.selectionModel()
            if sm.isSelected(index):
                sm.select(index, QItemSelectionModel.Deselect | QItemSelectionModel.Rows)
            else:
                sm.select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
            self.viewport().update()
            event.accept()
        else:
            super().mousePressEvent(event)

# File explorer panel with drive combo, path edit, and our custom tree view.
class FileExplorerPanel(QWidget):
    def __init__(self, start_path):
        super().__init__()
        self.current_path = start_path
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Drive combo box.
        self.drive_combo = QComboBox()
        self.drive_combo.setFocusPolicy(Qt.NoFocus)
        import string
        drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
        self.drive_combo.addItems(drives)
        self.drive_combo.currentIndexChanged.connect(self.on_drive_changed)

        # Path edit field.
        self.path_edit = QLineEdit(self.current_path)
        self.path_edit.setFocusPolicy(Qt.NoFocus)
        self.path_edit.returnPressed.connect(self.on_path_entered)

        # Go and Up buttons.
        self.go_button = QPushButton("Go")
        self.go_button.setFocusPolicy(Qt.NoFocus)
        self.go_button.clicked.connect(self.on_path_entered)

        self.up_button = QPushButton("Up")
        self.up_button.setFocusPolicy(Qt.NoFocus)
        self.up_button.clicked.connect(self.go_up)

        # Layout for controls.
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.drive_combo)
        top_layout.addWidget(self.path_edit)
        top_layout.addWidget(self.go_button)
        top_layout.addWidget(self.up_button)
        layout.addLayout(top_layout)

        # Tree view with custom model.
        self.model = CustomFileSystemModel()
        self.model.setRootPath("")
        self.tree = CustomTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.current_path))
        self.tree.setColumnWidth(0, 300)
        self.tree.setSortingEnabled(True)
        layout.addWidget(self.tree)
        self.setLayout(layout)
        self.tree.setFocus()  # Ensure tree gets key events.

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
            self.tree.setRootIndex(self.model.index(path))

    def set_focus_to_first_item(self):
        def try_set_focus():
            first_index = self.model.index(0, 0, self.tree.rootIndex())
            if first_index.isValid():
                self.tree.setCurrentIndex(first_index)
                self.tree.setFocus(Qt.OtherFocusReason)
            else:
                self.model.directoryLoaded.connect(lambda path: try_set_focus())
        try_set_focus()
