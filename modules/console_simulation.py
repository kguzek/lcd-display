#!/usr/bin/env python3
"""Module for executing the code printing the output to the console instead of the LCD."""

# Standard library imports
import os
import random
import time

# Third party imports
from corny_commons import file_manager
from corny_commons.console_graphics import Display

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

    def cleanup():  # pylint:disable=no-method-argument
        """Dummy method that is called when the program terminates."""


class DummyLCD(Display):
    """Placeholder class for the LCD."""

    def __init__(self, *_args, **_kwargs) -> None:
        self.celsius = "°C"
        os.environ["CONSOLE_ENABLED"] = "TRUE"
        super().__init__(NUM_COLUMNS, NUM_ROWS)

    def create_char(self, *_args, **_kwargs) -> None:
        """Placeholder method."""


if __name__ == "__main__":
    import main

    file_manager.log("Started program with forced dummy LCD & data!")
    main.main(DummyLCD(), DummyAdafruitDHT)
