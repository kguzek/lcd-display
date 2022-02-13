"""General utility functions."""

# Standard library imports
import time

# Third party imports
from RPLCD.gpio import CharLCD

# Local application imports
from . import NUM_COLUMNS


def scroll_text(lcd: CharLCD, text: str, row: int = 0, interval: float = 0.5,
                max_scrolls: int = None) -> None:
    """Renders the text on the LCD with a scrolling horizontal animation."""
    times_scrolled = 0
    stage = 0
    while True:
        if stage > NUM_COLUMNS + len(text):
            stage = 1
            times_scrolled += 1
        if max_scrolls is not None and times_scrolled >= max_scrolls:
            break
        fragment = text.rjust(len(text) + NUM_COLUMNS)[stage:]
        lcd.cursor_pos = (row, 0)
        # Ensure string doesn't exceed the maximum length
        lcd.write_string(fragment[:NUM_COLUMNS].ljust(NUM_COLUMNS))
        lcd.lf()
        time.sleep(interval)
        stage += 1


if __name__ == "__main__":
    scroll_text(CharLCD(), "hello world", interval=0.1, max_scrolls=3)
