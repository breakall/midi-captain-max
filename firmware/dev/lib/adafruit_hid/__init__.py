"""
adafruit_hid — USB HID keyboard and mouse library for CircuitPython.

Minimal implementation for MIDI Captain MAX firmware, compatible with
CircuitPython 7.x on RP2040.  Provides Keyboard, Mouse, and Keycode.

Only the features needed by MIDI Captain are implemented:
  - Keyboard.send() / press() / release() / release_all()
  - Mouse.press() / release()
  - Keycode constants for OEM SuperMode key names

USB HID report formats used:
  Keyboard: 8 bytes [modifier_byte, 0x00, key1..key6]
  Mouse:    4 bytes [buttons, x, y, wheel]

Modifier byte bits (keyboard report byte 0):
  0x01 Left Ctrl   0x10 Right Ctrl
  0x02 Left Shift  0x20 Right Shift
  0x04 Left Alt    0x40 Right Alt
  0x08 Left GUI    0x80 Right GUI

Modifier keycodes (0xe0-0xe7) are automatically promoted to modifier-byte
bits rather than occupying a key slot.

Author: Max Cascone
Date: 2026-04-28
"""
