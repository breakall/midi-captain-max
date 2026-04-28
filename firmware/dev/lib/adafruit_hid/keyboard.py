"""
USB HID Keyboard class for CircuitPython.

Sends standard 8-byte keyboard reports via the usb_hid keyboard device.
"""

from adafruit_hid.keycode import Keycode


class Keyboard:
    """USB HID Keyboard.

    Manages an 8-byte keyboard report (modifier byte + reserved + 6 key slots)
    and sends it to the OS via the usb_hid keyboard device whenever a key is
    pressed or released.

    Usage::

        import usb_hid
        from adafruit_hid.keyboard import Keyboard
        from adafruit_hid.keycode import Keycode

        kbd = Keyboard(usb_hid.devices)
        kbd.send(Keycode.A)               # type 'a'
        kbd.send(Keycode.LEFT_SHIFT, Keycode.A)  # type 'A'
        kbd.press(Keycode.LEFT_CONTROL, Keycode.S)   # hold Ctrl+S
        kbd.release_all()                # release everything
    """

    def __init__(self, devices):
        """Initialise and locate the keyboard HID device.

        Args:
            devices: Iterable of usb_hid.Device objects (usb_hid.devices).

        Raises:
            RuntimeError: if no keyboard device is found.
        """
        self._keyboard_device = None
        for device in devices:
            try:
                if device.usage_page == 0x01 and device.usage == 0x06:
                    self._keyboard_device = device
                    break
            except Exception:
                pass
        if self._keyboard_device is None:
            raise RuntimeError("No keyboard HID device found.")
        # 8-byte report: [modifier, reserved, key1..key6]
        self._report = bytearray(8)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _send_report(self):
        self._keyboard_device.send_report(bytes(self._report))

    def _press_keycode(self, keycode):
        """Add a keycode to the current report (modifier or key slot)."""
        mod_bit = Keycode.modifier_bit(keycode)
        if mod_bit:
            self._report[0] |= mod_bit
        else:
            for i in range(2, 8):
                if self._report[i] == 0:
                    self._report[i] = keycode
                    break

    def _release_keycode(self, keycode):
        """Remove a keycode from the current report."""
        mod_bit = Keycode.modifier_bit(keycode)
        if mod_bit:
            self._report[0] &= ~mod_bit & 0xff
        else:
            for i in range(2, 8):
                if self._report[i] == keycode:
                    self._report[i] = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def press(self, *keycodes):
        """Press one or more keys (add to held-key report).

        Args:
            *keycodes: One or more Keycode constants.
        """
        for keycode in keycodes:
            self._press_keycode(keycode)
        self._send_report()

    def release(self, *keycodes):
        """Release one or more keys.

        Args:
            *keycodes: One or more Keycode constants.
        """
        for keycode in keycodes:
            self._release_keycode(keycode)
        self._send_report()

    def release_all(self):
        """Release all currently held keys and modifiers."""
        for i in range(8):
            self._report[i] = 0
        self._send_report()

    def send(self, *keycodes):
        """Press and immediately release one or more keys.

        Args:
            *keycodes: One or more Keycode constants.
        """
        self.press(*keycodes)
        self.release(*keycodes)
