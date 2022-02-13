#!/usr/bin/env python3
"""A temperature controller for the Raspberry Pi made by Konrad Guzek."""

# Standard library imports
import signal
import time
import threading

# Third-party imports
import Adafruit_DHT
from corny_commons import file_manager
from RPi import GPIO
from RPLCD.gpio import CharLCD

# Local application imports
from modules import util, NUM_COLUMNS, SENSOR_PIN


# The GPIO pins used for transmitting data to the LCD
LCD_PINS = [26, 19, 13, 6, 1, 7, 8, 25]

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


def typewrite(text: str, interval: float = 0.1) -> None:
    """Types each character in the string one by one with the specified interval inbetween."""
    for char in text:
        lcd.write_string(char)
        if char != " ":
            # Don't sleep if the current character is whitespace
            time.sleep(interval)


def intro() -> None:
    """Renders the intro text on the LCD."""
    file_manager.log("Playing intro...")
    lcd.cursor_mode = "blink"
    typewrite("Welcome!")
    time.sleep(0.25)
    typewrite(" Made by")
    lcd.cursor_pos = (1, 0)  # Start of second line
    typewrite(centred("Konrad Guzek", span_entire_line=False))
    time.sleep(0.5)
    lcd.cursor_mode = "hide"
    lcd.clear()
    file_manager.log("Completed intro animation.")


def update_display_info() -> None:
    """Adds the humidity and temperature information to the second line of the LCD."""
    while SHOULD_UPDATE_INFO:
        # Read the values from the GPIO-connected humidity and temperature sensor
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, SENSOR_PIN)
        # 0x00 is the hex code for the LCD's custom defined character at location 0
        temp_details = f"{humidity or -1:0.01f}%  {temperature or -1:0.01f}\x00C"
        lcd.cursor_pos = (1, 0)
        lcd.write_string(centred(temp_details))
        lcd.lf()
        time.sleep(2)


def main() -> None:
    """Cleans up the LCD from previous usage and keeps the display updated."""
    lcd.clear()
    lcd.home()
    # Define custom character at location 0 with the above bitmap
    lcd.create_char(0, degree_sign)
    file_manager.log("LCD display initialised successfully!")
    intro()
    update_info_thread.start()
    util.scroll_text(lcd, "Pi Temperature")


# When the user presses Ctrl+C (SIGIGN), the Python process interprets this as KeyboardInterrupt
# This exception can be caught in the code above
# When the user presses Ctrl+Z (SIGTSTP), the Python process interprets this as having reached EOF.
# To make the program able to catch the user pressing Ctrl+Z, we remap it to raising the
# KeyboardInterrupt exception.

def raise_keyboard_interrupt(_signum, _stackframe) -> None:
    """Raises the signal.SIGINT signal which is interpreted as the `KeyboardInterrupt` exception."""
    signal.raise_signal(signal.SIGINT)
    # Alternatively: `raise KeyboardInterrupt`


# signal.SIGTSTP is a valid signal in unix-based systems; it's unsupported on Windows
try:
    signal.signal(signal.SIGTSTP, raise_keyboard_interrupt)  # pylint: disable=no-member
except AttributeError:
    # Running on Windows
    pass

SHOULD_UPDATE_INFO = True
update_info_thread = threading.Thread(target=update_display_info)

# Initialise the global LCD object reference
file_manager.log("Initialising LCD display...")
lcd = CharLCD(pin_rs=21, pin_rw=20,  pin_e=16, pins_data=LCD_PINS,
              numbering_mode=GPIO.BCM, cols=16, rows=2)
try:
    main()
except KeyboardInterrupt:
    # The user force exited the program
    print()  # Newline so log isn't on same line as user input
    file_manager.log("Quitting program (ctrl+c)")
finally:
    # Clean up GPIO resources and clear the display
    if update_info_thread.is_alive():
        SHOULD_UPDATE_INFO = False
        # Wait until the thread completes execution
        update_info_thread.join()
    lcd.close(clear=True)
