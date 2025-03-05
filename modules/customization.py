import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QSoundEffect

def apply_theme(widget, theme_name, theme_path=None):
    """Apply a theme to the widget from a QSS file or predefined style."""
    if theme_path and os.path.exists(theme_path):
        with open(theme_path, "r") as f:
            widget.setStyleSheet(f.read())
    elif theme_name == "dark":
        widget.setStyleSheet("""
            QMainWindow, QWidget { 
                background-color: #2b2b2b; 
                color: #ffffff; 
            }
            QTreeView { 
                background-color: #333333; 
                color: #ffffff; 
            }
            QHeaderView::section {
                background-color: #333333;
                color: #ffffff;
                padding: 4px;
                border: 1px solid #555555;
            }
            QPushButton { 
                background-color: #444444; 
                color: #ffffff; 
                border: 1px solid #555555; 
                padding: 5px; 
            }
            QPushButton:hover { 
                background-color: #555555; 
            }
            QMenuBar { 
                background-color: #2b2b2b; 
                color: #ffffff; 
            }
            QMenuBar::item:selected { 
                background-color: #444444; 
            }
            QComboBox, QLineEdit { 
                background-color: #333333; 
                color: #ffffff; 
            }
        """)
    elif theme_name == "light":
        widget.setStyleSheet("""
            QMainWindow, QWidget { 
                background-color: #ffffff; 
                color: #000000; 
            }
            QTreeView { 
                background-color: #f0f0f0; 
                color: #000000; 
            }
            QPushButton { 
                background-color: #e0e0e0; 
                color: #000000; 
                border: 1px solid #cccccc; 
                padding: 5px; 
            }
            QPushButton:hover { 
                background-color: #d0d0d0; 
            }
            QMenuBar { 
                background-color: #ffffff; 
                color: #000000; 
            }
            QMenuBar::item:selected { 
                background-color: #e0e0e0; 
            }
            QComboBox, QLineEdit { 
                background-color: #f0f0f0; 
                color: #000000; 
            }
        """)
    else:
        widget.setStyleSheet("")  # Reset to default

def play_sound(action):
    """Play a sound effect."""
    sound_path = os.path.join("resources", "sounds", f"{action}.wav")
    sound = QSoundEffect()
    sound.setSource(QUrl.fromLocalFile(sound_path))
    sound.setVolume(0.5)
    sound.play()
