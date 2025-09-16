#!/usr/bin/env python3

import sys
import subprocess
import socket
import urllib.parse
import argparse
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


def get_origin(url):
    """Extract the origin (scheme + hostname + port) from a URL."""
    parsed = urllib.parse.urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    return origin


def find_and_focus_tab_by_origin(target_origin):
    """Find and focus a Chrome tab with the same origin. Returns True if found."""
    applescript = f'''
    tell application "Google Chrome"
        set foundTab to false
        set targetOrigin to "{target_origin}"
        
        set windowCount to count of windows
        repeat with i from 1 to windowCount
            set w to window i
            set tabCount to count of tabs of w
            repeat with j from 1 to tabCount
                set t to tab j of w
                set tabURL to URL of t
                if tabURL starts with targetOrigin then
                    tell w
                        set active tab index to j
                    end tell
                    activate
                    set index of w to 1
                    set foundTab to true
                    exit repeat
                end if
            end repeat
            if foundTab then exit repeat
        end repeat
        
        return foundTab
    end tell
    '''
    
    try:
        result = subprocess.run(["osascript", "-e", applescript], 
                              capture_output=True, text=True, timeout=5)
        return result.stdout.strip() == "true"
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        print(f"AppleScript error: {e}")
        return False


def open_or_focus_browser_url(url, reuse_origin=False):
    """Open or focus on a URL in Google Chrome, optionally reusing tabs by origin."""
    
    if reuse_origin:
        target_origin = get_origin(url)
        print(f"Looking for existing tab with origin: {target_origin}")
        
        # Try to find and focus existing tab with same origin
        if find_and_focus_tab_by_origin(target_origin):
            print(f"Found existing tab with same origin, navigating to: {url}")
            # Navigate the existing tab to the new URL
            applescript = f'''
            tell application "Google Chrome"
                activate
                set URL of active tab of front window to "{url}"
            end tell
            '''
        else:
            print(f"No existing tab found with origin {target_origin}, creating new tab")
            # Create new tab
            applescript = f'''
            tell application "Google Chrome"
                activate
                open location "{url}"
            end tell
            '''
    else:
        # Simple approach - just open the URL (creates new tab)
        applescript = f'''
        tell application "Google Chrome"
            activate
            open location "{url}"
        end tell
        '''
    
    subprocess.run(["osascript", "-e", applescript])


def main():
    parser = argparse.ArgumentParser(
        description='Open URLs in Chrome with smart tab management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s https://example.com                    # Reuse tab with same origin (default)
  %(prog)s --no-reuse https://example.com         # Force new tab
  %(prog)s https://linear.app/page1 https://linear.app/page2  # Try multiple URLs, reuse origin
        '''
    )
    
    parser.add_argument('urls', nargs='+', help='URL(s) to open')
    parser.add_argument('--no-reuse', '-n', action='store_true',
                       help='Force new tab instead of reusing existing tabs with same origin')
    
    args = parser.parse_args()
    
    # Default behavior is now to reuse origin, unless --no-reuse is specified
    reuse_origin = not args.no_reuse
    
    # If only one URL is provided, open it directly
    if len(args.urls) == 1:
        open_or_focus_browser_url(args.urls[0], reuse_origin=reuse_origin)
        return
    
    # Otherwise, try each URL until one responds
    for url in args.urls:
        print(f"Checking {url}...")
        if check_url_availability(url):
            print(f"Found working URL: {url}")
            open_or_focus_browser_url(url, reuse_origin=reuse_origin)
            break
    else:  # This executes if the loop completes without breaking
        print("None of the provided URLs are responding.")
        # Optionally, you could still open the first URL even if it's not responding:
        print(f"Opening first URL anyway: {args.urls[0]}")
        open_or_focus_browser_url(args.urls[0], reuse_origin=reuse_origin)


if __name__ == "__main__":
    main()
