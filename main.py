import shutil
import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter, QFrame, 
    QPushButton, QMessageBox, QSizePolicy, QStyle
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from modules.file_explorer import FileExplorerPanel
from modules.customization import apply_theme, play_sound

# Configuration File
CONFIG_FILE = "config.json"

# Button actions mapped to functions
BUTTONS = [
    {"icon": QStyle.SP_DialogYesButton, "tooltip": "Toggle Theme", "action": "toggle_theme"},
    {"icon": QStyle.SP_BrowserReload, "tooltip": "Refresh", "action": "refresh_panels"},
    {"icon": QStyle.SP_FileDialogDetailedView, "tooltip": "View", "action": "on_view"},
    {"icon": QStyle.SP_DialogApplyButton, "tooltip": "Edit", "action": "on_edit"},
    {"icon": QStyle.SP_DialogOpenButton, "tooltip": "Copy", "action": "on_copy"}
]

class FixedButton(QPushButton):
    """A non-draggable QPushButton with an icon-only display."""
    def __init__(self, icon, tooltip, action, main_window):
        super().__init__()
        self.setFixedSize(40, 40)  # Square shape
        self.setIcon(main_window.style().standardIcon(icon))
        self.setIconSize(self.size())
        self.setToolTip(tooltip)
        self.action = action
        self.main_window = main_window
        self.clicked.connect(self.execute_action)

    def execute_action(self):
        """Executes the corresponding action when clicked."""
        if hasattr(self.main_window, self.action):
            getattr(self.main_window, self.action)()

class ButtonColumn(QFrame):
    """Fixed-position button column that holds functional buttons."""
    def __init__(self, button_configs, main_window):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(5, 5, 5, 5)

        # Populate with functional buttons
        for config in button_configs:
            button = FixedButton(config["icon"], config["tooltip"], config["action"], main_window)
            self.layout.addWidget(button)

class GXplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        print("Initializing GXplorer...")
        self.setWindowTitle("GXplorer")
        self.setGeometry(100, 100, 1200, 800)
        self.showMaximized()

        # Load Config
        self.config = self.load_config()
        self.current_theme = self.config.get("theme", "dark")

        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Splitter for dual-pane layout
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.left_panel = FileExplorerPanel(start_path=os.path.expanduser("~"), main_window=self)
        self.right_panel = FileExplorerPanel(start_path=os.path.expanduser("~"), main_window=self)

        # Track the last active panel
        self.last_active_panel = self.left_panel  # Default to left panel

        # Functional Button Column
        self.button_frame = ButtonColumn(BUTTONS, self)

        # Insert into splitter
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.button_frame)
        self.splitter.addWidget(self.right_panel)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 0)
        self.splitter.setStretchFactor(2, 1)

        main_layout.addWidget(self.splitter, stretch=1)

        # Apply Initial Theme
        apply_theme(self, self.current_theme)
        print("GXplorer is ready.")

    def toggle_theme(self):
        """Toggles between light and dark themes."""
        print("Toggling theme...")
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        apply_theme(self, self.current_theme)
        self.config["theme"] = self.current_theme
        self.save_config()
        play_sound("theme_change")

    def refresh_panels(self):
        """Refreshes both file explorer panels."""
        print("Refreshing panels...")
        self.left_panel.navigate_to_path(self.left_panel.current_path)
        self.right_panel.navigate_to_path(self.right_panel.current_path)
        play_sound("refresh")

    def on_view(self):
        """Opens the selected file in the default application."""
        print("Opening file...")
        self.execute_file_action("view")

    def on_edit(self):
        """Opens the selected file for editing."""
        print("Editing file...")
        self.execute_file_action("edit")

    def on_copy(self):
        """Copies the selected file(s) to the opposite pane."""
        print("Copying file(s)...")
        self.execute_file_action("copy")

    def execute_file_action(self, action):
        """Performs file operations based on user selection."""
        active_panel = self.last_active_panel
        print("Active panel:", "left" if active_panel == self.left_panel else "right")
        selected_indexes = active_panel.tree.selectionModel().selectedIndexes()
        print("Selected indexes:", selected_indexes)
        if selected_indexes:
            print("Number of items selected:", len(selected_indexes))
            if action == "copy":
                self.copy_files(active_panel, selected_indexes)
            else:
                for index in selected_indexes:
                    source_index = active_panel.proxy_model.mapToSource(index)
                    path = active_panel.model.filePath(source_index)
                    print(f"{'Viewing' if action == 'view' else 'Editing'} path: {path}")
                    try:
                        if action == "view":
                            os.startfile(path)  # Opens with default application
                        elif action == "edit":
                            os.system(f'notepad.exe "{path}"')  # Opens in Notepad
                    except Exception as e:
                        print(f"Failed to {action} {path}: {e}")
                        QMessageBox.warning(self, "Error", f"Failed to {action} {path}: {e}")
        else:
            print("No items selected")
            QMessageBox.information(self, "Info", "No items selected.")

    def copy_files(self, source_panel, selected_indexes):
        """Copies selected files to the opposite pane's current directory."""
        target_panel = self.right_panel if source_panel == self.left_panel else self.left_panel
        target_path = target_panel.current_path
        for index in selected_indexes:
            source_index = source_panel.proxy_model.mapToSource(index)
            source_path = source_panel.model.filePath(source_index)
            print("Copying from:", source_path)
            if os.path.isfile(source_path):
                file_name = os.path.basename(source_path)
                dest_path = os.path.join(target_path, file_name)
                try:
                    shutil.copy2(source_path, dest_path)
                    print(f"Copied to {dest_path}")
                except Exception as e:
                    print(f"Failed to copy {source_path}: {e}")
                    QMessageBox.warning(self, "Error", f"Failed to copy {source_path}: {e}")
        target_panel.navigate_to_path(target_path)  # Refresh target panel

    def load_config(self):
        """Loads configuration from file."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return {"theme": "dark"}
        return {"theme": "dark"}

    def save_config(self):
        """Saves configuration to file."""
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f)

def main():
    print("Starting GXplorer...")
    app = QApplication(sys.argv)
    window = GXplorer()
    window.show()
    print("GXplorer is now running.")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()