import time
import board
import digitalio

# EDIT THESE
ROW_PINS = [
    board.GP2,
    board.GP3,
    board.GP4,
    board.GP5,
    board.GP6,
    board.GP7,
    board.GP8,
    board.GP9,
]

COL_PINS = [
    board.GP22,
    board.GP21,
    board.GP20,
    board.GP19,
    board.GP18,
]

# SET THIS MANUALLY:
# True  = diodes are row -> column  (ROW2COL)
# False = diodes are column -> row  (COL2ROW)
ROW_TO_COL = False


# Prepare pins
rows = []
cols = []

for pin in ROW_PINS:
    p = digitalio.DigitalInOut(pin)
    p.direction = digitalio.Direction.INPUT
    p.pull = digitalio.Pull.UP
    rows.append(p)

for pin in COL_PINS:
    p = digitalio.DigitalInOut(pin)
    p.direction = digitalio.Direction.INPUT
    p.pull = digitalio.Pull.UP
    cols.append(p)


print("ZX Spectrum membrane scanner")
print("Press keys and watch row/col pairs.\n")


def scan_matrix():
    pressed = []

    if ROW_TO_COL:
        # Drive rows low, read columns
        for r_index, r_pin in enumerate(rows):
            r_pin.direction = digitalio.Direction.OUTPUT
            r_pin.value = False

            for c_index, c_pin in enumerate(cols):
                if not c_pin.value:
                    pressed.append((r_index, c_index))

            r_pin.direction = digitalio.Direction.INPUT
            r_pin.pull = digitalio.Pull.UP
    else:
        # Drive columns low, read rows
        for c_index, c_pin in enumerate(cols):
            c_pin.direction = digitalio.Direction.OUTPUT
            c_pin.value = False

            for r_index, r_pin in enumerate(rows):
                if not r_pin.value:
                    pressed.append((r_index, c_index))

            c_pin.direction = digitalio.Direction.INPUT
            c_pin.pull = digitalio.Pull.UP

    return pressed


last = set()

while True:
    now = set(scan_matrix())

    for r, c in now - last:
        print(f"DOWN row {r} col {c}")

    for r, c in last - now:
        print(f"UP   row {r} col {c}")

    last = now
    time.sleep(0.02)
