#!/usr/bin/env python3
"""Module for showing fake data on the LCD."""

# Third party imports
from corny_commons import file_manager

# Local application imports
from main import main, instantiate_lcd
from modules import console_simulation

file_manager.log("Started program with forced dummy data!")
main(instantiate_lcd(), console_simulation.DummyAdafruitDHT)
