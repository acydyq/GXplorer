import sys
import os
import shutil
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QSplitter,
    QAction, QFileDialog, QMessageBox, QMenuBar, QVBoxLayout,
    QPushButton, QFrame, QInputDialog
)
from PyQt5.QtCore import Qt, QEvent
from modules.file_explorer import FileExplorerPanel
from modules.customization import apply_theme, play_sound

class GXplorerMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GXplorer")
        # Start maximized
        self.setGeometry(100, 100, 1600, 1200)
        
        self.active_panel = None
        self.config_file = "resources/config.json"
        self.current_theme = "dark"  # Default to dark mode

        # Load config
        self.load_config()

        # Set up the central widget with a horizontal splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.splitter = QSplitter(Qt.Horizontal)
        self.left_panel = FileExplorerPanel(start_path=os.path.expanduser("~"))
        self.right_panel = FileExplorerPanel(start_path=os.path.expanduser("~"))

        self.left_panel.tree.clicked.connect(lambda: self.set_active_panel(self.left_panel))
        self.right_panel.tree.clicked.connect(lambda: self.set_active_panel(self.right_panel))

        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_panel)
        
        main_layout.addWidget(self.splitter)

        # Function button bar
        self.function_bar = QFrame()
        self.function_bar_layout = QHBoxLayout(self.function_bar)
        self.function_bar_layout.setSpacing(15)
        self.function_bar_layout.setContentsMargins(10, 10, 10, 10)

        self.dark_mode_button = QPushButton("Toggle Dark Mode")
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)
        self.function_bar_layout.addWidget(self.dark_mode_button)

        self.f2_refresh_button = QPushButton("F2 Refresh")
        self.f2_refresh_button.clicked.connect(self.on_f2_refresh)
        self.f3_view_button = QPushButton("F3 View")
        self.f3_view_button.clicked.connect(self.on_f3_view)
        self.f4_edit_button = QPushButton("F4 Edit")
        self.f4_edit_button.clicked.connect(self.on_f4_edit)
        self.f5_copy_button = QPushButton("F5 Copy")
        self.f5_copy_button.clicked.connect(self.on_f5_copy)
        self.f6_move_button = QPushButton("F6 Move")
        self.f6_move_button.clicked.connect(self.on_f6_move)
        self.f7_mkdir_button = QPushButton("F7 MkDir")
        self.f7_mkdir_button.clicked.connect(self.on_f7_mkdir)
        self.f8_delete_button = QPushButton("F8 Delete")
        self.f8_delete_button.clicked.connect(self.on_f8_delete)

        self.function_bar_layout.addWidget(self.f2_refresh_button)
        self.function_bar_layout.addWidget(self.f3_view_button)
        self.function_bar_layout.addWidget(self.f4_edit_button)
        self.function_bar_layout.addWidget(self.f5_copy_button)
        self.function_bar_layout.addWidget(self.f6_move_button)
        self.function_bar_layout.addWidget(self.f7_mkdir_button)
        self.function_bar_layout.addWidget(self.f8_delete_button)

        main_layout.addWidget(self.function_bar)

        # Set up menus
        self.create_menus()

        # Apply initial theme
        apply_theme(self, self.current_theme)

        # Set initial focus to the left pane
        self.set_active_panel(self.left_panel)
        self.left_panel.set_focus_to_first_item()

        # Install global event filter to catch Tab key presses
        QApplication.instance().installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Tab:
            # Clear selections on both panes when switching
            self.left_panel.tree.selectionModel().clearSelection()
            self.right_panel.tree.selectionModel().clearSelection()
            # Switch focus to the opposite pane's first item
            if self.active_panel == self.left_panel:
                self.set_active_panel(self.right_panel)
                self.right_panel.set_focus_to_first_item()
            else:
                self.set_active_panel(self.left_panel)
                self.left_panel.set_focus_to_first_item()
            return True  # Consume the event
        return super().eventFilter(source, event)

    def create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu("View")
        theme_action = QAction("Change Theme", self)
        theme_action.triggered.connect(self.change_theme)
        view_menu.addAction(theme_action)

        tools_menu = menubar.addMenu("Tools")
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About GXplorer", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def set_active_panel(self, panel):
        self.active_panel = panel
        play_sound("panel_focus")

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    self.current_theme = config.get("theme", "dark")
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self):
        config = {"theme": self.current_theme}
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    def toggle_dark_mode(self):
        self.current_theme = "dark" if self.current_theme != "dark" else "light"
        apply_theme(self, self.current_theme)
        self.save_config()
        play_sound("theme_change")

    def change_theme(self):
        theme_file, _ = QFileDialog.getOpenFileName(
            self, "Select Theme",
            "resources/themes",
            "QSS Files (*.qss)"
        )
        if theme_file:
            theme_name = os.path.splitext(os.path.basename(theme_file))[0]
            self.current_theme = theme_name
            apply_theme(self, theme_name, theme_path=theme_file)
            self.save_config()
            play_sound("theme_change")
            QMessageBox.information(self, "Theme Changed", f"Theme changed to: {theme_name}")

    def show_about(self):
        QMessageBox.information(
            self, "About GXplorer",
            "GXplorer\n\nA highly customizable, dual-pane Windows file explorer."
        )

    def on_f2_refresh(self):
        if self.active_panel:
            self.active_panel.navigate_to_path(self.active_panel.current_path)
            play_sound("refresh")

    def on_f3_view(self):
        if self.active_panel:
            selected_indexes = self.active_panel.tree.selectionModel().selectedIndexes()
            if selected_indexes:
                for index in selected_indexes:
                    path = self.active_panel.model.filePath(index)
                    if os.path.isfile(path):
                        try:
                            os.startfile(path)
                        except Exception as e:
                            QMessageBox.warning(self, "Error", f"Cannot open file: {str(e)}")
                    else:
                        self.active_panel.navigate_to_path(path)
            play_sound("open_file")

    def on_f4_edit(self):
        if self.active_panel:
            selected_indexes = self.active_panel.tree.selectionModel().selectedIndexes()
            if selected_indexes:
                for index in selected_indexes:
                    path = self.active_panel.model.filePath(index)
                    if os.path.isfile(path):
                        try:
                            os.startfile(path, "edit")
                        except:
                            try:
                                os.startfile(path)
                            except Exception as e:
                                QMessageBox.warning(self, "Error", f"Cannot edit file: {str(e)}")
                    else:
                        self.active_panel.navigate_to_path(path)
            play_sound("open_file")

    def on_f5_copy(self):
        if self.active_panel:
            source_panel = self.active_panel
            target_panel = self.right_panel if source_panel == self.left_panel else self.left_panel
            selected_indexes = source_panel.tree.selectionModel().selectedIndexes()
            if selected_indexes:
                selected_paths = set(source_panel.model.filePath(index) for index in selected_indexes)
                dest_dir = target_panel.current_path
                for src in selected_paths:
                    src = os.path.normpath(src)
                    if os.path.isfile(src):
                        try:
                            shutil.copy2(src, dest_dir)
                        except Exception as e:
                            QMessageBox.warning(self, "Copy Error", f"Could not copy {src}:\n{e}")
                    elif os.path.isdir(src):
                        try:
                            base_name = os.path.basename(src)
                            target_path = os.path.join(dest_dir, base_name)
                            shutil.copytree(src, target_path)
                        except Exception as e:
                            QMessageBox.warning(self, "Copy Error", f"Could not copy folder {src}:\n{e}")
                source_panel.navigate_to_path(source_panel.current_path)
                target_panel.navigate_to_path(target_panel.current_path)
                play_sound("copy")

    def on_f6_move(self):
        if self.active_panel:
            source_panel = self.active_panel
            target_panel = self.right_panel if source_panel == self.left_panel else self.left_panel
            selected_indexes = source_panel.tree.selectionModel().selectedIndexes()
            if selected_indexes:
                selected_paths = set(source_panel.model.filePath(index) for index in selected_indexes)
                dest_dir = target_panel.current_path
                for src in selected_paths:
                    src = os.path.normpath(src)
                    base_name = os.path.basename(src)
                    target_path = os.path.join(dest_dir, base_name)
                    try:
                        shutil.move(src, target_path)
                    except Exception as e:
                        QMessageBox.warning(self, "Move Error", f"Could not move {src}:\n{e}")
                source_panel.navigate_to_path(source_panel.current_path)
                target_panel.navigate_to_path(target_panel.current_path)
                play_sound("move")

    def on_f7_mkdir(self):
        if self.active_panel:
            folder_name, ok = QInputDialog.getText(self, "Create Folder", "Enter folder name:")
            if ok and folder_name.strip():
                new_folder_path = os.path.join(self.active_panel.current_path, folder_name.strip())
                try:
                    os.mkdir(new_folder_path)
                    self.active_panel.navigate_to_path(self.active_panel.current_path)
                    play_sound("mkdir")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Cannot create folder: {e}")

    def on_f8_delete(self):
        if self.active_panel:
            selected_indexes = self.active_panel.tree.selectionModel().selectedIndexes()
            if selected_indexes:
                selected_paths = set(self.active_panel.model.filePath(index) for index in selected_indexes)
                confirm = QMessageBox.question(
                    self, "Delete",
                    "Are you sure you want to delete the selected item(s)?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if confirm == QMessageBox.Yes:
                    for path in selected_paths:
                        path = os.path.normpath(path)
                        try:
                            if os.path.isfile(path):
                                os.remove(path)
                            elif os.path.isdir(path):
                                shutil.rmtree(path)
                        except Exception as e:
                            QMessageBox.warning(self, "Error", f"Could not delete {path}:\n{e}")
                    self.active_panel.navigate_to_path(self.active_panel.current_path)
                    play_sound("delete")

def main():
    app = QApplication(sys.argv)
    window = GXplorerMainWindow()
    window.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
