#!/usr/bin/env python3

import sys
import subprocess
import socket
import urllib.parse
from urllib.request import urlopen
from urllib.error import URLError
import time


def check_url_availability(url):
    """Check if a URL is available by attempting to connect to it."""
    try:
        # Parse the URL to get hostname and port
        parsed_url = urllib.parse.urlparse(url)
        hostname = parsed_url.hostname
        port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)

        # First try a quick socket connection
        try:
            with socket.create_connection((hostname, port), timeout=1) as sock:
                return True
        except (socket.timeout, socket.error):
            # If socket connection fails, try a full HTTP request
            try:
                with urlopen(url, timeout=2) as response:
                    return response.status == 200
            except URLError:
                return False
    except Exception:
        return False


def open_or_focus_browser_url(url):
    """Open or focus on a URL in Google Chrome."""
    # Use a simpler approach that just opens the URL without tab searching
    # This avoids the AppleScript syntax issues with URL property access
    applescript = f'''
    tell application "Google Chrome"
        activate
        open location "{url}"
    end tell
    '''

    subprocess.run(["osascript", "-e", applescript])


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <url1> [url2] [url3] ...")
        sys.exit(1)

    urls = sys.argv[1:]

    # If only one URL is provided, open it directly without checking
    if len(urls) == 1:
        open_or_focus_browser_url(urls[0])
        return

    # Otherwise, try each URL until one responds
    for url in urls:
        print(f"Checking {url}...")
        if check_url_availability(url):
            print(f"Found working URL: {url}")
            open_or_focus_browser_url(url)
            break
    else:  # This executes if the loop completes without breaking
        print("None of the provided URLs are responding.")
        # Optionally, you could still open the first URL even if it's not responding:
        print(f"Opening first URL anyway: {urls[0]}")
        open_or_focus_browser_url(urls[0])


if __name__ == "__main__":
    main()