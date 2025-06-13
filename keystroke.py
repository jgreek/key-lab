#!/usr/bin/env python3
import subprocess
import sys


def send_keystroke(app_name, key, modifiers=None):
    """
    Send a keystroke to a specific application on macOS

    Args:
        app_name (str): Name of the application
        key (str): The key to press
        modifiers (list): List of modifiers like 'command', 'option', 'shift', 'control'
    """
    if modifiers is None:
        modifiers = []

    # Build the modifier string
    modifier_str = ", ".join([f"{mod} down" for mod in modifiers])
    modifier_clause = f" using {{{modifier_str}}}" if modifier_str else ""

    # Build the AppleScript command
    script = f'''
    tell application "{app_name}" to activate
    tell application "System Events" to keystroke "{key}"{modifier_clause}
    '''

    try:
        subprocess.run(['osascript', '-e', script], check=True)
        print(f"Sent {'+'.join(modifiers + [key])} to {app_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print("Usage: python keystroke.py <app_name> <key> [modifiers...]")
        print("Example: python keystroke.py 'Microsoft Outlook' 2 command option")
        sys.exit(1)

    app_name = sys.argv[1]
    key = sys.argv[2]
    modifiers = sys.argv[3:] if len(sys.argv) > 3 else []

    send_keystroke(app_name, key, modifiers)


if __name__ == "__main__":
    main()