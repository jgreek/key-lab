import time
from pynput import keyboard


class KeyTracker:
    def __init__(self, combo_timeout=5.0, max_combo_length=3):
        self.combo_timeout = combo_timeout
        self.max_combo_length = max_combo_length
        self.last_keys = []
        self.last_key_times = []
        self.cmd_pressed = False
        self.shift_pressed = False
        self.option_pressed = False

    def cleanup_old_keys(self, current_time):
        while (self.last_key_times and
               current_time - self.last_key_times[0] > self.combo_timeout):
            self.last_keys.pop(0)
            self.last_key_times.pop(0)

    def add_key(self, char):
        current_time = time.time()
        self.cleanup_old_keys(current_time)

        self.last_keys.append(char)
        self.last_key_times.append(current_time)

        if len(self.last_keys) > self.max_combo_length:
            self.last_keys.pop(0)
            self.last_key_times.pop(0)

    def get_current_combo(self):
        return ''.join(self.last_keys)

    def clear_combo(self):
        self.last_keys.clear()
        self.last_key_times.clear()

    def set_modifier_state(self, key, pressed):
        if key == keyboard.Key.cmd:
            self.cmd_pressed = pressed
        elif key == keyboard.Key.shift:
            self.shift_pressed = pressed
        elif key == keyboard.Key.alt:
            self.option_pressed = pressed

    def backspace_combo(self, count):
        controller = keyboard.Controller()
        for _ in range(count):
            controller.press(keyboard.Key.backspace)
            controller.release(keyboard.Key.backspace)