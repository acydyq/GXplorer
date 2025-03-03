from PyQt5.QtWidgets import QAction, QMessageBox

def register(main_window, plugins_menu):
    """
    This function is called by the PluginManager.
    It registers a sample plugin that adds a menu item to show a message.
    """
    sample_action = QAction("Sample Plugin Action", main_window)
    sample_action.triggered.connect(lambda: QMessageBox.information(main_window, "Sample Plugin", "Hello from the Sample Plugin!"))
    plugins_menu.addAction(sample_action)
