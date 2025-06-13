import subprocess
import sys
import time


def find_note_by_name(note_name):
    """
    Searches for a note with the specified name in the Mac Notes app.

    Args:
        note_name (str): The name of the note to search for
    """
    # AppleScript to open Notes and search for the specified note
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

    # Execute the AppleScript and capture the output
    result = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True)
    print(result.stdout.strip())

    if "No note found" in result.stdout:
        return False
    return True


if __name__ == "__main__":
    # Get the note name from command line arguments
    # if len(sys.argv) < 2:
    #     print("Usage: python find_note.py 'Note Name'")
    #     sys.exit(1)

    note_name = "HELP723180"
    print(f"Searching for note containing: '{note_name}'")
    find_note_by_name(note_name)