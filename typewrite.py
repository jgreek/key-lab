#!/usr/bin/env python3

import time
import argparse
from pynput import keyboard

def typewrite(text, press_enter=False, delay=0.01):
    """
    Types the given text using the keyboard controller and optionally presses Enter.

    Args:
        text (str): The text to type
        press_enter (bool): Whether to press Enter after typing the text
        delay (float): Delay between keypresses in seconds
    """
    controller = keyboard.Controller()

    # Wait a moment before typing to ensure the target application is ready
    time.sleep(0.2)

    # Type the text character by character
    for char in text:
        controller.press(char)
        controller.release(char)
        time.sleep(delay)  # Small delay between keypresses for stability

    # Press Enter if requested
    if press_enter:
        time.sleep(0.1)  # Small pause before pressing Enter
        controller.press(keyboard.Key.enter)
        controller.release(keyboard.Key.enter)

    print(f"Typed: {text}{' + Enter' if press_enter else ''}")

def main():
    parser = argparse.ArgumentParser(description='Type text using keyboard simulation')
    parser.add_argument('text', nargs='+', help='The text to type')
    parser.add_argument('-e', '--enter', action='store_true', help='Press Enter after typing')
    parser.add_argument('-d', '--delay', type=float, default=0.01, help='Delay between keypresses in seconds')

    args = parser.parse_args()

    # Join all text arguments into a single string
    text = ' '.join(args.text)

    typewrite(text, args.enter, args.delay)

if __name__ == "__main__":
    main()