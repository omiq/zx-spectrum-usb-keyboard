from adafruit_hid.keycode import Keycode

# Your confirmed electrical matrix layout

pc_mode = [
    # row0
    Keycode.ONE, Keycode.TWO, Keycode.THREE, Keycode.FOUR, Keycode.FIVE,

    # row1
    Keycode.Q, Keycode.W, Keycode.E, Keycode.R, Keycode.T,

    # row2
    Keycode.A, Keycode.S, Keycode.D, Keycode.F, Keycode.G,

    # row3
    Keycode.ZERO, Keycode.NINE, Keycode.EIGHT, Keycode.SEVEN, Keycode.SIX,

    # row4
    Keycode.P, Keycode.O, Keycode.I, Keycode.U, Keycode.Y,

    # row5 (CAPS SHIFT -> SHIFT)
    Keycode.SHIFT, Keycode.Z, Keycode.X, Keycode.C, Keycode.V,

    # row6
    Keycode.ENTER, Keycode.L, Keycode.K, Keycode.J, Keycode.H,

    # row7 (SYMBOL SHIFT -> ALT)
    Keycode.SPACE, Keycode.ALT, Keycode.M, Keycode.N, Keycode.B,
]

# Example Spectrum mode (you can fill in later)
spectrum_mode = pc_mode[:]   # start with PC map

# ZX Spectrum key names by matrix position (8 rows × 5 cols)
# Based on the electrical matrix layout
SPECTRUM_KEY_NAMES = [
    # row0
    "1", "2", "3", "4", "5",
    # row1
    "Q", "W", "E", "R", "T",
    # row2
    "A", "S", "D", "F", "G",
    # row3
    "0", "9", "8", "7", "6",
    # row4
    "P", "O", "I", "U", "Y",
    # row5
    "CAPS SHIFT", "Z", "X", "C", "V",
    # row6
    "ENTER", "L", "K", "J", "H",
    # row7
    "SPACE", "SYMBOL SHIFT", "M", "N", "B",
]

# CAPS SHIFT combinations (CAPS SHIFT + key = Spectrum key)
# Matrix indices: CAPS SHIFT is at index 25 (row 5, col 0)
CAPS_SHIFT_COMBOS = {
    (25, 0): "EDIT",      # CAPS SHIFT + 1
    (25, 1): '"',      # CAPS SHIFT + 2
    (25, 2): "TRUE VIDEO",      # CAPS SHIFT + 3
    (25, 3): "INV VIDEO",      # CAPS SHIFT + 4
    (25, 4): "CURSOR LEFT",  # CAPS SHIFT + 5
    (25, 15): "DELETE",  # CAPS SHIFT + 0
    (25, 16): "GRAPH",      # CAPS SHIFT + 9
    (25, 17): "CURSOR RIGHT",   # CAPS SHIFT + 8
    (25, 18): "CURSOR UP", # CAPS SHIFT + 7
    (25, 19): "CURSOR DOWN", # CAPS SHIFT + 6
    (25, 20): "P",     # CAPS SHIFT + P (already P)
    (25, 21): "O",     # CAPS SHIFT + O (already O)
    (25, 22): "I",     # CAPS SHIFT + I (already I)
    (25, 23): "U",     # CAPS SHIFT + U (already U)
    (25, 24): "Y",     # CAPS SHIFT + Y (already Y)
    (25, 26): "Z",     # CAPS SHIFT + Z (already Z)
    (25, 27): "X",     # CAPS SHIFT + X (already X)
    (25, 28): "C",     # CAPS SHIFT + C (already C)
    (25, 29): "V",     # CAPS SHIFT + V (already V)
    (25, 30): "ENTER", # CAPS SHIFT + ENTER (already ENTER)
    (25, 31): "L",     # CAPS SHIFT + L (already L)
    (25, 32): "K",     # CAPS SHIFT + K (already K)
    (25, 33): "J",     # CAPS SHIFT + J (already J)
    (25, 34): "H",     # CAPS SHIFT + H (already H)
    (25, 35): "BREAK", # CAPS SHIFT + SPACE
    (25, 36): "EXTEND MODE", # CAPS SHIFT + SYMBOL SHIFT
    (25, 37): "M",     # CAPS SHIFT + M (already M)
    (25, 38): "N",     # CAPS SHIFT + N (already N)
    (25, 39): "B",     # CAPS SHIFT + B (already B)
}

