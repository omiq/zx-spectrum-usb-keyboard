## Circuitpython code for the ZX Spectrum+ and eventually the **Grey** ZX Spectrum 128+2 keyboard (not the A or B versions!)

(Now just uses Adafruit HID libraries, no need for KMK)

```
import time
import board
import usb_hid
from adafruit_hid.keyboard import Keyboard # Adafruit interface device libs
from adafruit_hid.keycode import Keycode

from matrix_scanner import SpectrumMatrix         # specific machine keyboard matrix
from lookup_tables import pc_mode, spectrum_mode  # I am going to have "Spectrum" mode for emulators etc and PC mode for regular use

# Choose your mode switch pin (optional)
mode_switch = None  # you can add a GPIO for switching modes

keyboard = Keyboard(usb_hid.devices)

# Set up the matrix
matrix = SpectrumMatrix(
    row_pins=(
        board.GP2,
        board.GP3,
        board.GP4,
        board.GP5,
        board.GP6,
        board.GP7,
        board.GP8,
        board.GP9,
    ),
    col_pins=(
        board.GP10,
        board.GP11,
        board.GP12,
        board.GP13,
        board.GP14,
    ),
    settle_us=300
)

prev = [0] * matrix.key_count

current_mode = pc_mode   # default
print("Starting")
while True:
    pressed = matrix.scan()
    # print(pressed)
    for idx in range(matrix.key_count):
        if pressed[idx] and not prev[idx]:
            keycode = current_mode[idx]
            keyboard.press(keycode)

        if prev[idx] and not pressed[idx]:
            keycode = current_mode[idx]
            keyboard.release(keycode)

    prev = pressed[:]
    time.sleep(0.005)

```

