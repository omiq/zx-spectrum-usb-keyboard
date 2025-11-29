import time
import board
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

from matrix_scanner import SpectrumMatrix
from lookup_tables import pc_mode, spectrum_mode

# Choose your mode switch pin (optional)
mode_switch = None  # you can add a GPIO for switching modes

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
    "DELETE": Keycode.DELETE,
    "BREAK": Keycode.ESCAPE,  # BREAK is typically ESC on modern keyboards
    "EDIT": Keycode.INSERT,   # EDIT is typically INSERT
    "TRUE VIDEO": None,  # No direct HID equivalent, keep as modifier combo
    "INV VIDEO": None,   # No direct HID equivalent, keep as modifier combo
    "GRAPH": None,       # No direct HID equivalent, keep as modifier combo
    "EXTEND MODE": None, # No direct HID equivalent, keep as modifier combo
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

def get_spectrum_key_name(pressed_indices):
    """Get the Spectrum key name for a combination of pressed keys."""
    if len(pressed_indices) == 0:
        return None
    
    if len(pressed_indices) == 1:
        idx = pressed_indices[0]
        if idx < len(SPECTRUM_KEY_NAMES):
            return SPECTRUM_KEY_NAMES[idx]
        return None
    
    # Check for CAPS SHIFT combinations
    caps_shift_idx = 25  # CAPS SHIFT is at index 25
    if caps_shift_idx in pressed_indices:
        for other_idx in pressed_indices:
            if other_idx != caps_shift_idx:
                # Dictionary keys are (25, other_idx) format
                combo_key = (caps_shift_idx, other_idx)
                if combo_key in CAPS_SHIFT_COMBOS:
                    return CAPS_SHIFT_COMBOS[combo_key]
                # If not in combo map, show as CAPS SHIFT + key
                other_name = SPECTRUM_KEY_NAMES[other_idx] if other_idx < len(SPECTRUM_KEY_NAMES) else f"KEY_{other_idx}"
                return f"CAPS SHIFT + {other_name}"
    
    # Check for SYMBOL SHIFT combinations
    symbol_shift_idx = 36  # SYMBOL SHIFT is at index 36
    if symbol_shift_idx in pressed_indices:
        for other_idx in pressed_indices:
            if other_idx != symbol_shift_idx:
                # Dictionary keys are (36, other_idx) format
                combo_key = (symbol_shift_idx, other_idx)
                if combo_key in SYMBOL_SHIFT_COMBOS:
                    return SYMBOL_SHIFT_COMBOS[combo_key]
                # If not in combo map, show as SYMBOL SHIFT + key
                other_name = SPECTRUM_KEY_NAMES[other_idx] if other_idx < len(SPECTRUM_KEY_NAMES) else f"KEY_{other_idx}"
                return f"SYMBOL SHIFT + {other_name}"
    
    # Multiple keys pressed but no known combination
    names = []
    for idx in sorted(pressed_indices):
        if idx < len(SPECTRUM_KEY_NAMES):
            names.append(SPECTRUM_KEY_NAMES[idx])
        else:
            names.append(f"KEY_{idx}")
    return " + ".join(names)

def get_keycode_name(keycode, matrix_idx=None, pressed_indices=None):
    """Get a readable name for a keycode, optionally with Spectrum key name."""
    # Get PC keycode name
    pc_name = None
    
    # Try to get the name attribute
    if hasattr(keycode, 'name'):
        pc_name = keycode.name
    
    # If no name attribute, try to find it by value in Keycode class
    if not pc_name:
        keycode_value = int(keycode) if hasattr(keycode, '__int__') else keycode
        for attr_name in dir(Keycode):
            if not attr_name.startswith('_'):
                attr_value = getattr(Keycode, attr_name)
                if isinstance(attr_value, int) and attr_value == keycode_value:
                    pc_name = attr_name
                    break
        
        # Fallback to showing the numeric value
        if not pc_name:
            pc_name = f"KEYCODE_{keycode_value}"
    
    # If we have pressed indices, try to get the Spectrum combination name
    if pressed_indices is not None and len(pressed_indices) > 0:
        spectrum_name = get_spectrum_key_name(pressed_indices)
        if spectrum_name:
            return f"{spectrum_name} ({pc_name})"
    
    # If we have a matrix index, also show the Spectrum key name
    if matrix_idx is not None and matrix_idx < len(SPECTRUM_KEY_NAMES):
        spectrum_name = SPECTRUM_KEY_NAMES[matrix_idx]
        if spectrum_name != pc_name:  # Only show both if they're different
            return f"{spectrum_name} ({pc_name})"
    
    return pc_name

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
    settle_us=1200  # Settle time - increased for more reliable sampling
)

