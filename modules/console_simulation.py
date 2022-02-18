#!/usr/bin/env python3
"""Module for executing the code printing the output to the console instead of the LCD."""

# Standard library imports
import os
import random
import time

# Third party imports
from corny_commons import file_manager

# Local application imports
from . import NUM_ROWS, NUM_COLUMNS


class DummyAdafruitDHT:  # pylint: disable=too-few-public-methods
    """Placeholder class for the Adafruit_DHT module."""

    DHT22: int = 22

    # pylint: disable=no-self-use
    def read(self, _sensor: int = 0, _pin: int = 0) -> tuple[float, float]:
        """Generate random sample data."""
        humidity = random.randint(300, 600) / 10  # %
        temperature = random.randint(150, 350) / 10  # C
        # Sleep up to 0.5 seconds
        time.sleep(random.random() * 0.5)
        return humidity, temperature


class DummyGPIO:  # pylint: disable=too-few-public-methods
    """Placeholder class for the GPIO interface."""
    BCM: int = 0


class DummyLCD:
    """Placeholder class for the LCD."""

    def __init__(self, *_args, **_kwargs) -> None:
        self.cursor_pos = (0, 0)
        self._write = print
        self.celsius = "°C"
        top_row = f"┌{'─' * NUM_COLUMNS}┐\n"
        mid_row = f"│{' ' * NUM_COLUMNS}│\n"
        end_row = f"└{'─' * NUM_COLUMNS}┘"
        self._write(top_row + mid_row * NUM_ROWS + end_row, end="", flush=True)
        os.environ["CONSOLE_ENABLED"] = "TRUE"


    def write_string(self, text: str = "") -> None:
        """Writes the string to the console."""
        row, col = self.cursor_pos
        row = min(row, NUM_ROWS - 1)
        prev_line = "\033[F" * (NUM_ROWS - row)
        next_line = "\n" * (NUM_ROWS - row - 1)

        self._write(f"{prev_line}\033[{col + 2}G{text}{next_line}")
        col += len(text)
        self.cursor_pos = row, col


    def home(self) -> None:
        """Reset the cursor position to line 0, column 0."""
        self.cursor_pos = (0, 0)

    def clear(self) -> None:
        """Clears the previous output."""
        self.home()
        self.write_string()
        self.home()


    def close(self, clear: bool = False) -> None:
        """Flushes the output stream."""
        if clear:
            self.clear()


    def create_char(self, *_args, **_kwargs) -> None:
        """Placeholder method."""


if __name__ == "__main__":
    import main
    file_manager.log("Started program with forced dummy LCD & data!")
    main.main(DummyLCD(), DummyAdafruitDHT)