# SYMBOL SHIFT combinations (SYMBOL SHIFT + key = Spectrum key)
# Matrix indices: SYMBOL SHIFT is at index 36 (row 7, col 1)
SYMBOL_SHIFT_COMBOS = {
    (36, 0): "!",      # SYMBOL SHIFT + 1
    (36, 1): '"',      # SYMBOL SHIFT + 2
    (36, 2): "#",      # SYMBOL SHIFT + 3
    (36, 3): "$",      # SYMBOL SHIFT + 4
    (36, 4): "%",      # SYMBOL SHIFT + 5
    (36, 5): "Q",      # SYMBOL SHIFT + Q (already Q)
    (36, 6): "W",      # SYMBOL SHIFT + W (already W)
    (36, 7): "E",      # SYMBOL SHIFT + E (already E)
    (36, 8): "R",      # SYMBOL SHIFT + R (already R)
    (36, 9): "T",      # SYMBOL SHIFT + T (already T)
    (36, 10): "A",     # SYMBOL SHIFT + A (already A)
    (36, 11): "S",     # SYMBOL SHIFT + S (already S)
    (36, 12): "D",     # SYMBOL SHIFT + D (already D)
    (36, 13): "F",     # SYMBOL SHIFT + F (already F)
    (36, 14): "G",     # SYMBOL SHIFT + G (already G)
    (36, 15): ")",     # SYMBOL SHIFT + 0
    (36, 16): "(",     # SYMBOL SHIFT + 9
    (36, 17): "*",     # SYMBOL SHIFT + 8
    (36, 18): "&",     # SYMBOL SHIFT + 7
    (36, 19): "^",     # SYMBOL SHIFT + 6
    (36, 20): '"',     # SYMBOL SHIFT + P (already P)
    (36, 21): ";",     # SYMBOL SHIFT + O (already O)
    (36, 22): "I",     # SYMBOL SHIFT + I (already I)
    (36, 23): "U",     # SYMBOL SHIFT + U (already U)
    (36, 24): "Y",     # SYMBOL SHIFT + Y (already Y)
    (36, 25): "CAPS SHIFT", # SYMBOL SHIFT + CAPS SHIFT
    (36, 26): ":",     # SYMBOL SHIFT + Z
    (36, 27): ";",     # SYMBOL SHIFT + X
    (36, 28): "?",     # SYMBOL SHIFT + C
    (36, 29): "/",     # SYMBOL SHIFT + V
    (36, 30): "ENTER", # SYMBOL SHIFT + ENTER (already ENTER)
    (36, 31): "=",     # SYMBOL SHIFT + L
    (36, 32): "+",     # SYMBOL SHIFT + K
    (36, 33): "-",     # SYMBOL SHIFT + J
    (36, 34): "£",     # SYMBOL SHIFT + H
    (36, 35): "SPACE", # SYMBOL SHIFT + SPACE (already SPACE)
    (36, 37): ".",     # SYMBOL SHIFT + M
    (36, 38): ",",     # SYMBOL SHIFT + N
    (36, 39): ">",     # SYMBOL SHIFT + B
}

# Map Spectrum special keys to their HID keycodes
# These override the default keycode mapping for special keys
SPECIAL_KEY_HID_MAP = {
    "CURSOR LEFT": Keycode.LEFT_ARROW,
    "CURSOR RIGHT": Keycode.RIGHT_ARROW,
    "CURSOR UP": Keycode.UP_ARROW,
    "CURSOR DOWN": Keycode.DOWN_ARROW,
    "DELETE": Keycode.BACKSPACE,
    "BREAK": Keycode.ESCAPE,  # BREAK is typically ESC on modern keyboards
    "EDIT": Keycode.INSERT,   # EDIT is typically INSERT
    "TRUE VIDEO": None,  # No direct HID equivalent, keep as modifier combo
    "INV VIDEO": None,   # No direct HID equivalent, keep as modifier combo
    "GRAPH": None,       # No direct HID equivalent, keep as modifier combo
    "EXTEND MODE": Keycode.TAB, # No direct HID equivalent, keep as modifier combo
}

# Keys that should swap modifiers when sending to USB HID
# Format: (modifier_idx, other_idx): True means swap the modifiers
# This swaps which modifier keycode is sent, but keeps Spectrum key name the same
SWAP_MODIFIERS = {
    (25, 1): True,   # CAPS SHIFT + 2 (") should send SYMBOL SHIFT keycode
    (25, 2): True,   # CAPS SHIFT + 3 (TRUE VIDEO) should send SYMBOL SHIFT keycode
    (25, 3): True,   # CAPS SHIFT + 4 (INV VIDEO) should send SYMBOL SHIFT keycode
    (36, 3): True,   # SYMBOL SHIFT + 4 ($) should send CAPS SHIFT keycode
    (36, 1): True,   # SYMBOL SHIFT + 2 (") should send CAPS SHIFT keycode
    # Add more mappings here as needed
}
