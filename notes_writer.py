import subprocess
import datetime
import time


def open_notes_and_create_note():
    # Get today's date in the specified format
    today = datetime.datetime.now().strftime("%B %d, %Y")

    # AppleScript to open Notes and create a new note with today's date
    applescript = f'''
    tell application "Notes"
        activate
        delay 1
        tell application "System Events"
            keystroke "n" using command down
            delay 0.5
            keystroke "{today}"
        end tell
    end tell
    '''

    # Execute the AppleScript
    subprocess.run(["osascript", "-e", applescript])
    print(f"Created new note with date: {today}")


if __name__ == "__main__":
    open_notes_and_create_note()