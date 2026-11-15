"""
Tests for the firmware animation loader (onboard/common/loader.py).
"""

import json
import os

import pytest

from loader import get_animation_paths, read_frames


@pytest.fixture
def board(tmp_path):
    """Folder paths standing in for the board's /json/ and /csvs/."""
    return str(tmp_path / "json") + "/", str(tmp_path / "csvs") + "/"


def write_json(json_folder, name, frames):
    folder = f"{json_folder}{name}"
    os.makedirs(folder, exist_ok=True)
    with open(f"{folder}/{name}.json", "w") as f:
        json.dump({"metadata": {"name": name}, "frames": frames}, f)


def write_csvs(csv_folder, name, frames, line_end="\n"):
    folder = f"{csv_folder}{name}"
    os.makedirs(folder, exist_ok=True)
    for i, frame in enumerate(frames):
        lines = ["index,blue,green,red"] + [",".join(map(str, p)) for p in frame]
        with open(f"{folder}/{i:06d}.csv", "w", newline="") as f:
            f.write(line_end.join(lines) + line_end)


FRAMES = [[[0, 1, 2, 3], [5, 10, 20, 30]], [], [[5, 0, 0, 0]]]
EXPECTED = (((0, 1, 2, 3), (5, 10, 20, 30)), (), ((5, 0, 0, 0),))


def test_missing_folders_give_no_animations(board):
    assert get_animation_paths(*board) == ()


def test_json_and_csv_load_to_same_format(board):
    json_folder, csv_folder = board
    write_json(json_folder, "a", FRAMES)
    write_csvs(csv_folder, "b", FRAMES, line_end="\r\n")

    paths = get_animation_paths(json_folder, csv_folder)
    assert [read_frames(p) for p in paths] == [EXPECTED, EXPECTED]


def test_animations_sorted_by_name_across_layouts(board):
    json_folder, csv_folder = board
    write_json(json_folder, "b", FRAMES)
    write_csvs(csv_folder, "a", FRAMES)
    write_csvs(csv_folder, "c", FRAMES)

    paths = get_animation_paths(json_folder, csv_folder)
    assert paths == (f"{csv_folder}a", f"{json_folder}b/b.json", f"{csv_folder}c")


def test_json_wins_over_csv_with_same_name(board):
    json_folder, csv_folder = board
    write_json(json_folder, "smile", FRAMES)
    write_csvs(csv_folder, "smile", [[[9, 9, 9, 9]]])

    assert get_animation_paths(json_folder, csv_folder) == (
        f"{json_folder}smile/smile.json",
    )


def test_json_folder_without_its_file_is_skipped(board):
    json_folder, csv_folder = board
    os.makedirs(f"{json_folder}empty")
    assert get_animation_paths(json_folder, csv_folder) == ()


def test_csv_frames_read_in_filename_order(board):
    _, csv_folder = board
    write_csvs(csv_folder, "walk", [[[i, i, i, i]] for i in range(12)])
    frames = read_frames(f"{csv_folder}walk")
    assert [f[0][0] for f in frames] == list(range(12))


def test_csv_blank_lines_ignored(board):
    _, csv_folder = board
    os.makedirs(f"{csv_folder}x")
    with open(f"{csv_folder}x/000000.csv", "w") as f:
        f.write("index,blue,green,red\n1,2,3,4\n\n")
    assert read_frames(f"{csv_folder}x") == (((1, 2, 3, 4),),)
