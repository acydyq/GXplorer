import os
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import QUrl

def apply_theme(window, theme_name, theme_path=None):
    """
    Apply a QSS theme to the application.
    If theme_path is not provided, it looks for the theme in resources/themes.
    """
    if not theme_path:
        theme_path = os.path.join("resources", "themes", f"{theme_name}.qss")
    try:
        with open(theme_path, "r") as f:
            style = f.read()
            window.setStyleSheet(style)
    except Exception as e:
        print(f"Error applying theme {theme_name}: {e}")

def play_sound(sound_name):
    """
    Play a sound effect.
    Looks for the sound file in resources/sounds.
    Supported formats depend on your system.
    """
    sound_path = os.path.join("resources", "sounds", f"{sound_name}.wav")
    sound = QSoundEffect()
    sound.setSource(QUrl.fromLocalFile(sound_path))
    sound.setVolume(0.5)
    sound.play()
