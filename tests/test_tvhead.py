"""
Basic checks that the project imports and its configuration loads.
"""

import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from tvlib import Config, Flip, Rotation
from controller import ImageSettings, TVHeadController

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def in_repo_root(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)


def test_tvlib_imports_without_pygame():
    # pygame is optional: only sprite_to_array needs it
    code = (
        "import sys; sys.modules['pygame'] = None; "
        "import tvlib, controller; "
        "assert 'tvlib.sprites' not in sys.modules"
    )
    subprocess.run([sys.executable, "-c", code], cwd=REPO_ROOT, check=True)


def test_config_loads(in_repo_root):
    assert Config.load()
    width, height = Config.resolution()
    assert isinstance(width, int) and isinstance(height, int)
    assert width > 0 and height > 0


def test_rotation_swaps_dimensions():
    img = np.zeros((2, 3, 3), dtype=np.uint8)
    assert Rotation.ROTATE_90(img).shape == (3, 2, 3)
    assert Rotation.ROTATE_270(img).shape == (3, 2, 3)
    assert Rotation.ROTATE_180(img).shape == (2, 3, 3)
    assert Rotation.NONE(img) is img


def test_flip():
    img = np.arange(6, dtype=np.uint8).reshape(1, 6, 1).repeat(3, axis=2)
    flipped = Flip.VERTICAL_FLIP(img)
    assert flipped[0, 0, 0] == 5 and flipped[0, 5, 0] == 0


def test_controller_defaults():
    settings = ImageSettings()
    assert settings.rotation is Rotation.NONE
    assert settings.flip is Flip.NONE
    assert TVHeadController().settings == settings
