# 
#
#

import board
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.modules.combos import Combos
from kmk.modules.combos import Chord
from kmk.modules.combos import Sequence

#from kmk.modules.layers import Layers

print("Starting")
keyboard = KMKKeyboard()
keyboard.debug_enabled = True
#keyboard.modules.append(Layers())

combos = Combos()
keyboard.modules.append(combos)


keyboard.row_pins = (

board.GP0,
board.GP1,
board.GP2,
board.GP3,
board.GP4,
board.GP5,
board.GP6,
board.GP7,


)

keyboard.col_pins = (
board.GP8,
board.GP9,
board.GP10,
board.GP11,
board.GP12,


)

# keyboard.diode_orientation = DiodeOrientation.ROW2COL

#MOMENTARY = KC.MO(1)

combos.combos = [
    Chord((KC.Z, KC.X, KC.N9, KC.N8,  ), KC.DEL, timeout=500),
    Chord((KC.Z, KC.X, KC.N9, KC.N6, ), KC.DOWN, timeout=500),
    Chord((KC.Z, KC.X, KC.N9, KC.N7, ), KC.UP, timeout=500),
    Chord((KC.Z, KC.N2), KC.CAPS, timeout=500),
    Chord((KC.N2,KC.N3), KC.N2, timeout=500),
   # Chord((KC.1,KC.1), KC.N1, timeout=500),

]



keyboard.keymap  = [
    [
    #   0         1            2           3   1       4
        KC.N1     ,KC.N2      ,KC.N3      ,KC.N4      ,KC.N5   ,

    #   5          6           7           8  q        9
        KC.Q      ,KC.W       ,KC.E       ,KC.R       ,KC.T    ,

    #   10          11          12        13 a         14
        KC.A      ,KC.S       ,KC.D       ,KC.F       ,KC.G    ,

    #   15         16          17         15 0         19
        KC.N0     ,KC.N9      ,KC.N8      ,KC.N7      ,KC.N6   ,

    #   21         21          22          20 p        24
        KC.P      ,KC.O       ,KC.I       ,KC.U       ,KC.Y    ,

    #   25         26          27           25 cap          29
        KC.LSFT   ,KC.Z       ,KC.X       ,KC.C       ,KC.V    ,

    #   30        31            32         30 CR       34
        KC.RET  ,KC.L       ,KC.K    ,   KC.J   ,    KC.H  ,

    #   36                      37          35 SP        39
        KC.SPC, KC.LALT     ,KC.M       , KC.N  , KC.B ,

        KC.NO,
        KC.NO,
        KC.NO,
        KC.NO,
        KC.NO,
        KC.NO,
        KC.NO,
        KC.NO,
        KC.NO,
        KC.NO,
        KC.NO,
        KC.NO,
        KC.NO,
        KC.NO,
        KC.NO,
        KC.NO,
        KC.NO,
        KC.NO,
        KC.NO,
        KC.NO,


]]

if __name__ == '__main__':
    keyboard.go()
