"""Package containing general utility modules."""

from typing import Annotated

# The number of characters on one line of the LCD
NUM_COLUMNS: int = 16

# The number of the GPIO pin to which the humidity and temperature sensor is connected
SENSOR_PIN: int = 23

# A boolean indicating if the output should go to the LCD or the console
CONSOLE_ENABLED: bool = False
