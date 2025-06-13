#!/usr/bin/env python3

import sys
import subprocess


def open_or_focus_browser_url(url):
    # This AppleScript will:
    # 1. Check if Chrome is running and has any windows
    # 2. Look through all tabs in all windows for the URL
    # 3. If found, focus on that tab
    # 4. If not found, open a new tab with the URL
    applescript = f'''
    tell application "Google Chrome"
        activate

        set targetUrl to "{url}"
        set found to false

        if (count of windows) > 0 then
            repeat with w in windows
                set tabIndex to 0
                repeat with t in tabs of w
                    set tabIndex to tabIndex + 1
                    if URL of t contains targetUrl then
                        set found to true
                        set index of w to 1
                        set active tab index of w to tabIndex
                        exit repeat
                    end if
                end repeat
                if found then exit repeat
            end repeat
        end if

        if not found then
            open location targetUrl
        end if
    end tell
    '''

    subprocess.run(["osascript", "-e", applescript])


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <url>")
        sys.exit(1)

    url = sys.argv[1]
    open_or_focus_browser_url(url)


if __name__ == "__main__":
    main()