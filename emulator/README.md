# Emulator Testing (Wokwi)

Headless firmware testing using **Wokwi CLI** — runs actual CircuitPython 7.3.3 on a simulated RP2040.

## How it works

`wokwi-cli` uploads a UF2 to Wokwi's cloud simulator and streams serial output back. The key challenge: the CLI does **not** inject project files into CircuitPython's flash filesystem (that's a browser-only feature). The solution is an **all-in-one UF2** that bundles the CP runtime + a FAT12 filesystem containing our firmware.

`build-uf2.py` creates this bundle:
1. Formats a 1MB FAT12 image using `pyfatfs` (pure Python, cross-platform)
2. Populates it with `code.py`, `boot.py`, `config.json`, `core/`, `devices/`, `lib/`, `fonts/`
3. Converts the FAT image to UF2 blocks at flash offset `0x10100000`
4. Concatenates with the CircuitPython 7.3.3 firmware UF2

## Usage

```bash
pip install pyfatfs                         # one-time
./emulator/setup.sh                         # downloads CP UF2, builds firmware-bundle.uf2
export WOKWI_CLI_TOKEN=your_token           # from https://wokwi.com/dashboard/ci
./emulator/test.sh                          # automated: --expect-text "MIDI CAPTAIN" --fail-text "Traceback"
./emulator/run.sh                           # interactive
```

## Directory layout

```
emulator/
├── build-uf2.py          # Builds all-in-one UF2 (requires pyfatfs)
├── setup.sh              # Downloads CP UF2, runs build-uf2.py
├── test.sh               # wokwi-cli automated test
├── run.sh                # wokwi-cli interactive mode
├── wokwi.toml            # Points firmware at firmware-bundle.uf2
├── diagram.json          # STD10 hardware model for Wokwi simulator
├── test-boot.yaml        # Automation scenario (button press simulation, alpha)
├── configs/              # Test configs using correct firmware schema
├── firmware-bundle.uf2   # Generated — gitignored
└── circuitpython.uf2     # Downloaded — gitignored
```

## What it can and cannot test

**Can test:** firmware boot, config loading/parsing, device detection, button/encoder/expression init, MIDI message sending, display init (font loading), main loop execution.

**Cannot test:** NeoPixel/display visual rendering, GP23/24/25 buttons (internal Pico pins not exposed in Wokwi), real USB MIDI communication.

## Gotchas

- **`wokwi-cli` requires `firmware` field** in `wokwi.toml` — hard requirement for CircuitPython
- **GP23, GP24, GP25 are not available** on Wokwi's `wokwi-pi-pico` — valid pins are GP0–GP22 and GP26–GP28. The MIDI Captain PCB uses these internal pins for 3 switches; they can't be wired in the diagram but the firmware runs fine (switches float HIGH with pull-ups)
- **NeoPixel part type** is `wokwi-neopixel`; pins are `DIN`/`DOUT`/`VDD`/`VSS` (not `VCC`/`GND`)
- **CircuitPython filesystem is read-only from serial** — `storage.remount()` fails with `Cannot remount '/' when visible via USB` unless called from `boot.py` before USB init. This is why file injection via mpremote/REPL doesn't work.
- **`pyfatfs` API**: must create the image file first (`f.truncate(size)`), then call `PyFat.mkfs()`, then open with `PyFatFS()`. There is no `create=True` parameter.
- **UF2 block renumbering**: when concatenating two UF2s, all `block_no` and `total_blocks` fields must be rewritten across both halves
- **Free tier**: 50 CI minutes/month — sufficient for weekly runs, not per-push. Pro is $25/seat/mo for 2,000 minutes.
- **`rp2040js-circuitpython` is a dead end** — has no CLI argument parsing, no `--image`/`--fs` flags, no filesystem injection. PR #33 was based on non-existent features.
