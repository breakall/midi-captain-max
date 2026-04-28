"""
MIDI Captain boot.py

Runs once at device power-on/reset, before code.py.

CRITICAL: Autoreload is DISABLED for rock-solid live performance.
The device must NEVER reset unexpectedly during a gig. File changes
on the USB drive will not trigger reloads.

USB DRIVE — two modes, controlled by config.json:

  Performance Mode (default, dev_mode: false):
    Drive is hidden unless Switch 1 is held during boot.
    - Hold switch 1 (top-left) while powering on → USB drive appears
    - Release switch and reboot normally → USB hidden again

  Development Mode (dev_mode: true):
    Drive always mounts on boot — no switch needed.
    Convenient when iterating on firmware locally.

To reload after config/code changes:
- Send Ctrl+D over serial console
- Or power-cycle the device
"""

import board
import digitalio
import storage
import supervisor
import time

# DISABLED for live performance stability - no unexpected resets
# CP 7.x uses supervisor.disable_autoreload(), not runtime.autoreload
supervisor.disable_autoreload()

# Load config settings needed at boot time (drive name, dev mode, HID enable).
# boot.py runs before normal module search paths are established,
# so we add /core to sys.path explicitly.
usb_drive_name = "MIDICAPTAIN"  # Default fallback
dev_mode = False                # Default: performance mode
hid_enabled = False             # Default: HID not enabled
try:
    import sys
    sys.path.insert(0, "/core")
    from config import load_config, get_usb_drive_name, get_dev_mode

    cfg = load_config("/config.json")
    dev_mode = get_dev_mode(cfg)
    usb_drive_name = get_usb_drive_name(cfg)

    # Enable USB HID only if at least one button uses type="hid".
    # This keeps the USB descriptor clean for MIDI-only setups.
    for btn in cfg.get("buttons", []):
        if btn.get("type") == "hid":
            hid_enabled = True
            break
except Exception:
    # If config fails to load, use safe defaults (performance mode, no HID)
    pass

# Enable USB HID (keyboard + mouse) if any configured button uses type="hid".
# Must be called before USB is fully initialized; boot.py is the only place
# where usb_hid.enable() has any effect.
if hid_enabled:
    try:
        import usb_hid
        usb_hid.enable((usb_hid.Device.KEYBOARD, usb_hid.Device.MOUSE))
        print("🎹 USB HID enabled (keyboard + mouse)")
    except Exception as e:
        print(f"⚠️  USB HID enable failed: {e}")

# Check if user is holding a switch during boot.
# DUO2/ONE1 use GP11 (KEY0) because GP1 is a DIP switch on those devices.
# All other devices use GP1 (switch 1).
# With pull-up: LOW (False) = pressed, HIGH (True) = not pressed.
boot_switch_pin = board.GP1
try:
    _device = cfg.get("device", "") if cfg else ""
    if _device in ("duo2", "one1"):
        boot_switch_pin = board.GP11
except Exception:
    pass

switch_1 = digitalio.DigitalInOut(boot_switch_pin)
switch_1.direction = digitalio.Direction.INPUT
switch_1.pull = digitalio.Pull.UP
time.sleep(0.05)  # Allow pull-up to stabilize before reading

switch_held = not switch_1.value          # True when switch is pressed
enable_usb_drive = dev_mode or switch_held  # dev_mode overrides switch gate


# CRITICAL: disable_usb_drive() must be called BEFORE any USB initialization.
# Always check the disable condition first; remount() would initialize USB.
if not enable_usb_drive:
    # Performance mode - hide USB drive completely
    # Drive won't appear on computer, preventing remount issues
    try:
        storage.disable_usb_drive()
        print("🔒 USB drive disabled (hold switch 1 during boot to enable)")
    except Exception as e:
        print(f"⚠️  USB disable failed: {e}")

# If USB is enabled, apply the custom drive label.
# This runs AFTER the disable check so USB only initializes when needed.
if enable_usb_drive:
    mode_label = "DEV MODE" if dev_mode else "switch held"
    print(f"🔓 USB DRIVE ENABLED as '{usb_drive_name}' ({mode_label})")
    if not dev_mode:
        print("   Release switch and reboot to hide drive")
    try:
        # readonly=True: CircuitPython is read-only, USB host has write access
        # (needed for config editor to save files to the device)
        storage.remount("/", readonly=True, label=usb_drive_name)
    except TypeError:
        # CircuitPython 7.x doesn't support label=; skip remount so the USB
        # host retains default write access
        pass
    except Exception as e:
        print(f"⚠️  Drive label warning: {e}")

# Clean up - switch will be available again in code.py
switch_1.deinit()
