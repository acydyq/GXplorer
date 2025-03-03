import os
import sys
import importlib.util

class PluginManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.plugins_folder = os.path.join(os.getcwd(), "plugins")
        self.loaded_plugins = []

    def load_plugins(self):
        if not os.path.exists(self.plugins_folder):
            print("Plugins folder not found.")
            return
        
        for filename in os.listdir(self.plugins_folder):
            if filename.endswith(".py"):
                filepath = os.path.join(self.plugins_folder, filename)
                plugin_name = os.path.splitext(filename)[0]
                try:
                    spec = importlib.util.spec_from_file_location(plugin_name, filepath)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[plugin_name] = module
                    spec.loader.exec_module(module)
                    if hasattr(module, "register"):
                        # Call the plugin's register function and pass the main window and plugin menu.
                        module.register(self.main_window, self.main_window.plugins_menu)
                        self.loaded_plugins.append(plugin_name)
                        print(f"Loaded plugin: {plugin_name}")
                    else:
                        print(f"No register() found in {plugin_name}")
                except Exception as e:
                    print(f"Error loading plugin {plugin_name}: {e}")
