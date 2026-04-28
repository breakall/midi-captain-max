"""
Keycode constants for USB HID keyboard usage page (0x01, Usage 0x06).

All constants match the USB HID Usage Tables specification and are compatible
with the Adafruit CircuitPython HID library's Keycode class.

Only keycodes referenced by the OEM SuperMode specification are defined here;
modifier keycodes (0xe0-0xe7) are included for use with Keyboard.press/send.
"""


class Keycode:
    """USB HID keyboard keycodes."""

    # --- Letters ---
    A = 0x04
    B = 0x05
    C = 0x06
    D = 0x07
    E = 0x08
    F = 0x09
    G = 0x0a
    H = 0x0b
    I = 0x0c  # noqa: E741
    J = 0x0d
    K = 0x0e
    L = 0x0f
    M = 0x10
    N = 0x11
    O = 0x12  # noqa: E741
    P = 0x13
    Q = 0x14
    R = 0x15
    S = 0x16
    T = 0x17
    U = 0x18
    V = 0x19
    W = 0x1a
    X = 0x1b
    Y = 0x1c
    Z = 0x1d

    # --- Digits ---
    ONE = 0x1e
    TWO = 0x1f
    THREE = 0x20
    FOUR = 0x21
    FIVE = 0x22
    SIX = 0x23
    SEVEN = 0x24
    EIGHT = 0x25
    NINE = 0x26
    ZERO = 0x27

    # --- Control keys ---
    ENTER = 0x28
    ESCAPE = 0x29
    BACKSPACE = 0x2a
    TAB = 0x2b
    SPACEBAR = 0x2c

    # --- Lock keys ---
    CAPS_LOCK = 0x39

    # --- Function keys ---
    F1 = 0x3a
    F2 = 0x3b
    F3 = 0x3c
    F4 = 0x3d
    F5 = 0x3e
    F6 = 0x3f
    F7 = 0x40
    F8 = 0x41
    F9 = 0x42
    F10 = 0x43
    F11 = 0x44
    F12 = 0x45

    # --- Navigation / editing ---
    PRINT_SCREEN = 0x46
    PAUSE = 0x48
    INSERT = 0x49
    HOME = 0x4a
    PAGE_UP = 0x4b
    DELETE = 0x4c
    END = 0x4d
    PAGE_DOWN = 0x4e
    RIGHT_ARROW = 0x4f
    LEFT_ARROW = 0x50
    DOWN_ARROW = 0x51
    UP_ARROW = 0x52

    # --- Modifier keycodes (0xe0-0xe7) ---
    # These are *keycodes*, not bit-flags.  The Keyboard class detects them and
    # sets the appropriate modifier byte bit rather than occupying a key slot.
    LEFT_CONTROL = 0xe0
    LEFT_SHIFT = 0xe1
    LEFT_ALT = 0xe2
    LEFT_GUI = 0xe3    # Windows / Meta / Command
    RIGHT_CONTROL = 0xe4
    RIGHT_SHIFT = 0xe5
    RIGHT_ALT = 0xe6
    RIGHT_GUI = 0xe7

    @staticmethod
    def modifier_bit(keycode):
        """Return the modifier byte bit for a modifier keycode, or 0 if not a modifier."""
        if 0xe0 <= keycode <= 0xe7:
            return 1 << (keycode - 0xe0)
        return 0
