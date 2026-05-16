# MIDI Captain Migration and Tempo Tap/Tuner Log

Date: 2026-05-16

## Summary

Migrated the connected USB MIDI Captain STD10 from OEM/SuperMode-style firmware to `midi-captain-max` firmware from `firmware/dev`, created a full backup of the OEM device contents, enabled `dev_mode`, validated automatic remount + write access, assigned the top-right STD10 button to the new `tempo_tap` mode, tested the resulting MIDI output against MainStage, and refined the firmware so a short press turns tuner off when tuner is already on.

## Device and Backup

- Detected mounted device: `/Volumes/MIDICAPTAIN`
- Inferred device type: `std10`
- OEM backup created at:
  `/Users/neo/Documents/midi-captain-max/midi-captain-backup-2026-05-16`

## Migration Notes

- Initial deploy flow exposed environment issues:
  - `pip` was not on `PATH` for the deploy script
  - installing `circup` via system Python hit environment policy restrictions
  - device writes required escalated access to `/Volumes/MIDICAPTAIN`
- First scripted deploy partially completed, so remaining required firmware files were copied manually to reach a coherent on-device state.
- Final device state after migration:
  - MIDI Captain MAX `boot.py`
  - MIDI Captain MAX `code.py`
  - on-device `config.json` with `device: "std10"`
  - `dev_mode: true`
  - `VERSION.txt` fixed as a real file containing `v1.11.0-1-g1701a65`

## Dev Mode Validation

Validated that:

- the device remounts automatically with no switch held
- the volume remains writable from the host
- this provides a usable iteration loop for config and firmware updates

## Tempo Tap / Tuner Button Assignment

Updated the on-device `config.json` so STD10 switch 5 (top row, far right; user labels it with an up arrow) uses:

```json
{
  "label": "TAP",
  "type": "tempo_tap",
  "color": "white",
  "tempo_tap_cc": 63,
  "tempo_tap_value": 127,
  "tempo_tuner_cc": 68,
  "tempo_tuner_on": 127,
  "tempo_tuner_off": 0,
  "tempo_long_press_ms": 700
}
```

## MainStage Validation

Confirmed with serial monitoring and live testing:

- short press sends `CC63=127`
- first long press after boot sends `CC68=127`
- next long press sends `CC68=0`
- MainStage mapping worked correctly for tap tempo and tuner toggle

## Firmware Follow-Up Change

After MainStage testing, the desired behavior changed:

- if tuner is already on, a short press should turn tuner off immediately

Implemented that in firmware by changing the `TempoTapState` release behavior and the `tempo_tap` runtime handling:

- when tuner is off:
  - short press => tap tempo
- when tuner is on:
  - short press => send tuner off

Updated files:

- `firmware/dev/core/button.py`
- `firmware/dev/code.py`
- `tests/test_button_state.py`

## Test Results

Created a local Python 3.12 virtualenv `.venv312` and ran the targeted suite:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv312/bin/python -m pytest -q tests/test_button_state.py tests/test_config.py tests/test_schema.py
```

Result:

- `201 passed`

## Final Verified Behavior

With the updated firmware on the device:

- long press on switch 5 sends tuner on:
  - `CC68=127`
- short press while tuner is on sends tuner off:
  - `CC68=0`
- short press while tuner is off sends tap tempo:
  - `CC63=127`

## Remaining Notes

- The startup banner still prints button 5 as a simple CC button (`CC24 (TAP)`), which is only a display/logging inconsistency. Runtime behavior is correct.
- LED blinking currently depends on incoming MIDI Clock from the host. Tap tempo alone does not start local LED blink.
