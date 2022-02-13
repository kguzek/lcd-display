"""Module for showing fake data on the LCD."""

# Local application imports
from main import main, instantiate_lcd
from modules import console_simulation


main(instantiate_lcd(), console_simulation.DummyAdafruitDHT)