prev = [0] * matrix.key_count
last_reported_key = None
modifier_press_time = {}  # Track when modifiers were pressed to allow combo detection

# Buffer to track key states over multiple iterations for more reliable detection
key_state_buffer = []  # List of recent scan results
BUFFER_SIZE = 4  # Number of iterations to buffer (increased for more reliable detection)

current_mode = pc_mode   # default
print("Starting")
while True:
    # Scan the matrix
    pressed = matrix.scan()
    
    # Add current scan to buffer
    key_state_buffer.append(pressed[:])
    if len(key_state_buffer) > BUFFER_SIZE:
        key_state_buffer.pop(0)
    
    # Use merged state from buffer - if a key is pressed in ANY of the recent scans, consider it pressed
    # This helps catch keys that might be missed in a single scan
    merged_pressed = [0] * matrix.key_count
    for buffered_state in key_state_buffer:
        for idx in range(matrix.key_count):
            if buffered_state[idx]:
                merged_pressed[idx] = 1
    
    # Use merged state for processing
    pressed = merged_pressed

    # Track currently pressed keys
    currently_pressed = []
    for idx in range(matrix.key_count):
        if pressed[idx]:
            currently_pressed.append(idx)

    # Detect key press events (transitions from not pressed to pressed)
    # First, collect all newly pressed keys
    newly_pressed = []
    for idx in range(matrix.key_count):
        if pressed[idx] and not prev[idx]:
            newly_pressed.append(idx)
            
            # Get the Spectrum key name for this combination to check for special keys
            combo_indices = currently_pressed[:]
            spectrum_name = get_spectrum_key_name(combo_indices)
            
            # Check if this is a special key that has a direct HID mapping
            if spectrum_name and spectrum_name in SPECIAL_KEY_HID_MAP:
                special_keycode = SPECIAL_KEY_HID_MAP[spectrum_name]
                if special_keycode is not None:
                    # Send the special HID keycode directly
                    keyboard.press(special_keycode)
                    continue  # Skip normal keycode handling
            
            # Normal keycode handling with modifier swapping
            keycode = current_mode[idx]
            caps_shift_idx = 25
            symbol_shift_idx = 36
            
            # Check if we have a modifier combination that needs swapping
            if idx == caps_shift_idx:
                # CAPS SHIFT pressed - check if combo needs swap
                for other_idx in currently_pressed:
                    if other_idx != idx:
                        combo_key = (idx, other_idx)
                        if combo_key in SWAP_MODIFIERS:
                            # Swap: send SYMBOL SHIFT keycode instead
                            keycode = current_mode[symbol_shift_idx]
                            break
            elif idx == symbol_shift_idx:
                # SYMBOL SHIFT pressed - check if combo needs swap
                for other_idx in currently_pressed:
                    if other_idx != idx:
                        combo_key = (idx, other_idx)
                        if combo_key in SWAP_MODIFIERS:
                            # Swap: send CAPS SHIFT keycode instead
                            keycode = current_mode[caps_shift_idx]
                            break
            else:
                # Regular key pressed - check if modifier combo needs swap
                if caps_shift_idx in currently_pressed:
                    combo_key = (caps_shift_idx, idx)
                    if combo_key in SWAP_MODIFIERS:
                        # Send SYMBOL SHIFT keycode instead of CAPS SHIFT
                        keyboard.press(current_mode[symbol_shift_idx])
                        keycode = current_mode[idx]
                elif symbol_shift_idx in currently_pressed:
                    combo_key = (symbol_shift_idx, idx)
                    if combo_key in SWAP_MODIFIERS:
                        # Send CAPS SHIFT keycode instead of SYMBOL SHIFT
                        keyboard.press(current_mode[caps_shift_idx])
                        keycode = current_mode[idx]
            
            keyboard.press(keycode)
    
    # Handle key releases - need to check for special keys and swapped modifiers
    for idx in range(matrix.key_count):
        if prev[idx] and not pressed[idx]:
            # Check if this was a special key combination
            prev_pressed = []
            for i in range(matrix.key_count):
                if prev[i]:
                    prev_pressed.append(i)
            
            prev_spectrum_name = get_spectrum_key_name(prev_pressed)
            if prev_spectrum_name and prev_spectrum_name in SPECIAL_KEY_HID_MAP:
                special_keycode = SPECIAL_KEY_HID_MAP[prev_spectrum_name]
                if special_keycode is not None:
                    # Release the special HID keycode
                    keyboard.release(special_keycode)
                    continue  # Skip normal keycode handling
            
            # Normal keycode release handling with modifier swapping
            keycode = current_mode[idx]
            caps_shift_idx = 25
            symbol_shift_idx = 36
            
            # Check if this was part of a swapped modifier combination
            if idx == caps_shift_idx:
                # Check if we need to release swapped modifier
                for other_idx in range(matrix.key_count):
                    if prev[other_idx] and other_idx != idx:
                        combo_key = (idx, other_idx)
                        if combo_key in SWAP_MODIFIERS:
                            keyboard.release(current_mode[symbol_shift_idx])
                            keycode = None  # Don't release the original
                            break
            elif idx == symbol_shift_idx:
                # Check if we need to release swapped modifier
                for other_idx in range(matrix.key_count):
                    if prev[other_idx] and other_idx != idx:
                        combo_key = (idx, other_idx)
                        if combo_key in SWAP_MODIFIERS:
                            keyboard.release(current_mode[caps_shift_idx])
                            keycode = None  # Don't release the original
                            break
            
            if keycode is not None:
                keyboard.release(keycode)
            # Reset reported key when all keys are released
            if len([i for i in range(matrix.key_count) if pressed[i]]) == 0:
                last_reported_key = None
    
    # Now process all newly pressed keys together to detect combinations
    if newly_pressed:
        # Get all currently pressed keys (including ones that were already pressed)
        combo_indices = currently_pressed[:]
        
        # Track modifier presses for delayed reporting
        caps_shift_idx = 25
        symbol_shift_idx = 36
        for idx in newly_pressed:
            if idx == caps_shift_idx or idx == symbol_shift_idx:
                modifier_press_time[idx] = time.monotonic()
        
        # Get the Spectrum key name for this combination
        spectrum_name = get_spectrum_key_name(combo_indices)
        
        # Only report if this is a new combination (avoid duplicate reports)
        current_combo = tuple(sorted(combo_indices))
        if current_combo != last_reported_key:
            # Determine what to report
            if spectrum_name and len(combo_indices) > 1:
                # This is a combination - show the Spectrum key name
                # Clear any pending modifier reports since we have a combo
                modifier_press_time.clear()
                # Get PC keycode names for reporting
                pc_names = []
                for idx in combo_indices:
                    keycode = current_mode[idx]
                    pc_name = None
                    if hasattr(keycode, 'name'):
                        pc_name = keycode.name
                    if not pc_name:
                        keycode_value = int(keycode) if hasattr(keycode, '__int__') else keycode
                        for attr_name in dir(Keycode):
                            if not attr_name.startswith('_'):
                                attr_value = getattr(Keycode, attr_name)
                                if isinstance(attr_value, int) and attr_value == keycode_value:
                                    pc_name = attr_name
                                    break
                        if not pc_name:
                            pc_name = f"KEYCODE_{keycode_value}"
                    pc_names.append(pc_name)
                pc_name_str = " + ".join(pc_names) if pc_names else "UNKNOWN"
                print(f"Key pressed: {spectrum_name} ({pc_name_str})")
                last_reported_key = current_combo
            elif len(combo_indices) == 1:
                # Single key pressed - check if it's a modifier
                idx = combo_indices[0]
                if idx == caps_shift_idx or idx == symbol_shift_idx:
                    # Don't report modifier alone immediately - wait to see if combo arrives
                    # It will be reported in the else block if no combo comes
                    pass
                else:
                    # Non-modifier key - report it immediately
                    keycode = current_mode[idx]
                    pc_name = None
                    if hasattr(keycode, 'name'):
                        pc_name = keycode.name
                    if not pc_name:
                        keycode_value = int(keycode) if hasattr(keycode, '__int__') else keycode
                        for attr_name in dir(Keycode):
                            if not attr_name.startswith('_'):
                                attr_value = getattr(Keycode, attr_name)
                                if isinstance(attr_value, int) and attr_value == keycode_value:
                                    pc_name = attr_name
                                    break
                        if not pc_name:
                            pc_name = f"KEYCODE_{keycode_value}"
                    
                    if idx < len(SPECTRUM_KEY_NAMES):
                        print(f"Key pressed: {SPECTRUM_KEY_NAMES[idx]} ({pc_name})")
                    else:
                        print(f"Key pressed: {pc_name}")
                    last_reported_key = current_combo
            else:
                # Multiple keys but no special combination name
                names = []
                for idx in sorted(combo_indices):
                    if idx < len(SPECTRUM_KEY_NAMES):
                        names.append(SPECTRUM_KEY_NAMES[idx])
                    else:
                        names.append(f"KEY_{idx}")
                print(f"Key pressed: {' + '.join(names)}")
                last_reported_key = current_combo
    else:
        # No new keys pressed, but check if we have keys held that we haven't reported yet
        # This handles the case where CAPS SHIFT was pressed first, then number key arrives later
        if len(currently_pressed) > 0:
            current_combo = tuple(sorted(currently_pressed))
            if current_combo != last_reported_key:
                spectrum_name = get_spectrum_key_name(currently_pressed)
                if spectrum_name and len(currently_pressed) > 1:
                    # We have a combination that we haven't reported yet
                    # Clear any pending modifier reports
                    modifier_press_time.clear()
                    pc_names = []
                    for idx in currently_pressed:
                        keycode = current_mode[idx]
                        pc_name = None
                        if hasattr(keycode, 'name'):
                            pc_name = keycode.name
                        if not pc_name:
                            keycode_value = int(keycode) if hasattr(keycode, '__int__') else keycode
                            for attr_name in dir(Keycode):
                                if not attr_name.startswith('_'):
                                    attr_value = getattr(Keycode, attr_name)
                                    if isinstance(attr_value, int) and attr_value == keycode_value:
                                        pc_name = attr_name
                                        break
                            if not pc_name:
                                pc_name = f"KEYCODE_{keycode_value}"
                        pc_names.append(pc_name)
                    pc_name_str = " + ".join(pc_names) if pc_names else "UNKNOWN"
                    print(f"Key pressed: {spectrum_name} ({pc_name_str})")
                    last_reported_key = current_combo
                elif len(currently_pressed) == 1:
                    # Single modifier held - don't report modifiers alone
                    # They should only be reported as part of combinations
                    pass
    
    # Clean up modifier tracking for released keys
    for idx in list(modifier_press_time.keys()):
        if idx not in currently_pressed:
            del modifier_press_time[idx]

    prev = pressed[:]
    # Reduced sleep since we're already doing delays in the scan loop
    time.sleep(0.001)
