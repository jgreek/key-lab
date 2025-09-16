import os
import logging
from pathlib import Path
from pynput import keyboard
from config_manager import ConfigManager
from csv_logger import CSVLogger
from csv_cleaner import CSVCleaner
from key_tracker import KeyTracker
from command_executor import CommandExecutor
from display_manager import DisplayManager

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class MacKeyListener:
    def __init__(self):
        self.app_dir = Path(os.path.dirname(os.path.abspath(__file__)))

        # Initialize components
        self.config_manager = ConfigManager(self.app_dir / "config.json")
        self.csv_logger = CSVLogger(self.app_dir / "key_listener_actions.csv")
        self.csv_cleaner = CSVCleaner(self.csv_logger, self.config_manager)
        self.key_tracker = KeyTracker(
            combo_timeout=self.config_manager.get_setting("combo_timeout_seconds", 5.0),
            max_combo_length=3
        )
        self.command_executor = CommandExecutor(self.app_dir)
        self.display_manager = DisplayManager(self.config_manager, self.csv_logger)

        # Clean up CSV file on startup
        self.csv_cleaner.cleanup_outdated_entries()

        # Initialize keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)

    def on_press(self, key):
        try:
            if key in [keyboard.Key.cmd, keyboard.Key.shift, keyboard.Key.alt]:
                self.key_tracker.set_modifier_state(key, True)
            elif hasattr(key, 'char') and key.char:
                self.key_tracker.add_key(key.char)

                # Check for custom combos
                combo = self.key_tracker.get_current_combo()
                custom_combo_keys = self.config_manager.get_custom_combo_keys()

                if combo in custom_combo_keys:
                    backspace_custom_combo = self.config_manager.get_setting("backspace_custom_combo", True)
                    if backspace_custom_combo:
                        self.key_tracker.backspace_combo(len(combo))
                    self.handle_key_combo(combo)
                    self.key_tracker.clear_combo()

                # Check for cmd+ combos
                if self.key_tracker.cmd_pressed and key.char:
                    if not self.key_tracker.shift_pressed and not self.key_tracker.option_pressed:
                        self.handle_key_combo(f"cmd+{key.char}")
                    else:
                        # Shift+Cmd combination not configured - skip silently
                        pass

        except Exception as e:
            logging.error(f"Error handling key {key}: {str(e)}", exc_info=True)

    def on_release(self, key):
        if key in [keyboard.Key.cmd, keyboard.Key.shift, keyboard.Key.alt]:
            self.key_tracker.set_modifier_state(key, False)

    def handle_key_combo(self, key_combo):
        # Check for config updates
        config_updated = self.config_manager.check_for_updates()

        if config_updated:
            # Update key tracker timeout if config changed
            self.key_tracker.combo_timeout = self.config_manager.get_setting("combo_timeout_seconds", 5.0)
            # Clean up CSV file when config is updated
            self.csv_cleaner.cleanup_outdated_entries()
            self.display_manager.print_cheatsheet()

        # Only process configured shortcuts
        if self.config_manager.is_configured_shortcut(key_combo):
            # Get comment for logging
            comment = self.display_manager.get_action_comment(key_combo)

            # Log the action
            self.csv_logger.log_action(key_combo, comment)

            # Execute the action
            apps = self.config_manager.get_apps()
            commands = self.config_manager.get_commands()

            if key_combo in apps:
                self.command_executor.open_app(apps[key_combo])
            elif key_combo in commands:
                self.command_executor.run_commands(commands[key_combo], key_combo)

    def start(self):
        print(f"MacKeyListener started. Using config: {self.config_manager.config_path}")
        print(f"CSV logging to: {self.csv_logger.csv_log_path}")
        print("Config auto-reload enabled - changes will be detected on next key press")
        self.display_manager.print_cheatsheet()
        self.display_manager.print_csv_stats()
        self.display_manager.print_recent_commands()
        self.display_manager.print_least_used_commands()
        print("\nPress Ctrl+C to exit.")

        with self.listener as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                print("\nMacKeyListener stopped.")
                print("Final usage statistics:")
                self.display_manager.print_csv_stats()
                self.display_manager.print_recent_commands()