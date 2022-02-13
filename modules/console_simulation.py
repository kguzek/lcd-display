"""Module for executing the code printing the output to the console instead of the LCD."""

# Standard library imports
import random


class DummyAdafruitDHT:  # pylint: disable=too-few-public-methods
    """Placeholder class for the Adafruit_DHT module."""

    DHT22: int = 22

    def read_retry(self, _sensor: int = 0, _pin: int = 0) -> None:  # pylint: disable=no-self-use
        """Generate random sample data."""
        humidity = random.randint(30, 60)  # %
        temperature = random.randint(15, 35)  # C
        return humidity, temperature


class DummyGPIO:  # pylint: disable=too-few-public-methods
    """Placeholder class for the GPIO interface."""
    BCM: int = 0


class DummyLCD:
    """Placeholder class for the LCD."""

    def __init__(self, *_args, **_kwargs) -> None:
        pass


    def write_string(self, text: str) -> None:  # pylint: disable=no-self-use
        """Writes the string to the console."""
        print(text, end="")


    def placeholder(self, *_args, **_kwargs):
        """Placeholder method."""


    def lf(self):  # pylint: disable=invalid-name
        """Prints a linefeed (flushes the output stream)."""
        self.write_string("\n")

    clear = home = create_char = close = placeholder


if __name__ == "__main__":
    import main
    main.main(DummyLCD())
