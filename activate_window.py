#!/usr/bin/env python3

import sys
import subprocess


def activate_window(app_name, window_name):
    applescript = f'''
    tell application "{app_name}" to activate
    tell application "System Events"
        tell process "{app_name}"
            set frontmost to true
            click menu item "{window_name}" of menu "Window" of menu bar 1
        end tell
    end tell
    '''

    subprocess.run(["osascript", "-e", applescript])


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <application_name> <window_name>")
        sys.exit(1)

    app_name = sys.argv[1]
    window_name = sys.argv[2]

    activate_window(app_name, window_name)


if __name__ == "__main__":
    main()