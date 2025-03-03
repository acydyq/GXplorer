import os
import shutil
import string

from PyQt5.QtCore import (
    Qt, QDir, QItemSelection, QItemSelectionModel, QModelIndex
)
from PyQt5.QtGui import QColor, QPalette, QPainter, QPen
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTreeView, QMenu, QAction,
    QMessageBox, QPushButton, QStyledItemDelegate, QInputDialog, QComboBox,
    QHeaderView, QFileSystemModel, QStyleOptionViewItem, QStyle
)

class FileExplorerDelegate(QStyledItemDelegate):
    """
    Custom delegate that:
      - Uses a custom selection model for 'selected' rows
      - Distinguishes 'focused row' by checking if index == tree.currentIndex()
      - In paint(), sets the background + text color:
          Focus + Selected => red text on black
          Focus only => white text on black
          Selected only => black text on red
          Otherwise => default or folder/archive color
    """
    def __init__(self, file_model, tree_view, parent=None):
        super().__init__(parent)
        self.file_model = file_model
        self.tree_view = tree_view

    def paint(self, painter, option, index):
        """
        We override paint so we can unify focus/selection logic here.
        """
        row = index.row()
        parent_idx = index.parent()
        first_col = self.file_model.index(row, 0, parent_idx)

        # Determine if the row is selected in our custom selection model
        is_selected = (
            self.tree_view.selection_model is not None
            and self.tree_view.selection_model.isSelected(first_col)
        )

        # Determine if this row is in focus (i.e., currentIndex)
        is_focused = (index == self.tree_view.currentIndex())

        # Decide background + text color
        if is_focused and is_selected:
            # Focus + Selected => red text on black
            bg_color = QColor("black")
            fg_color = QColor("red")
        elif is_focused:
            # Focus only => white text on black
            bg_color = QColor("black")
            fg_color = QColor("white")
        elif is_selected:
            # Selected only => black text on red
            bg_color = QColor("red")
            fg_color = QColor("black")
        else:
            # Not focused, not selected => use folder/archive color or default
            path = self.file_model.filePath(index)
            if self.file_model.isDir(index):
                fg_color = QColor("cyan")
            else:
                _, ext = os.path.splitext(path)
                if ext.lower() in (".zip", ".rar", ".7z", ".tar", ".gz", ".iso"):
                    fg_color = QColor("violet")
                else:
                    fg_color = option.palette.color(QPalette.Text)
            bg_color = option.palette.color(QPalette.Base)  # typically white or your theme’s color

        # Fill the row background
        painter.fillRect(option.rect, bg_color)

        # Now paint the text
        # We'll replicate normal QStyledItemDelegate text painting logic:
        # but with our chosen foreground color
        text = index.data(Qt.DisplayRole)
        if text is None:
            text = ""

        painter.setPen(fg_color)

        # We can do basic text alignment
        alignment = index.data(Qt.TextAlignmentRole)
        if alignment is None:
            alignment = Qt.AlignLeft | Qt.AlignVCenter

        rect = option.rect
        painter.drawText(rect, alignment, text)

    def sizeHint(self, option, index):
        """
        Keep default sizeHint from QStyledItemDelegate, or override if you want bigger row heights.
        """
        return super().sizeHint(option, index)

