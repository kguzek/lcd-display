"""General utility functions."""

# pyright: reportMissingImports=false

# Standard library imports
import time

# Third party imports
try:
    from RPLCD.gpio import CharLCD
except ModuleNotFoundError:
    from .console_simulation import DummyLCD as CharLCD

# Local application imports
from . import NUM_COLUMNS, SENSOR_PIN, systemp


# Boolean indicating whether or not the data update threads should be active
PROGRAM_IS_RUNNING = True

# The original signal handler for when the user sends the EOF macro
ORIGINAL_SIGTSTP_HANDLER = None

PAGE_TITLES = ["Temperature & Humidity", "System Temperature"]
TIME_PER_TEMPERATURE_UPDATE = 2  # seconds
TIME_PER_CHARACTER_SCROLL = 650  # milliseconds


def centred(text: str, span_entire_line: bool = True) -> str:
    """Returns a string with the left and right sides padded with the correct number of spaces."""
    # The number of spaces that should be on either side of the string
    padding = (NUM_COLUMNS - len(text)) // 2
    # Make the string a total length of left space + original length
    _centred = text.rjust(padding + len(text))
    if span_entire_line:
        # Make the string the length of the entire line
        return _centred.ljust(NUM_COLUMNS)
    # file_manager.log(f"Centred text: '{_centred}'")
    return _centred


def rerender_display(lcd: CharLCD, adafruit) -> None:
    """Keeps the LCD display contents updated."""
    scroll_stage = current_page = last_temperature_update = last_scroll_update = 0

    def rerender_temperature() -> None:
        """Render either the sensor temperature or the system temperature."""
        if current_page == 0:
            text = get_sensor_temperature()
        else:
            sys_temp = systemp.get_system_temperature()
            # Mark the temperature as unknown if there was an error while retrieving
            text = None if sys_temp is None else f"{sys_temp:0.01f}{lcd.celsius}"
        # Don't update the display if the temperature was not retrieved
        if text is None:
            return
        lcd.cursor_pos = (1, 0)
        lcd.write_string(centred(text))

    def get_sensor_temperature() -> str | None:
        """Reads the values from the GPIO-connected humidity and temperature sensor."""
        humidity, temperature = adafruit.read(adafruit.DHT22, SENSOR_PIN)
        if temperature is None or humidity is None:
            return None
        return f"{temperature:0.01f}{lcd.celsius} {humidity:0.01f}%"

    def scroll_text() -> None:
        """Scrolls the text by one position."""
        nonlocal scroll_stage
        text: str = PAGE_TITLES[current_page]
        # Add leading spaces to the text according to the scroll stage
        fragment = text.rjust(len(text) + NUM_COLUMNS)[scroll_stage:]
        lcd.cursor_pos = (0, 0)
        # Ensure string doesn't exceed the maximum length and fill the rest with spaces
        lcd.write_string(fragment[:NUM_COLUMNS].ljust(NUM_COLUMNS))
        scroll_stage += 1

    while PROGRAM_IS_RUNNING:
        now = time.time()  # Current time in seconds
        # Update the page once the text has scrolled to the end
        if scroll_stage > NUM_COLUMNS + len(PAGE_TITLES[current_page]):
            # Switch page
            scroll_stage = 1
            current_page += 1
            if current_page == len(PAGE_TITLES):
                current_page = 0
            lcd.cursor_pos = (1, 0)
            lcd.write_string(centred("Loading..."))
            # Scroll the text so the first character is already visible
            scroll_text()
        # Scroll the title text every 0.75 seconds
        if (now - last_scroll_update) * 1000 >= TIME_PER_CHARACTER_SCROLL:
            last_scroll_update = now
            scroll_text()
        # Update the temperature text every 2 seconds
        if now - last_temperature_update >= TIME_PER_TEMPERATURE_UPDATE:
            # Update the temperature display
            last_temperature_update = now
            rerender_temperature()
