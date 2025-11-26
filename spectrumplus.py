import time
import board

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation


keyboard = KMKKeyboard()

keyboard.debug_enabled = False

# Your confirmed wiring
keyboard.row_pins = (
    board.GP2,  # row0
    board.GP3,  # row1
    board.GP4,  # row2
    board.GP5,  # row3  (0 9 8 7 6)
    board.GP6,  # row4  (P O I U Y)
    board.GP7,  # row5  (CAPS Z X C V)
    board.GP8,  # row6  (ENTER L K J H)
    board.GP9,  # row7  (SPACE SYMBOL M N B)
)

keyboard.col_pins = (
    board.GP22,  # col0
    board.GP21,  # col1
    board.GP20,  # col2
    board.GP19,  # col3
    board.GP18,  # col4
)

keyboard.diode_orientation = DiodeOrientation.COL2ROW


# Keymap in electrical order (8 rows × 5 cols)
# Based on your matrix tester results

keyboard.keymap = [
    [
        # row0
        KC.N1, KC.N2, KC.N3, KC.N4, KC.N5,
        # row1
        KC.Q, KC.W, KC.E, KC.R, KC.T,
        # row2
        KC.A, KC.S, KC.D, KC.F, KC.G,
        # row3
        KC.N0, KC.N9, KC.N8, KC.N7, KC.N6,
        # row4
        KC.P, KC.O, KC.I, KC.U, KC.Y,
        # row5
        KC.LSFT, KC.Z, KC.X, KC.C, KC.V,
        # row6
        KC.ENTER, KC.L, KC.K, KC.J, KC.H,
        # row7
        KC.SPACE, KC.LALT, KC.M, KC.N, KC.B,
    ]
]


keyboard.go()
