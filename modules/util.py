"""General utility functions."""

# Standard library imports
import asyncio

# Local application imports
from . import NUM_COLUMNS


async def scroll_text(lcd, text: str, row: int = 0, max_num_scrolls: int = 3,
                      interval: float = 0.5) -> None:
    """Renders the text on the LCD with a scrolling horizontal animation."""
    times_scrolled = 0

    async def _scroll(stage: int = 1):
        """Recursive function that progresses through the string's characters one by one."""
        nonlocal times_scrolled
        if stage > NUM_COLUMNS + len(text):
            stage = 1
            times_scrolled += 1
        # Infinite max times scrolled if less than or equal to 0
        if times_scrolled >= max_num_scrolls > 0:
            return
        fragment = text.rjust(len(text) + NUM_COLUMNS)[stage:]
        lcd.cursor_pos = (row, 0)
        # Ensure string doesn't exceed the maximum length
        lcd.write_string(fragment[:NUM_COLUMNS].ljust(NUM_COLUMNS))
        await asyncio.sleep(interval)
        await _scroll(stage + 1)

    await _scroll()


if __name__ == "__main__":
    class LCD:  # pylint: disable=too-few-public-methods
        """Placeholder class for console demonstration."""
        write_string = print

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(scroll_text(LCD, "hello world", interval=0.1))
