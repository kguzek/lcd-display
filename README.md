# LCD Display

This is a showcase Python project which can be run on a Raspberry Pi with a temperature and humidity sensor as well as an LCD board to output the current measured values. It bases on the [RPLCD library](https://rplcd.readthedocs.io/en/stable/index.html) with added utility functions which facilitate scrolling text, typewriter effect and automatic centering.

The display cycles between sensor values and system temperature, which is read from the Raspberry Pi's default temperature virtual device.

## Hardware compatibility

The program automatically detects any missing devices. In the case of no sensors, it mocks the data as random values, and if there is no LCD connected it uses the console output as a mock 16x2 LCD board using the `console_graphics` module from [corny_commons](https://github.com/kguzek/corny-commons).
If it is run on another device than a Raspberry Pi (e.g. WSL on Windows), it will likely not detect the system temperature correctly and will instead leave the value loading.

## Demo

![lcd-display](https://github.com/user-attachments/assets/856ecc91-0a34-43ef-818f-f01eef857854)
