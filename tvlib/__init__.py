"""
TV Head Library

A library for processing and displaying images on LED matrix displays
for TV Head cosplay projects.
"""

from .transformations import Rotation, Flip
from ._config import Config
from .comparator import convert_all, convert_dir, convert_images

__version__ = "1.0.0"
__author__ = "Tadj Cazaubon"

__all__ = [
    "Rotation",
    "Flip",
    "Config",
    "convert_all",
    "convert_dir",
    "convert_images",
    "sprite_to_array",
]


def __getattr__(name):
    # sprites needs pygame, an optional dependency, so only import it on use
    if name == "sprite_to_array":
        from .sprites import sprite_to_array

        return sprite_to_array
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
