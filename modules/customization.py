import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QSoundEffect

def apply_theme(widget, theme_name):
    """Apply a theme to the widget."""
    if theme_name == "dark":
        widget.setStyleSheet("""
            QWidget { background-color: #2b2b2b; color: white; }
            QPushButton { background-color: #444; color: white; }
            QPushButton:hover { background-color: #666; }
        """)
    elif theme_name == "light":
        widget.setStyleSheet("""
            QWidget { background-color: #ffffff; color: black; }
            QPushButton { background-color: #ccc; color: black; }
            QPushButton:hover { background-color: #aaa; }
        """)
    else:
        widget.setStyleSheet("")

def play_sound(action):
    """Play a sound effect if the file exists."""
    sound_path = os.path.join("resources", "sounds", f"{action}.wav")
    if os.path.exists(sound_path):
        sound = QSoundEffect()
        sound.setSource(QUrl.fromLocalFile(sound_path))
        sound.setVolume(0.5)
        sound.play()
