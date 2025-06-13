import subprocess
import shlex
import os
import time
from pathlib import Path
from datetime import datetime


class CommandExecutor:
    def __init__(self, app_dir):
        self.app_dir = Path(app_dir)

    def open_app(self, app_path):
        if os.path.exists(app_path):
            if os.path.isdir(app_path):
                subprocess.Popen(["open", app_path])
            else:
                subprocess.Popen([app_path])
            app_name = Path(app_path).stem
            current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            print(f"[{current_time}] KeyMapper - Opened (Direct): {app_name}")
        else:
            print(f"The file or directory {app_path} does not exist.")

    def run_iterm_command(self, command):
        applescript = f'''
            tell application "iTerm2"
                tell current window
                    create window with default profile
                    tell current session
                        write text "{command}"
                    end tell
                end tell
            end tell
            '''
        subprocess.run(["osascript", "-e", applescript])

    def run_file_command(self, file_command):
        try:
            parts = shlex.split(file_command)
            file_name = parts[0]
            args = parts[1:]

            file_path = self.app_dir / file_name

            if file_path.exists():
                if file_path.suffix == '.py':
                    subprocess.run(['python3', str(file_path)] + args)
                else:
                    subprocess.run([str(file_path)] + args)
            else:
                print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error running file command: {e}")

    def run_commands(self, commands, key_combo):
        if not commands:
            print(f"No commands configured for {key_combo}")
            return

        for cmd in commands:
            if 'file_command' in cmd:
                self.run_file_command(cmd['file_command'])
            else:
                full_command = f"source ~/.bashrc && {cmd['command']}"
                self.run_iterm_command(full_command)
            time.sleep(cmd.get("delay", 0))

        current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        comment = ""
        if commands and len(commands) > 0 and 'comment' in commands[0]:
            comment = f" - {commands[0]['comment']}"

        print(f"[{current_time}] {key_combo}{comment}")
