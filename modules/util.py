"""General utility functions."""

# Standard library imports
import time

# Local application imports
from . import NUM_COLUMNS


def scroll(lcd, text: str, row: int = 0, interval: float = 0.5, max_scrolls: int = None) -> None:
    """Renders the text on the LCD with a scrolling horizontal animation."""
    times_scrolled = 0
    stage = 0
    while max_scrolls is None or times_scrolled < max_scrolls:
        if stage > NUM_COLUMNS + len(text):
            stage = 1
            times_scrolled += 1
        fragment = text.rjust(len(text) + NUM_COLUMNS)[stage:]
        lcd.cursor_pos = (row, 0)
        # Ensure string doesn't exceed the maximum length
        lcd.write_string(fragment[:NUM_COLUMNS].ljust(NUM_COLUMNS))
        time.sleep(interval)
        stage += 1


if __name__ == "__main__":
    class LCD:  # pylint: disable=too-few-public-methods
        """Placeholder class for console demonstration."""
        write_string = print
    scroll(LCD, "hello world", interval=0.1, max_scrolls=3)
