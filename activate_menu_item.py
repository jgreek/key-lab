#!/usr/bin/env python3

import sys
import subprocess

def activate_menu_item(app_name, menu_name, menu_item):
    applescript = f'''
    tell application "{app_name}" to activate
    tell application "System Events"
        tell process "{app_name}"
            set frontmost to true
            click menu item "{menu_item}" of menu "{menu_name}" of menu bar 1
        end tell
    end tell
    '''

    subprocess.run(["osascript", "-e", applescript])

def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <application_name> <menu_name> <menu_item>")
        sys.exit(1)

    app_name = sys.argv[1]
    menu_name = sys.argv[2]
    menu_item = sys.argv[3]

    activate_menu_item(app_name, menu_name, menu_item)

if __name__ == "__main__":
    main()