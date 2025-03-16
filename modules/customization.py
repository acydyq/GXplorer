import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QSoundEffect

def apply_theme(widget, theme_name):
    """Apply a theme to the widget."""
    if theme_name == "dark":
        widget.setStyleSheet("""
            QMainWindow, QWidget { 
                background-color: #2b2b2b; 
                color: white; 
            }
            QTreeView { 
                background-color: #333333; 
                color: white; 
            }
            QHeaderView::section {
                background-color: #444444;  /* Dark background for column labels */
                color: white;
                padding: 4px;
                border: 1px solid #555555;
            }
            QPushButton { 
                background-color: #444444; 
                color: white; 
                border: 1px solid #555555; 
                padding: 5px; 
            }
            QPushButton:hover { 
                background-color: #555555; 
            }
            QMenuBar { 
                background-color: #2b2b2b; 
                color: white; 
            }
            QMenuBar::item:selected { 
                background-color: #444444; 
            }
            QComboBox, QLineEdit { 
                background-color: #333333; 
                color: white; 
            }
        """)
    elif theme_name == "light":
        widget.setStyleSheet("""
            QMainWindow, QWidget { 
                background-color: white; 
                color: black; 
            }
            QTreeView { 
                background-color: #f0f0f0; 
                color: black; 
            }
            QHeaderView::section {
                background-color: #e0e0e0;  /* Light background for column labels */
                color: black;
                padding: 4px;
                border: 1px solid #cccccc;
            }
            QPushButton { 
                background-color: #e0e0e0; 
                color: black; 
                border: 1px solid #cccccc; 
                padding: 5px; 
            }
            QPushButton:hover { 
                background-color: #d0d0d0; 
            }
            QMenuBar { 
                background-color: white; 
                color: black; 
            }
            QMenuBar::item:selected { 
                background-color: #e0e0e0; 
            }
            QComboBox, QLineEdit { 
                background-color: #f0f0f0; 
                color: black; 
            }
        """)

def play_sound(action):
    """Play a sound effect."""
    sound_path = os.path.join("resources", "sounds", f"{action}.wav")
    sound = QSoundEffect()
    sound.setSource(QUrl.fromLocalFile(sound_path))
    sound.setVolume(0.5)
    sound.play()
