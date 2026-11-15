"""
Converter tests, including a round trip through the firmware loader:
images -> converter json -> loader -> replayed LED buffer.
"""

import json

import cv2
import numpy as np
import pytest

from loader import get_animation_paths, read_frames
import tvlib.comparator as comparator_module
from tvlib.comparator import comparator, convert_dir
from tvlib.transformations import Rotation

RED = (0, 0, 255)
GREEN = (0, 255, 0)


def to_strip(img: np.ndarray) -> np.ndarray:
    """Flatten an image into serpentine LED order."""
    img = img.astype(int).copy()
    img[1::2] = img[1::2, ::-1]
    return img.reshape(-1, 3)


def replay(frames, pixel_count: int, loops: int = 2):
    """Play frames the way the firmware does, yielding the buffer per frame."""
    buf = np.zeros((pixel_count, 3), int)
    for _ in range(loops):
        buf[:] = 0
        for frame in frames:
            for i, b, g, r in frame:
                buf[i] = (b, g, r)
            yield buf.copy()


@pytest.fixture
def animation_dir(tmp_path, monkeypatch):
    """A working dir with animations/ and json/, as the converter expects."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "animations").mkdir()
    return tmp_path


def write_frames(folder, images, names):
    folder.mkdir(parents=True)
    for img, name in zip(images, names):
        cv2.imwrite(str(folder / name), img)


def test_unchanged_frames_are_empty():
    img = np.zeros((4, 4, 3), np.uint8)
    img[0, 0] = RED
    frames = comparator(np.array([img, img, img]), 4, 4)
    assert frames[0] == [(0, *RED)]
    assert frames[1] == [] and frames[2] == []


def test_first_frame_skips_black_pixels():
    img = np.zeros((4, 4, 3), np.uint8)
    img[3, 3] = GREEN
    frames = comparator(np.array([img]), 4, 4)
    # Row 3 is reversed in serpentine order, so (3, 3) is index 12
    assert [p[0] for p in frames[0]] == [12]


def test_resizes_to_target():
    img = np.zeros((20, 20, 3), np.uint8)
    img[:10] = RED
    frames = comparator(np.array([img]), 10, 10)
    assert len(frames[0]) == 50
    assert max(p[0] for p in frames[0]) < 100


def test_rotation_then_resize_on_non_square():
    # 40 wide x 20 tall, left half red; rotated it becomes 20 x 40, bottom half red
    img = np.zeros((20, 40, 3), np.uint8)
    img[:, :20] = RED
    frames = comparator(np.array([img]), 8, 16, Rotation.ROTATE_90)
    lit = sorted(p[0] for p in frames[0])
    assert lit == list(range(64, 128))


def test_frames_are_ordered_by_filename(animation_dir, monkeypatch):
    images = []
    for i in range(12):
        img = np.zeros((4, 4, 3), np.uint8)
        img.reshape(-1, 3)[i] = RED
        images.append(img)
    names = [f"frame-{i:04d}.png" for i in range(12)]
    write_frames(animation_dir / "animations" / "walk", images, names)

    # listdir order is filesystem dependent, so force a scrambled one
    real_listdir = comparator_module.listdir
    monkeypatch.setattr(
        comparator_module,
        "listdir",
        lambda p: sorted(real_listdir(p), key=lambda n: n[::-1]),
    )

    frames = convert_dir("walk", (4, 4))
    expected = [to_strip(img) for img in images]
    for got, want in zip(replay(frames, 16, loops=1), expected):
        assert np.array_equal(got, want)


def test_round_trip_through_firmware_loader(animation_dir):
    rng = np.random.default_rng(0)
    images = []
    for _ in range(8):
        img = np.zeros((6, 6, 3), np.uint8)
        mask = rng.random((6, 6)) < 0.3
        img[mask] = rng.integers(1, 256, (mask.sum(), 3))
        images.append(img)
    images.insert(4, images[3].copy())  # an unchanged frame
    write_frames(
        animation_dir / "animations" / "noise",
        images,
        [f"f{i:03d}.png" for i in range(len(images))],
    )

    assert convert_dir("noise", (6, 6)) is not None
    data = json.loads((animation_dir / "json/noise/noise.json").read_text())
    assert data["metadata"]["frame_count"] == len(images)

    (path,) = get_animation_paths(
        str(animation_dir / "json") + "/", str(animation_dir / "csvs") + "/"
    )
    frames = read_frames(path)
    expected = [to_strip(img) for img in images] * 2
    for got, want in zip(replay(frames, 36), expected, strict=True):
        assert np.array_equal(got, want)
