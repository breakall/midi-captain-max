"""
Mock adafruit_hid.keycode — re-exports the real Keycode constants.

The keycode.py in firmware/dev/lib/adafruit_hid/ defines all constants; the
mock simply imports and re-exports them so tests resolve the same values.
"""

import sys
import importlib.util
from pathlib import Path

_LIB_PATH = Path(__file__).parent.parent.parent.parent / "firmware" / "dev" / "lib"
_spec = importlib.util.spec_from_file_location(
    "_fw_keycode",
    _LIB_PATH / "adafruit_hid" / "keycode.py"
)
_fw_keycode = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fw_keycode)
Keycode = _fw_keycode.Keycode

__all__ = ["Keycode"]
