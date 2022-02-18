"""General utility functions."""

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
TIME_PER_PAGE = 15  # seconds
TIME_PER_TEMPERATURE_UPDATE = 2  # seconds
TIME_PER_CHARACTER_SCROLL = 500  # milliseconds


def centred(text: str, span_entire_line: bool = True) -> str:
    """Returns a string with the left and right sides padded with the correct number of spaces."""
    # The number of spaces that should be on either side of the string
    padding = (NUM_COLUMNS - len(text)) // 2
    # Make the string a total length of left space + original length
    _centred = text.rjust(padding + len(text))
    if span_entire_line:
        # Make the string the length of the entire line
        _centred = _centred.ljust(NUM_COLUMNS)
    # file_manager.log(f"Centred text: '{_centred}'")
    return _centred


def rerender_display(lcd: CharLCD, adafruit) -> None:
    """Keeps the LCD display contents updated."""
    current_page = scroll_stage = 0
    start_time = time.time()
    last_page_update = last_temperature_update = last_scroll_update = start_time


    def rerender_temperature():
        """Render either the sensor temperature or the system temperature."""
        if current_page == 0:
            text = get_sensor_temperature()
        else:
            sys_temp = systemp.get_system_temperature()
            # Mark the temperature as unknown if there was an error while retrieving
            text = ("??" if sys_temp is None else f"{sys_temp:0.01f}") + lcd.celsius
        lcd.cursor_pos = (1, 0)
        lcd.write_string(centred(text))


    def get_sensor_temperature():
        """Reads the values from the GPIO-connected humidity and temperature sensor."""
        humidity, temperature = adafruit.read(adafruit.DHT22, SENSOR_PIN)
        temperature = "??" if temperature is None else f"{temperature:0.01f}"
        humidity = "??" if humidity is None else f"{humidity:0.01f}"
        return f"{temperature}{lcd.celsius} {humidity}%"


    def scroll_text():
        """Scrolls the text by one position."""
        nonlocal scroll_stage
        text: str = PAGE_TITLES[current_page]
        if scroll_stage > NUM_COLUMNS + len(text):
            scroll_stage = 0
        # Add leading spaces to the text according to the scroll stage
        fragment = text.rjust(len(text) + NUM_COLUMNS)[scroll_stage:]
        lcd.cursor_pos = (0, 0)
        # Ensure string doesn't exceed the maximum length and fill the rest with spaces
        lcd.write_string(fragment[:NUM_COLUMNS].ljust(NUM_COLUMNS))
        scroll_stage += 1

    rerender_temperature()
    scroll_text()
    while PROGRAM_IS_RUNNING:
        now = time.time()
        # Update the page every 15 seconds
        if now - last_page_update >= TIME_PER_PAGE:
            # Switch page
            last_page_update = now
            current_page += 1
            if current_page == len(PAGE_TITLES):
                current_page = 0
            scroll_stage = 0
        # Update the temperature text every 2 seconds
        if now - last_temperature_update >= TIME_PER_TEMPERATURE_UPDATE:
            # Update the temperature display
            last_temperature_update = now
            rerender_temperature()
        # Scroll the text every 0.5 seconds
        if (now - last_scroll_update) * 1000 >= TIME_PER_CHARACTER_SCROLL:
            last_scroll_update = now
            scroll_text()