class FileExplorerTree(QTreeView):
    """
    - setSelectionMode(QTreeView.NoSelection) so left-click doesn't auto-select
    - We manage a QItemSelectionModel for toggling selection with space
    - Arrow keys move focus only
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QTreeView.NoSelection)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSelectionBehavior(QTreeView.SelectRows)
        self.setAllColumnsShowFocus(True)

        self.selection_model = None

    def set_custom_selection_model(self, sel_model):
        self.selection_model = sel_model

    def mousePressEvent(self, event):
        idx = self.indexAt(event.pos())
        if idx.isValid():
            if event.button() == Qt.LeftButton:
                # Left-click => focus only
                self.setCurrentIndex(idx)
                self.setFocus(Qt.MouseFocusReason)
                super(QTreeView, self).mousePressEvent(event)
            elif event.button() == Qt.RightButton:
                # Right-click => focus only, context menu is handled externally
                self.setCurrentIndex(idx)
                self.setFocus(Qt.MouseFocusReason)
                super(QTreeView, self).mousePressEvent(event)
            else:
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def keyPressEvent(self, event):
        current = self.currentIndex()
        if event.key() == Qt.Key_Space and current.isValid():
            self.toggle_selection(current)
            event.accept()
        elif event.key() == Qt.Key_Up:
            self.move_focus_up(current)
            event.accept()
        elif event.key() == Qt.Key_Down:
            self.move_focus_down(current)
            event.accept()
        else:
            super().keyPressEvent(event)

    def toggle_selection(self, index):
        """Toggle entire row in the custom selection model."""
        if not self.selection_model:
            return
        row = index.row()
        parent = index.parent()
        col_count = self.model().columnCount(parent)
        first_col = self.model().index(row, 0, parent)
        last_col = self.model().index(row, col_count - 1, parent)

        selection = QItemSelection(first_col, last_col)
        if self.selection_model.isSelected(first_col):
            self.selection_model.select(selection, QItemSelectionModel.Deselect)
        else:
            self.selection_model.select(selection, QItemSelectionModel.Select)

        self.viewport().update()

    def move_focus_up(self, current):
        if current.isValid():
            up_idx = self.indexAbove(current)
            if up_idx.isValid():
                self.setCurrentIndex(up_idx)
                self.viewport().update()

    def move_focus_down(self, current):
        if current.isValid():
            down_idx = self.indexBelow(current)
            if down_idx.isValid():
                self.setCurrentIndex(down_idx)
                self.viewport().update()

class FileExplorerPanel(QWidget):
    def __init__(self, start_path=None, parent=None):
        super().__init__(parent)
        self.current_path = start_path or QDir.rootPath()

        # Path bar
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.path_layout = QHBoxLayout()
        self.drive_combo = QComboBox()
        self.populate_drives()
        self.drive_combo.currentIndexChanged.connect(self.on_drive_changed)
        self.path_layout.addWidget(self.drive_combo)

        self.path_edit = QLineEdit(self.current_path)
        self.path_edit.returnPressed.connect(self.on_path_entered)
        self.path_layout.addWidget(self.path_edit)

        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.on_path_entered)
        self.path_layout.addWidget(self.go_button)

        self.up_button = QPushButton("Up")
        self.up_button.clicked.connect(self.go_up)
        self.path_layout.addWidget(self.up_button)

        self.main_layout.addLayout(self.path_layout)

        # File system + Tree
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())

        self.tree = FileExplorerTree()
        self.tree.setModel(self.model)

        # Create custom selection model after setModel
        self.my_selection_model = QItemSelectionModel(self.model)
        self.tree.set_custom_selection_model(self.my_selection_model)

        # We do NOT rely on style sheets for selected/focus color.
        # The delegate's paint method handles everything for consistent logic.

        # If you want a general style sheet for QTreeView, e.g. row heights, do it here
        # self.tree.setStyleSheet("QTreeView { font-size: 10pt; }")

        self.tree.setHeaderHidden(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, self.model.columnCount()):
            self.tree.header().setSectionResizeMode(col, QHeaderView.ResizeToContents)

        # Our custom delegate
        self.delegate = FileExplorerDelegate(self.model, self.tree)
        self.tree.setItemDelegate(self.delegate)

        self.main_layout.addWidget(self.tree)

        self.navigate_to_path(self.current_path)

    def populate_drives(self):
        self.drive_combo.clear()
        if os.name == 'nt':
            drs = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
            self.drive_combo.addItems(drs)
        else:
            self.drive_combo.addItem("/")

    def on_drive_changed(self):
        drive = self.drive_combo.currentText()
        if drive:
            self.navigate_to_path(drive)

    def on_path_entered(self):
        new_path = self.path_edit.text().strip()
        self.navigate_to_path(new_path)

    def go_up(self):
        parent_dir = os.path.dirname(self.current_path)
        if parent_dir and os.path.exists(parent_dir):
            self.navigate_to_path(parent_dir)

    def navigate_to_path(self, path):
        if not os.path.exists(path):
            QMessageBox.warning(self, "Error", f"Path does not exist:\n{path}")
            return
        self.current_path = os.path.normpath(path)
        self.path_edit.setText(self.current_path)
        self.tree.setRootIndex(self.model.index(self.current_path))

    def open_context_menu(self, pos):
        idx = self.tree.indexAt(pos)
        if not idx.isValid():
            return

        menu = QMenu()
        open_action = QAction("Open", self)
        open_action.triggered.connect(lambda: self.on_double_click(idx))
        menu.addAction(open_action)

        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(lambda: self.rename_item(idx))
        menu.addAction(rename_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_item(idx))
        menu.addAction(delete_action)

        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def on_double_click(self, index):
        path = self.model.filePath(index)
        if os.path.isdir(path):
            self.navigate_to_path(path)
        else:
            try:
                os.startfile(path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Cannot open file:\n{e}")

    def rename_item(self, index):
        path = self.model.filePath(index)
        base_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=base_name)
        if ok and new_name.strip():
            new_path = os.path.join(os.path.dirname(path), new_name.strip())
            if os.path.exists(new_path):
                QMessageBox.warning(self, "Error", "Cannot rename: file/folder already exists.")
                return
            try:
                os.rename(path, new_path)
                self.navigate_to_path(os.path.dirname(new_path))
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not rename:\n{e}")

    def delete_item(self, index):
        path = self.model.filePath(index)
        ans = QMessageBox.question(
            self, "Delete",
            f"Are you sure you want to delete:\n{path}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if ans == QMessageBox.Yes:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)
                QMessageBox.information(self, "Deleted", f"Deleted: {path}")
                self.navigate_to_path(os.path.dirname(path))
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not delete:\n{e}")
