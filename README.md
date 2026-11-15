# TV Head

[![CI](https://github.com/sdvnci/TV-head/actions/workflows/linting.yml/badge.svg?branch=main)](https://github.com/sdvnci/TV-head/actions/workflows/linting.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

TV Head is an LED matrix display worn as part of a TV-head cosplay build. This repository
contains the desktop converter that turns image sequences into compact animation files,
the JSON format those files use, and MicroPython firmware that plays them on an ESP32 or
Raspberry Pi Pico with a NeoPixel/WS2812 strip.

## How it works

1. Place one image per frame in `animations/<name>/`, named so that sorted order is the
   playback order (`eyes-0000.png`, `eyes-0001.png`, ...).
2. Run the converter. It resizes each frame to the configured resolution, applies
   rotation and flip, reorders pixels for serpentine strip wiring, and writes
   `json/<name>/<name>.json`.
3. Copy the firmware and the `json/` directory to the board. Animations play in name
   order.

The first frame stores every lit pixel. Each following frame stores only the pixels that
changed, so unchanged frames are empty lists and repetitive animations stay small.

## Gallery

| Animation preview | Wearing the display | LED matrix detail |
|:-----------------:|:-------------------:|:-----------------:|
| <img src="media/IMG_0134.gif" width="250" alt="Animation preview"> | <img src="media/IMG_9166.jpg" width="250" alt="Wearing the display"> | <img src="media/IMG_0185.jpg" width="250" alt="LED matrix detail"> |

## Requirements

- Python 3.10+
- OpenCV, NumPy, and `toml` (`pip install -r requirements.txt`)
- A MicroPython board with a NeoPixel strip for playback
- [`mpremote`](https://docs.micropython.org/en/latest/reference/mpremote.html) to copy
  files to the board (optional)

## Installation

```bash
git clone https://github.com/sdvnci/TV-head.git
cd TV-head
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The optional sprite-sheet helper in `tvlib/sprites.py` requires `pygame`
(`pip install pygame`); it is not used by the command-line converter.

## Configuration

`conf.toml` holds the display resolution and the target board:

```toml
[resolution]
width = 10
height = 10

[target]
board = "raspberry pi pico"
```

Accepted board names: `esp32`, `esp32s2`, `esp32s3`, `esp32c3`, `raspberry pi 3`,
`raspberry pi 4`, `raspberry pi pico`, `raspberry pi pico 2`.

The converter reads `conf.toml` from the working directory. Rotation and flip are chosen
per run through the interactive prompts and are not written back to the file.

## Usage

```bash
# Interactive: choose image mode, rotation, and flip, then convert
python main.py

# Convert every animation using conf.toml
python main.py --convert-all

# Convert a single animation folder
python main.py --convert-dir eyes

# Choose rotation and flip interactively, then convert everything
python main.py --configure --convert-all

# Enable debug logging
python main.py --convert-all --verbose
```

| Option | Description |
|--------|-------------|
| `-c`, `--configure` | Prompt for image mode, rotation, and flip before converting |
| `-a`, `--convert-all` | Convert every folder in `animations/` |
| `-d DIR`, `--convert-dir DIR` | Convert a single folder in `animations/` |
| `-v`, `--verbose` | Enable debug logging |
| `--config-file PATH` | Accepted but not yet implemented; `conf.toml` is always used |

Results are written to `json/<name>/<name>.json`. A log of each run is written to
`tvhead.log` in the working directory.

## Output format

Each pixel is stored as `[index, blue, green, red]`, where `index` is the pixel's position
in the flattened LED strip:

```json
{
  "metadata": {
    "name": "eyes",
    "width": 10,
    "height": 10,
    "total_pixels": 100,
    "frame_count": 3,
    "format": "bgr",
    "type": "diff"
  },
  "frames": [
    [[0, 0, 0, 255], [1, 0, 255, 0]],
    [[1, 255, 128, 0]],
    []
  ]
}
```

Black pixels are omitted from the first frame. Later frames contain every changed pixel,
including pixels that changed to black, so that the board can clear them. Frame indices
follow the serpentine wiring of the strip, so every second row is reversed. See
[JSON_FORMAT.md](JSON_FORMAT.md) for the full specification and the index mapping.

The converter reads still images through OpenCV (PNG, JPEG, BMP, WebP, and similar).
Animated GIFs are not expanded into frames; export the frames as individual images first.

## Installing on the board

Both firmwares use the shared loader in `onboard/common/loader.py`.

Raspberry Pi Pico:

```bash
mpremote cp onboard/Pico/*.py onboard/common/loader.py :
mpremote cp -r json :
```

ESP32:

```bash
mpremote cp onboard/ESP/main.py onboard/common/loader.py :
mpremote cp -r json :
```

LED pin and LED count are constants at the top of `onboard/Pico/config.py` and
`onboard/ESP/main.py`; adjust them for your wiring before flashing.

Animations are sorted by name. The loader also reads the legacy
`/csvs/<name>/*.csv` layout (one CSV per frame); if an animation exists in both layouts,
the JSON version is used.

## Repository layout

```
main.py                 command-line entry point
controller.py           interactive setup flow
ui.py                   terminal menus used by the setup flow
conf.toml               resolution and target board
tvlib/
  comparator.py         image-to-frame conversion and JSON output
  transformations.py    rotation and flip helpers
  sprites.py            sprite-sheet splitting (optional, requires pygame)
  _config.py            configuration loading
  _boards.py            supported board names
  _fileio.py            file and path helpers
onboard/
  common/loader.py      animation loader shared by both firmwares
  Pico/                 Raspberry Pi Pico firmware (MPU6050, rotary encoder)
  ESP/                  ESP32 firmware
animations/             source frames, one directory per animation
json/                   generated output (gitignored)
tests/                  converter and firmware-loader tests
```

## Development

```bash
pip install -r requirements.txt

pytest            # run the test suite
ruff check        # lint
black --check .   # formatting
```

CI runs these checks on Python 3.10 for pushes and pull requests to `main`. See
[CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

Released under the MIT License. See [LICENSE](LICENSE).
