#!/usr/bin/env python3
"""A temperature controller for the Raspberry Pi made by Konrad Guzek."""

# Standard library imports
import asyncio
import signal

# Third-party imports
import Adafruit_DHT  # pylint: disable=import-error
from corny_commons import file_manager
from RPi import GPIO  # pylint: disable=import-error
from RPLCD.gpio import CharLCD  # pylint: disable=import-error

# Local application imports
from modules import NUM_COLUMNS, util


# The GPIO pins used for transmitting data to the LCD
LCD_PINS = [26, 19, 13, 6, 1, 7, 8, 25]

# Initialise temperature sensor
sensor: int = Adafruit_DHT.DHT22
SENSOR_PIN = 23

# Declare custom degree symbol bitmap
degree_sign = (
    0b01100,
    0b10010,
    0b10010,
    0b01100,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)


def centred(text: str, num_columns: int = NUM_COLUMNS, span_entire_line: bool = True) -> str:
    """Returns a string with the left and right sides padded with the correct number of spaces."""
    # The number of spaces that should be on either side of the string
    padding = (num_columns - len(text)) // 2
    # Make the string a total length of left space + original length
    _centred = text.rjust(padding + len(text))
    if span_entire_line:
        # Make the string the length of the entire line
        _centred = _centred.ljust(num_columns)
    # file_manager.log(f"Centred text: '{_centred}'")
    return _centred


async def typewrite(fragment: str, interval: float = 0.1) -> None:
    """Types each character in the string one by one with the specified interval inbetween."""
    for char in fragment:
        lcd.write_string(char)
        if char != " ":
            # Don't sleep if the current character is whitespace
            await asyncio.sleep(interval)


async def intro() -> None:
    """Renders the intro text on the LCD."""
    file_manager.log("Playing intro...")
    lcd.cursor_mode = "blink"
    await typewrite("Welcome!")
    await asyncio.sleep(0.25)
    await typewrite(" Made by")
    lcd.cursor_pos = (1, 0)  # Start of second line
    await typewrite(centred("Konrad Guzek", span_entire_line=False))
    await asyncio.sleep(0.5)
    lcd.cursor_mode = "hide"
    lcd.clear()
    file_manager.log("Completed intro animation.")


async def update_display_info() -> None:
    """Adds the humidity and temperature information to the second line of the LCD."""
    lcd.cursor_pos = (1, 0)
    humidity, temperature = Adafruit_DHT.read_retry(sensor, SENSOR_PIN)
    # 0x00 is the hex code for the LCD's custom defined character at location 0
    temp_details= f"{humidity or -1:0.01f}%  {temperature or -1:0.01f}\x00C"
    lcd.write_string(centred(temp_details))
    await asyncio.sleep(2)
    await update_display_info()


async def main() -> None:
    """Cleans up the LCD from previous usage and keeps the display updated."""
    lcd.clear()
    lcd.home()
    # Define custom character at location 0 with the above bitmap
    lcd.create_char(0, degree_sign)
    file_manager.log("LCD display initialised successfully!")
    await intro()
    loop.create_task(util.scroll_text(lcd, "Pi Temperature", max_num_scrolls=0))
    loop.create_task(update_display_info())
    # Wait until all tasks have completed
    await asyncio.gather(*asyncio.all_tasks())


# When the user presses Ctrl+C (SIGIGN), the Python process interprets this as KeyboardInterrupt
# This exception can be caught in the code above
# When the user presses Ctrl+Z (SIGTSTP), the Python process interprets this as having reached EOF.
# To make the program able to catch the user pressing Ctrl+Z, we remap it to raising the
# KeyboardInterrupt exception.

def raise_keyboard_interrupt(_signum, _stackframe) -> None:
    """Raises the signal.SIGINT signal which is interpreted as the `KeyboardInterrupt` exception."""
    signal.raise_signal(signal.SIGINT)
    # Alternatively: `raise KeyboardInterrupt``


# signal.SIGTSTP is a valid signal in unix-based systems; it's unsupported on Windows
signal.signal(signal.SIGTSTP, raise_keyboard_interrupt)  # pylint: disable=no-member

# Initialise the global LCD object reference
file_manager.log("Initialising LCD display...")
lcd = CharLCD(pin_rs=21, pin_rw=20,  pin_e=16, pins_data=LCD_PINS,
              numbering_mode=GPIO.BCM, cols=16, rows=2)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    # The user force exited the program
    print()  # Newline so log isn't on same line as user input
    file_manager.log("Quitting program (ctrl+c)")
finally:
    # Clean up GPIO resources and clear the display
    lcd.close(clear=True)
