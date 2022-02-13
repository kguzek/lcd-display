"""Module for executing the code printing the output to the console instead of the LCD."""

# Standard library imports
import os
import random
import time

class DummyAdafruitDHT:  # pylint: disable=too-few-public-methods
    """Placeholder class for the Adafruit_DHT module."""

    DHT22: int = 22

    def read_retry(self, _sensor: int = 0, _pin: int = 0) -> None:  # pylint: disable=no-self-use
        """Generate random sample data."""
        humidity = random.randint(300, 600) / 10  # %
        temperature = random.randint(150, 350) / 10  # C
        time.sleep(random.random() * 2)

        return humidity, temperature


class DummyGPIO:  # pylint: disable=too-few-public-methods
    """Placeholder class for the GPIO interface."""
    BCM: int = 0


class DummyLCD:
    """Placeholder class for the LCD."""

    def __init__(self, *_args, **_kwargs) -> None:
        self.cursor_pos = (0, 0)
        self._write = print
        top_row = f"┌{'─' * 16}┐\n"
        mid_row = f"│{' ' * 16}│\n"
        end_row = f"└{'─' * 16}┘"
        self._write(top_row + mid_row * 2 + end_row, end="", flush=True)
        os.environ["CONSOLE_ENABLED"] = "TRUE"


    def write_string(self, text: str = "") -> None:
        """Writes the string to the console."""
        row, col = self.cursor_pos
        prev_line = "\033[F" * (2 - row)
        next_line = "\n" * (1 - row)

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
    main.main(DummyLCD(), DummyAdafruitDHT)
