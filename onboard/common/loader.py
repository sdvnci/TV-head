"""
Animation loading shared by the ESP and Pico firmware.
Copy this file onto the board next to main.py.

Two on-board layouts are supported:
    /json/<name>/<name>.json  - one file per animation, as written by the converter
    /csvs/<name>/*.csv        - legacy, one file per frame with a header line

Both store [index, blue, green, red] pixels as frame diffs, and are loaded
into the same tuple[tuple[tuple[int, int, int, int]]] format.

Only os.listdir/os.stat are used so this also runs under CPython for tests.
"""

from os import listdir, stat
from json import load
import gc

JSON_FOLDER: str = "/json/"
CSV_FOLDER: str = "/csvs/"

# Directory bit of st_mode
_DIR_FLAG = 0x4000


def _exists(file_path: str) -> bool:
    try:
        stat(file_path)
        return True
    except OSError:
        return False


def _subdirs(folder_path: str) -> list[str]:
    """
    Get the names of the folders within a folder.
    A missing folder has no subfolders.
    """
    try:
        names = listdir(folder_path)
    except OSError:
        return []
    return [name for name in names if stat(folder_path + name)[0] & _DIR_FLAG]


def get_animation_paths(
    json_folder: str = JSON_FOLDER, csv_folder: str = CSV_FOLDER
) -> tuple[str]:
    """
    Get a tuple of animation paths, sorted by animation name.
    json animations are file paths, csv animations are folder paths.
    If an animation exists in both layouts, the json version is used.
    """
    paths: dict[str, str] = {}
    for name in _subdirs(csv_folder):
        paths[name] = csv_folder + name
    for name in _subdirs(json_folder):
        file_path = json_folder + name + "/" + name + ".json"
        if _exists(file_path):
            paths[name] = file_path
    return tuple(paths[name] for name in sorted(paths))


def _read_json(file_path: str) -> tuple[tuple[tuple[int, int, int, int]]]:
    """
    Read the frames from an animation json file.
    """
    with open(file_path, "r", encoding="utf-8") as jsonfile:
        frames = load(jsonfile)["frames"]
    frames = tuple(tuple((p[0], p[1], p[2], p[3]) for p in frame) for frame in frames)
    gc.collect()
    return frames


def _read_csv_frame(file_path: str) -> tuple[tuple[int, int, int, int]]:
    """
    Read a single frame csv, skipping the header line and blank lines.
    """
    pixels = []
    with open(file_path, "r", encoding="utf-8") as csvfile:
        csvfile.readline()
        for line in csvfile:
            line = line.strip()
            if line:
                i, b, g, r = line.split(",")
                pixels.append((int(i), int(b), int(g), int(r)))
    return tuple(pixels)


def _read_csvs(folder_path: str) -> tuple[tuple[tuple[int, int, int, int]]]:
    """
    Read the frame csvs within an animation folder, in filename order.
    """
    return tuple(
        _read_csv_frame(folder_path + "/" + filename)
        for filename in sorted(listdir(folder_path))
        if filename.endswith(".csv")
    )


def read_frames(animation_path: str) -> tuple[tuple[tuple[int, int, int, int]]]:
    """
    Read the frames of an animation from either layout.
    """
    if animation_path.endswith(".json"):
        return _read_json(animation_path)
    return _read_csvs(animation_path)
