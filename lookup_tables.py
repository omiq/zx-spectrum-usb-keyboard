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
