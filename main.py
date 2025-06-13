#!/usr/bin/env python3
"""
MacKeyListener - A configurable keyboard shortcut manager for macOS
"""

from mac_key_listener import MacKeyListener

if __name__ == "__main__":
    mac_listener = MacKeyListener()
    mac_listener.start()
