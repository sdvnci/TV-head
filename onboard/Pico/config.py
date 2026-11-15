from micropython import const
from loader import get_animation_paths, read_frames

# If debug is True, our debug lines throughtout the code will print.
# If debug is False, our debug lines will not print.
DEBUG: bool = True


def out01(x: str) -> None:
    """
    Print the given string.
    """
    print(x)


def out02(x: str) -> None:
    """
    Don't print the given string.
    This is a dummy function.
    """
    pass


debug = out01 if DEBUG else out02

# Variable to keep running script or not
RUNNING: bool = True

# Variables to define constant labels
BRIGHTNESS: str = const("Brightness")
CHANNEL: str = const("Channel")
SPEED: str = const("Speed")

# Pin number to address
P: int = const(16)
# Number of leds to address
N: int = const(100)

# Render variable values for playing animations.
RENDER_VALUES: dict[str, int | float] = {BRIGHTNESS: 0.1, SPEED: 1, CHANNEL: 0}


# Pre-load animations in a tuple.
animation_paths = get_animation_paths()
animation_amount = len(animation_paths)
animations = tuple(read_frames(file) for file in animation_paths)
