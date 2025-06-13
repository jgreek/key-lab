#!/usr/bin/env python3

import subprocess
import datetime
import sys
import time
import argparse


class NotesManager:
    """A class to manage notes in the macOS Notes app."""

    def __init__(self):
        """Initialize the NotesManager."""
        # Check if running on macOS
        if sys.platform != "darwin":
            raise SystemError("This script only works on macOS")

    def _run_applescript(self, script):
        """Execute an AppleScript and return the result.

        Args:
            script (str): The AppleScript to execute

        Returns:
            str: The output of the AppleScript
        """
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        if result.stderr:
            print(f"AppleScript Error: {result.stderr}")
        return result.stdout.strip()

    def find_note(self, note_name):
        """Find a note by name.

        Args:
            note_name (str): The name of the note to find

        Returns:
            bool: True if the note was found, False otherwise
        """
        print(f"Searching for note: '{note_name}'")

        applescript = f'''
        tell application "Notes"
            activate
            delay 0.5

            -- Use search functionality
            tell application "System Events"
                keystroke "f" using command down
                delay 0.3
                keystroke "{note_name}"
                delay 1
            end tell

            -- Try to find the note in the current account
            set foundNotes to notes where name contains "{note_name}"

            if length of foundNotes > 0 then
                set targetNote to item 1 of foundNotes
                show targetNote
                return "Note found: " & name of targetNote
            else
                return "No note found with name containing: {note_name}"
            end if
        end tell
        '''

        result = self._run_applescript(applescript)
        print(result)
        return "No note found" not in result

    def create_note(self, title=None, content=""):
        """Create a new note with optional title and content.

        Args:
            title (str, optional): The title for the new note. If None, today's date is used.
            content (str, optional): The content for the new note.

        Returns:
            bool: True if the note was created successfully
        """
        if title is None:
            title = datetime.datetime.now().strftime("%B %d, %Y")

        print(f"Creating new note with title: '{title}'")

        # Escape double quotes in content and title
        content = content.replace('"', '\\"')
        title = title.replace('"', '\\"')

        applescript = f'''
        tell application "Notes"
            activate
            delay 0.5

            -- Create a new note
            set newNote to make new note with properties {{body:"{title}\\n{content}"}}
            show newNote

            return "Note created: " & name of newNote
        end tell
        '''

        result = self._run_applescript(applescript)
        print(result)
        return "Note created" in result

    def append_to_note(self, note_name, content):
        """Append content to an existing note.

        Args:
            note_name (str): The name of the note to append to
            content (str): The content to append

        Returns:
            bool: True if content was appended successfully
        """
        print(f"Appending to note: '{note_name}'")

        # Escape double quotes in content and note_name
        content = content.replace('"', '\\"')
        note_name = note_name.replace('"', '\\"')

        applescript = f'''
        tell application "Notes"
            set foundNotes to notes where name contains "{note_name}"

            if length of foundNotes > 0 then
                set targetNote to item 1 of foundNotes
                set body of targetNote to (body of targetNote) & "\\n{content}"
                show targetNote
                return "Content appended to note: " & name of targetNote
            else
                return "No note found with name containing: {note_name}"
            end if
        end tell
        '''

        result = self._run_applescript(applescript)
        print(result)
        return "Content appended" in result

    def read_file_content(self, file_path):
        """Read content from a file.

        Args:
            file_path (str): Path to the file to read

        Returns:
            str: The content of the file
        """
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return ""


def main():
    """Main function to parse arguments and call appropriate methods."""
    parser = argparse.ArgumentParser(description="Manage notes in the macOS Notes app")

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Find note command
    find_parser = subparsers.add_parser("find", help="Find a note by name")
    find_parser.add_argument("note_name", help="Name of the note to find")

    # Create note command
    create_parser = subparsers.add_parser("create", help="Create a new note")
    create_parser.add_argument("--title", help="Title for the new note (default: today's date)")
    create_parser.add_argument("--content", help="Content for the new note")
    create_parser.add_argument("--file", help="File containing content for the new note")

    # Append command
    append_parser = subparsers.add_parser("append", help="Append content to an existing note")
    append_parser.add_argument("note_name", help="Name of the note to append to")
    append_parser.add_argument("--content", help="Content to append")
    append_parser.add_argument("--file", help="File containing content to append")

    args = parser.parse_args()

    # Initialize the NotesManager
    manager = NotesManager()

    if args.command == "find":
        manager.find_note(args.note_name)

    elif args.command == "create":
        content = ""
        if args.file:
            content = manager.read_file_content(args.file)
        elif args.content:
            content = args.content

        manager.create_note(args.title, content)

    elif args.command == "append":
        content = ""
        if args.file:
            content = manager.read_file_content(args.file)
        elif args.content:
            content = args.content
        else:
            print("Error: Either --content or --file must be provided")
            return

        manager.append_to_note(args.note_name, content)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()