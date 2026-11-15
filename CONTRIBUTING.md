# Contributing to TV Head

Contributions are welcome: bug reports, fixes, documentation, and new animations or
firmware features. This document covers the development workflow and the checks CI runs.

## Project layout

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
  common/loader.py      animation loader shared by ESP32 and Pico firmware
  Pico/                 Raspberry Pi Pico firmware
  ESP/                  ESP32 firmware
animations/             source frames, one directory per animation
tests/                  converter, loader, and configuration tests
```

## Development setup

1. Fork the repository and create a branch from `main`. A descriptive name is enough
   (`fix-diff-frames`, `pico-brightness`); there is no required prefix.
2. Create a virtual environment and install the dependencies, including pytest, Ruff,
   and Black:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Checks

Run these before opening a pull request; CI runs the same checks on Python 3.10 for
pushes and pull requests to `main`.

```bash
ruff check        # lint
black --check .   # formatting
pytest            # tests
```

To fix formatting instead of just checking it, run `black .`. Configuration for both
tools lives in `pyproject.toml` (line length 88, Ruff rules `E4`, `E7`, `E9`, `F`).

## Tests

Tests live in `tests/` and run against CPython; no hardware is required.

- `tests/test_converter.py` covers resizing, rotation, serpentine ordering, frame
  diffing, and a round trip from images through the generated JSON and the firmware
  loader.
- `tests/test_loader.py` covers the firmware loader's JSON and legacy CSV layouts.
- `tests/test_tvhead.py` covers imports (including the optional pygame dependency),
  configuration loading, transformations, and controller defaults.

Run a single file or test with:

```bash
pytest tests/test_converter.py
pytest tests/test_converter.py::test_unchanged_frames_are_empty
```

Write tests for behavior changes, especially anything that affects the generated JSON or
how the firmware replays it. Generated output goes to `json/`, which is gitignored; do
not commit converted animations.

## Firmware changes

The firmware under `onboard/` targets MicroPython and cannot be tested by CI.

- `onboard/common/loader.py` is imported by both firmwares and by the test suite. Keep
  it importable under CPython: it should stay limited to modules available in both
  environments (`os`, `json`, `gc`) and avoid MicroPython-only APIs.
- `onboard/Pico/rotary.py` is vendored from Mike Teachman's `micropython-rotary`. It is
  excluded from Ruff and Black, so do not reformat it.
- Test firmware changes on a real board when possible, and note the board and MicroPython
  version in the pull request.

## Pull requests

- Keep changes focused; separate unrelated refactors from behavior changes.
- Describe the behavior change and any effects on the JSON format or firmware, and link
  the relevant issue if one exists.
- Update `README.md` or `JSON_FORMAT.md` when commands, configuration, or the output
  format change.

## Reporting bugs

Include enough detail to reproduce the problem:

- Python version and operating system
- Board and MicroPython version, if the issue is on-device
- The command you ran and the relevant part of `tvhead.log`
- Expected behavior, actual behavior, and a minimal input that triggers it

## Security

Do not report security vulnerabilities through public issues. Email
`tadj.d.cazaubon@gmail.com` with a description, reproduction steps, and the potential
impact.

## License

By contributing, you agree that your contributions are licensed under the MIT License.
