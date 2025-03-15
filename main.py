import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter, QFrame, 
    QPushButton, QAction, QMessageBox, QSizePolicy, QLabel, QStyle
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from modules.file_explorer import FileExplorerPanel
from modules.customization import apply_theme, play_sound

# Configuration File
CONFIG_FILE = "config.json"

# Use built-in Qt icons (no external images)
BUTTONS = [
    {"icon": QStyle.SP_DialogYesButton, "tooltip": "Theme"},
    {"icon": QStyle.SP_BrowserReload, "tooltip": "Refresh"},
    {"icon": QStyle.SP_FileDialogDetailedView, "tooltip": "View"},
    {"icon": QStyle.SP_DialogApplyButton, "tooltip": "Edit"},
    {"icon": QStyle.SP_DialogOpenButton, "tooltip": "Copy"}
]

class FixedButton(QPushButton):
    """A non-draggable QPushButton with an icon-only display."""
    def __init__(self, icon, tooltip, style):
        super().__init__()
        self.setFixedSize(40, 40)  # Square shape
        self.setIcon(style.standardIcon(icon))
        self.setIconSize(self.size())
        self.setToolTip(tooltip)

class ButtonColumn(QFrame):
    """Fixed-position button column that holds non-draggable buttons."""
    def __init__(self, button_configs, style):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(5, 5, 5, 5)

        # Populate with icon-only buttons
        for config in button_configs:
            button = FixedButton(config["icon"], config["tooltip"], style)
            self.layout.addWidget(button)

class GXplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GXplorer")
        self.setGeometry(100, 100, 1200, 800)
        self.showMaximized()  # Start Maximized

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

        self.left_panel = FileExplorerPanel(start_path=os.path.expanduser("~"))
        self.right_panel = FileExplorerPanel(start_path=os.path.expanduser("~"))

        # Fixed Button Column
        self.button_frame = ButtonColumn(BUTTONS, QApplication.style())

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

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        apply_theme(self, self.current_theme)
        self.config["theme"] = self.current_theme
        self.save_config()
        play_sound("theme_change")

    def refresh_panels(self):
        self.left_panel.refresh()
        self.right_panel.refresh()
        play_sound("refresh")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return {"theme": "dark"}
        return {"theme": "dark"}

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f)

def main():
    app = QApplication(sys.argv)
    window = GXplorer()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
