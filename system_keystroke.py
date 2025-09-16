#!/usr/bin/env python3

import subprocess
import sys
import argparse

def send_system_keystroke(key, modifiers=None):
    """
    Send a system-wide keystroke using AppleScript
    
    Args:
        key (str): The key to press
        modifiers (list): List of modifiers like 'command', 'shift', 'option', 'control'
    """
    if modifiers is None:
        modifiers = []
    
    # Build the modifier string for AppleScript
    modifier_str = ", ".join([f"{mod} down" for mod in modifiers])
    modifier_clause = f" using {{{modifier_str}}}" if modifier_str else ""
    
    # Build the AppleScript command for system-wide keystrokes
    script = f'''
    tell application "System Events"
        keystroke "{key}"{modifier_clause}
    end tell
    '''
    
    try:
        subprocess.run(['osascript', '-e', script], check=True)
        print(f"Sent system keystroke: {'+'.join(modifiers + [key])}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Send system-wide keystrokes')
    parser.add_argument('key', help='The key to press')
    parser.add_argument('modifiers', nargs='*', help='Modifiers like command, shift, option, control')
    
    args = parser.parse_args()
    
    send_system_keystroke(args.key, args.modifiers)

if __name__ == "__main__":
    main()