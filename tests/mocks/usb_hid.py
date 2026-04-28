"""
Mock usb_hid module — simulates CircuitPython USB HID.

Provides mock keyboard and mouse HID devices whose send_report() calls are
recorded for inspection in tests.
"""


class MockHIDDevice:
    """Mock usb_hid.Device — records send_report() calls."""

    def __init__(self, usage_page, usage, name="MockHID"):
        self.usage_page = usage_page
        self.usage = usage
        self.name = name
        self._reports = []

    def send_report(self, report):
        self._reports.append(bytes(report))

    # Test helpers
    def get_reports(self):
        return list(self._reports)

    def clear(self):
        self._reports.clear()

    @property
    def last_report(self):
        return self._reports[-1] if self._reports else None


# Singleton device instances reused across tests
_KEYBOARD_DEVICE = MockHIDDevice(0x01, 0x06, "MockKeyboard")
_MOUSE_DEVICE = MockHIDDevice(0x01, 0x02, "MockMouse")

# usb_hid.devices — iterable list of active HID devices
devices = [_KEYBOARD_DEVICE, _MOUSE_DEVICE]


class _DeviceDescriptors:
    """Descriptors matching what boot.py passes to usb_hid.enable()."""
    KEYBOARD = MockHIDDevice(0x01, 0x06, "KeyboardDescriptor")
    MOUSE = MockHIDDevice(0x01, 0x02, "MouseDescriptor")


Device = _DeviceDescriptors()

_enabled = False


def enable(device_list):
    """Record that HID was enabled (no-op in tests)."""
    global _enabled
    _enabled = True


def reset():
    """Reset mock state between tests."""
    global _enabled
    _enabled = False
    _KEYBOARD_DEVICE.clear()
    _MOUSE_DEVICE.clear()
