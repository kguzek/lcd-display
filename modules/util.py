"""General utility functions."""

# Standard library imports
import os
import time

# Third party imports
try:
    from RPLCD.gpio import CharLCD
except ModuleNotFoundError:
    from .console_simulation import DummyLCD as CharLCD

# Local application imports
from . import NUM_COLUMNS


# Boolean indicating whether or not the data update threads should be active
PROGRAM_IS_RUNNING = True

# The original signal handler for when the user sends the EOF macro
ORIGINAL_SIGTSTP_HANDLER = None


job_details = {
    "page": 0,
    "scrolling": False,
    "displaying_info": False,
    "texts_to_scroll": [None, None],
    "scroll_stage": 0
}


def scroll_text(lcd: CharLCD, interval: float = 0.5,
                max_scrolls: int = None) -> None:
    """Renders the text on the LCD with a scrolling horizontal animation."""
    times_scrolled = 0
    while PROGRAM_IS_RUNNING:
        texts = job_details["texts_to_scroll"]
        for text in texts:
            if text is None:
                continue
            while job_details["displaying_info"] or not PROGRAM_IS_RUNNING:
                # Check if the program was terminated before this cycle's completion
                if not PROGRAM_IS_RUNNING:
                    return
            stage = job_details["scroll_stage"]
            if stage > NUM_COLUMNS + len(text):
                stage = 1
                times_scrolled += 1
            if max_scrolls is not None and times_scrolled >= max_scrolls:
                break
            fragment = text.rjust(len(text) + NUM_COLUMNS)[stage:]
            job_details["scrolling"] = True
            lcd.cursor_pos = (texts.index(text), 0)
            # Ensure string doesn't exceed the maximum length
            lcd.write_string(fragment[:NUM_COLUMNS].ljust(NUM_COLUMNS))
            job_details["scrolling"] = False

            stage += 1
            job_details["scroll_stage"] = stage

            if os.environ.get("CONSOLE_ENABLED"):
                # Use faster scrolling for console (10 characters per second)
                time.sleep(0.1)
            else:
                # Use slower scrolling for LCD (defaults to 2 characters per second)
                time.sleep(interval)


if __name__ == "__main__":
    job_details["texts_to_scroll"][0] = "hello world"
    scroll_text(CharLCD(), max_scrolls=3)
