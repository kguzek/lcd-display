#!/usr/bin/env python3

# Standard library imports
import random
import signal
import time

# Third-party imports
import Adafruit_DHT
from corny_commons import file_manager, util
from RPi import GPIO
from RPLCD.gpio import CharLCD

NUM_COLUMNS = 16

# Initialise temperature sensor
sensor = Adafruit_DHT.DHT22
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
    centred = text.rjust(padding + len(text))
    if span_entire_line:
        # Make the string the length of the entire line
        centred = centred.ljust(num_columns)
    # file_manager.log(f"Centred text: '{centred}'")
    return centred


def type(fragment: str, interval: float = 0.1) -> None:
    """Types each character in the string one by one with the specified interval inbetween."""
    for char in fragment:
        lcd.write_string(char)      
        if char != " ":
            # Don't sleep if the current character is whitespace
            time.sleep(interval)         

    
def intro() -> None:
    """Renders the intro text on the LCD."""
    file_manager.log("Playing intro...")
    lcd.cursor_mode = "blink"
    type("Welcome!")
    time.sleep(0.25)
    type(" Made by")
    lcd.cursor_pos = (1, 0)  # Start of second line
    type(centred("Konrad Guzek", span_entire_line = False))
    time.sleep(0.5)
    lcd.cursor_mode = "hide"


def update_display_info() -> None:
    """Adds the humidity and temperature information to the second line of the LCD."""
    lcd.cursor_pos = (1, 0)
    temp = random.randint(15, 40)
    humidity, temperature = Adafruit_DHT.read_retry(sensor, SENSOR_PIN)
    # 0x00 is the hex code for the LCD's custom defined character at location 0
    lcd.write_string(centred(f"{humidity or -1:0.01f}%  {temperature or -1:0.01f}\x00C"))
    time.sleep(2)


def main() -> None:
    """Cleans up the LCD from previous usage and keeps the display updated."""
    lcd.clear()
    lcd.home()
    # Define custom character at location 0 with the above bitmap
    lcd.create_char(0, degree_sign)
    file_manager.log("LCD display initialised successfully!")
    try:
        intro()
        lcd.clear()
        lcd.write_string(centred("Pi Temperature"))
        while True:
            update_display_info()
    except KeyboardInterrupt:
        # The user force exited the program
        print()  # Newline so log isn't on same line as user input
        file_manager.log("Quitting program (ctrl+c)")
    finally:
        # Clean up GPIO resources and clear the display
        lcd.close(clear=True)

# When the user presses Ctrl+C (SIGIGN), the Python process interprets this as KeyboardInterrupt
# This exception can be caught in the code above
# When the user presses Ctrl+Z (SIGSTP), the Python process interprets this as having reached EOF
# To make the program able to catch the user pressing Ctrl+Z, we remap it to raising the
# KeyboardInterrupt exception.
signal.signal(signal.SIGTSTP, lambda _signum, _stack_frame: signal.raise_signal(signal.SIGINT))

# Initialise the global LCD object reference
file_manager.log("Initialising LCD display...")
lcd = CharLCD(pin_rs=21, pin_rw=20,  pin_e=16, pins_data=[26, 19, 13, 6, 1, 7, 8, 25], numbering_mode=GPIO.BCM, cols=16, rows=2)
# lcd = CharLCD(pin_rs=40, pin_rw=38, pin_e=36, pins_data=[37, 35, 33, 31, 28, 26, 24, 22], cols=16, rows=2, numbering_mode=GPIO.BOARD)
main()

