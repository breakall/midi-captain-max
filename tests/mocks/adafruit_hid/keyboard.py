"""
Mock adafruit_hid.keyboard — records keyboard operations for test assertions.
"""

import sys
from pathlib import Path

# Import Keycode directly from the firmware library path to avoid circular
# dependency during conftest.py mock installation.
_LIB_PATH = str(Path(__file__).parent.parent.parent.parent / "firmware" / "dev" / "lib")
if _LIB_PATH not in sys.path:
    sys.path.insert(0, _LIB_PATH)

# Import the real Keycode from the firmware library (not from sys.modules["adafruit_hid.keycode"])
import importlib.util as _iutil
_spec = _iutil.spec_from_file_location(
    "_fw_keycode",
    Path(_LIB_PATH) / "adafruit_hid" / "keycode.py"
)
_fw_keycode = _iutil.module_from_spec(_spec)
_spec.loader.exec_module(_fw_keycode)
Keycode = _fw_keycode.Keycode


class Keyboard:
    """Mock Keyboard that records every press/release/send call."""

    def __init__(self, devices):
        self._devices = devices
        self._pressed = set()   # currently held keycodes
        self._calls = []        # ordered log: (method, *args)

    # ------------------------------------------------------------------
    # Public API (mirrors adafruit_hid.keyboard.Keyboard)
    # ------------------------------------------------------------------

    def press(self, *keycodes):
        for kc in keycodes:
            self._pressed.add(kc)
        self._calls.append(("press",) + tuple(keycodes))

    def release(self, *keycodes):
        for kc in keycodes:
            self._pressed.discard(kc)
        self._calls.append(("release",) + tuple(keycodes))

    def release_all(self):
        self._pressed.clear()
        self._calls.append(("release_all",))

    def send(self, *keycodes):
        self.press(*keycodes)
        self.release(*keycodes)
        # Replace the last two separate press/release log entries with a
        # single "send" entry for cleaner assertions.
        self._calls = self._calls[:-2]
        self._calls.append(("send",) + tuple(keycodes))

    # ------------------------------------------------------------------
    # Test helpers
    # ------------------------------------------------------------------

    def get_calls(self):
        return list(self._calls)

    def clear(self):
        self._pressed.clear()
        self._calls.clear()

    @property
    def is_pressed(self):
        return frozenset(self._pressed)
