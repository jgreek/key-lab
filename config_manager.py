import json
import os
from pathlib import Path
from datetime import datetime
import logging


class ConfigManager:
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.config_mtime = 0
        self.config = self.load_config()
        self.update_config_mtime()

    def get_default_config(self):
        return {
            "settings": {
                "backspace_custom_combo": True,
                "combo_timeout_seconds": 5.0
            },
            "apps": {
                "cmd+1": "/Applications/Google Chrome.app",
                "cmd+2": "/Applications/PyCharm.app",
                "cmd+3": "/Applications/Microsoft Outlook.app",
                "cmd+4": "/Applications/iTerm.app",
                "cmd+5": "/Applications/Symphony.app"
            },
            "commands": {
                "cmd+6": [
                    {"command": "mxx", "delay": 10},
                    {"command": "gparun", "delay": 0},
                    {"command": "v2run", "delay": 0}
                ],
                "cmd+7": [{"command": "xx", "delay": 0}],
                "cmd+8": [{"command": "top", "delay": 0}]
            }
        }

    def load_config(self):
        if not self.config_path.exists():
            default_config = self.get_default_config()
            with open(self.config_path, "w") as f:
                json.dump(default_config, f, indent=2)
            print(f"Created default config file at {self.config_path}")

        with open(self.config_path, "r") as f:
            return json.load(f)

    def update_config_mtime(self):
        try:
            self.config_mtime = os.path.getmtime(self.config_path)
        except Exception as e:
            logging.error(f"Error getting config file modification time: {e}")

    def check_for_updates(self):
        try:
            current_mtime = os.path.getmtime(self.config_path)
            if current_mtime != self.config_mtime:
                self.config = self.load_config()
                self.config_mtime = current_mtime
                print(f"[{datetime.now().strftime('%Y-%m-%d %I:%M %p')}] Config reloaded - file was modified")
                return True
        except Exception as e:
            logging.error(f"Error checking config file: {e}")
        return False

    def get_setting(self, key, default=None):
        return self.config.get("settings", {}).get(key, default)

    def get_apps(self):
        return self.config.get("apps", {})

    def get_commands(self):
        return self.config.get("commands", {})

    def get_custom_combo_keys(self):
        return set(combo for combo in self.get_commands() if not combo.startswith("cmd+"))

    def is_configured_shortcut(self, key_combo):
        return key_combo in self.get_apps() or key_combo in self.get_commands()