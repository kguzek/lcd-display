"""Module for retrieving the system CPU temperature."""

# Standard library imports
import os

# Third party imports
from corny_commons import file_manager

BASE_DIR = "/sys/class/thermal/thermal_zone0/"
ENABLED = os.path.isdir(BASE_DIR)


def get_system_temperature() -> float or None:
    """Gets the system's CPU temperature."""
    if not ENABLED:
        return None
    try:
        with open(BASE_DIR + "temp", encoding="utf-8") as file:
            raw_data = file.read()
    except (ValueError, FileNotFoundError):
        # Invalid temperature data
        return None
    else:
        temp = int(raw_data)
        # Temperature is stored as thousandths of a Celsius degree
        return temp / 1000


if __name__ == "__main__":
    temperature = get_system_temperature()
    if temperature is None:
        file_manager.log("The current system temperature could not be established.")
    else:
        file_manager.log(f"The current system temperature is {temperature}°C.")
