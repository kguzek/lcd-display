#!/usr/bin/env python3
"""A temperature controller for the Raspberry Pi made by Konrad Guzek."""

# Standard library imports
import signal
import time
import threading

# Third-party imports
from corny_commons import file_manager
try:
    import Adafruit_DHT
    from RPi import GPIO
    from RPLCD.gpio import CharLCD
except ModuleNotFoundError:
    from modules.console_simulation import DummyAdafruitDHT as Adafruit_DHT
    from modules.console_simulation import DummyGPIO as GPIO, DummyLCD as CharLCD

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


def typewrite(lcd: CharLCD, text: str, interval: float = 0.1) -> None:
    """Types each character in the string one by one with the specified interval inbetween."""
    for char in text:
        lcd.write_string(char)
        if char != " ":
            # Don't sleep if the current character is whitespace
            time.sleep(interval)


def intro(lcd: CharLCD) -> None:
    """Renders the intro text on the LCD."""
    # file_manager.log("Playing intro...")
    lcd.cursor_mode = "blink"
    typewrite(lcd, "Welcome!")
    time.sleep(0.25)
    typewrite(lcd, " Made by")
    lcd.cursor_pos = (1, 0)  # Start of second line
    typewrite(lcd, centred("Konrad Guzek", span_entire_line=False))
    time.sleep(0.5)
    lcd.cursor_mode = "hide"
    lcd.clear()
    # file_manager.log("Completed intro animation.")


def update_display_info(lcd: CharLCD, adafruit) -> None:
    """Adds the humidity and temperature information to the second line of the LCD."""
    while util.PROGRAM_IS_RUNNING:
        # Read the values from the GPIO-connected humidity and temperature sensor
        humidity, temperature = adafruit.read_retry(adafruit.DHT22, SENSOR_PIN)
        # 0x00 is the hex code for the LCD's custom defined character at location 0
        temp_details = f"{humidity or -1:0.01f}% {temperature or -1:0.01f}\x00C"
        while util.currently_processing["scroll"]:
            if not util.PROGRAM_IS_RUNNING:
                return
        util.currently_processing["display_info"] = True
        lcd.cursor_pos = (1, 0)
        lcd.write_string(centred(temp_details))
        util.currently_processing["display_info"] = False
        time.sleep(2)


def main(lcd: CharLCD, adafruit) -> None:
    """Cleans up the LCD from previous usage and keeps the display updated."""
    lcd.clear()
    lcd.home()
    # Define custom character at location 0 with the above bitmap
    lcd.create_char(0, degree_sign)
    # file_manager.log("LCD display initialised successfully!")
    update_info_thread = threading.Thread(target=update_display_info, args=[lcd, adafruit])

    # When the user presses Ctrl+C (SIGIGN), Python interprets this as KeyboardInterrupt.
    # This is favourable as it can be caught in the code below (line 118).
    # When the user presses Ctrl+Z (SIGTSTP), Python interprets this as having reached the EOF.
    # To make the program able to catch the user pressing Ctrl+Z, we remap it to raising the
    # KeyboardInterrupt exception.

    def raise_keyboard_interrupt(_signum, _stackframe) -> None:
        """Raises the signal.SIGINT signal which is interpreted as `KeyboardInterrupt`."""
        signal.raise_signal(signal.SIGINT)
        # Alternatively: simply `raise KeyboardInterrupt`.

    # signal.SIGTSTP is a valid signal in unix-based systems, but not on Windows
    try:
        signal.signal(signal.SIGTSTP, raise_keyboard_interrupt)  # pylint: disable=no-member
    except AttributeError:
        # Running on Windows
        pass

    try:
        intro(lcd)
        update_info_thread.start()
        # Blocking call; infinite loop
        util.scroll_text(lcd, "Pi Temperature")
    except KeyboardInterrupt:
        # The user force exited the program
        print()  # Newline so log isn't on same line as user input
        file_manager.log("Quitting program (ctrl+c)")
    finally:
        # Clean up GPIO resources and clear the display
        util.PROGRAM_IS_RUNNING = False
        if update_info_thread.is_alive():
            # Wait until the thread completes execution
            update_info_thread.join()
        lcd.close(clear=True)


def instantiate_lcd() -> CharLCD:
    """Returns an instance of the CharLCD class using the specific configs."""
    return CharLCD(pin_rs=21, pin_rw=20, pin_e=16, pins_data=LCD_PINS,
         numbering_mode=GPIO.BCM, cols=16, rows=2)


if __name__ == "__main__":
    print("Started program from main!")
    main(instantiate_lcd(), Adafruit_DHT)
