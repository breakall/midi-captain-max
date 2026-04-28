"""
Mock adafruit_hid.mouse — records mouse button operations for test assertions.
"""


class Mouse:
    """Mock Mouse that records every press/release call."""

    LEFT_BUTTON = 0x01
    RIGHT_BUTTON = 0x02
    MIDDLE_BUTTON = 0x04

    def __init__(self, devices):
        self._devices = devices
        self._buttons = 0    # currently held button bitmask
        self._calls = []     # ordered log: (method, buttons)

    # ------------------------------------------------------------------
    # Public API (mirrors adafruit_hid.mouse.Mouse)
    # ------------------------------------------------------------------

    def press(self, buttons):
        self._buttons |= buttons & 0xff
        self._calls.append(("press", buttons))

    def release(self, buttons):
        self._buttons &= ~buttons & 0xff
        self._calls.append(("release", buttons))

    # ------------------------------------------------------------------
    # Test helpers
    # ------------------------------------------------------------------

    def get_calls(self):
        return list(self._calls)

    def clear(self):
        self._buttons = 0
        self._calls.clear()

    @property
    def held_buttons(self):
        return self._buttons
