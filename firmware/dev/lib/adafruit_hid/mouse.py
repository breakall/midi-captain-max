"""
USB HID Mouse class for CircuitPython.

Sends standard 4-byte mouse reports via the usb_hid mouse device.
"""


class Mouse:
    """USB HID Mouse.

    Sends a 4-byte report [buttons, x, y, wheel] to the OS.
    Only button press/release is used by MIDI Captain; movement is not needed.

    Usage::

        import usb_hid
        from adafruit_hid.mouse import Mouse

        m = Mouse(usb_hid.devices)
        m.press(Mouse.LEFT_BUTTON)
        m.release(Mouse.LEFT_BUTTON)
    """

    LEFT_BUTTON = 0x01
    RIGHT_BUTTON = 0x02
    MIDDLE_BUTTON = 0x04

    def __init__(self, devices):
        """Initialise and locate the mouse HID device.

        Args:
            devices: Iterable of usb_hid.Device objects (usb_hid.devices).

        Raises:
            RuntimeError: if no mouse device is found.
        """
        self._mouse_device = None
        for device in devices:
            try:
                if device.usage_page == 0x01 and device.usage == 0x02:
                    self._mouse_device = device
                    break
            except Exception:
                pass
        if self._mouse_device is None:
            raise RuntimeError("No mouse HID device found.")
        # 4-byte report: [buttons, x, y, wheel]
        self._report = bytearray(4)

    def _send_report(self):
        self._mouse_device.send_report(bytes(self._report))

    def press(self, buttons):
        """Press one or more mouse buttons.

        Args:
            buttons: Bitmask of Mouse.LEFT_BUTTON / RIGHT_BUTTON / MIDDLE_BUTTON.
        """
        self._report[0] |= buttons & 0xff
        self._send_report()

    def release(self, buttons):
        """Release one or more mouse buttons.

        Args:
            buttons: Bitmask of Mouse.LEFT_BUTTON / RIGHT_BUTTON / MIDDLE_BUTTON.
        """
        self._report[0] &= ~buttons & 0xff
        self._send_report()
