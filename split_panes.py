#!/usr/bin/env python3
"""
IT-Split: A utility to create split panes in iTerm2 and run commands in each pane.

Usage:
    it-split [vertical|horizontal] "command1" "command2" ...
"""

import sys
import os
import subprocess


def create_applescript(split_type, commands):
    """Generate AppleScript to create splits in iTerm2 with the given commands."""

    # Start the AppleScript
    script = """
    tell application "iTerm"
        activate
        tell current window
            set newTab to create tab with default profile
            tell newTab
                tell current session
    """

    # Add the first command to the initial session
    if commands:
        script += f'\n                    write text "{commands[0]}"'

    # For each additional command, create a split and run the command
    for i, cmd in enumerate(commands[1:], 1):
        split_cmd = "split vertically with default profile" if split_type == "vertical" else "split horizontally with default profile"
        script += f"""
                    set newSession to {split_cmd}
                    tell newSession
                        write text "{cmd}"
                    end tell
        """

    # Close the AppleScript
    script += """
                end tell
            end tell
        end tell
    end tell
    """

    return script


def run_applescript(script):
    """Execute the given AppleScript."""
    try:
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing AppleScript: {e}", file=sys.stderr)
        return False


def main():
    # Parse arguments
    args = sys.argv[1:]

    if not args:
        print("Usage: it-split [vertical|horizontal] \"command1\" \"command2\" ...")
        return 1

    # Check if first argument is split type
    split_type = "vertical"  # default
    if args[0].lower() in ["vertical", "horizontal"]:
        split_type = args[0].lower()
        args = args[1:]

    if not args:
        print("Error: No commands specified.")
        print("Usage: it-split [vertical|horizontal] \"command1\" \"command2\" ...")
        return 1

    # Create and run the AppleScript
    script = create_applescript(split_type, args)
    success = run_applescript(script)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())