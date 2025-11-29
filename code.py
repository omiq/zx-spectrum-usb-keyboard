import time
import board
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

from matrix_scanner import SpectrumMatrix
from lookup_tables import (
    pc_mode, 
    spectrum_mode,
    SPECTRUM_KEY_NAMES,
    CAPS_SHIFT_COMBOS,
    SYMBOL_SHIFT_COMBOS,
    SPECIAL_KEY_HID_MAP,
    SWAP_MODIFIERS
)

# Choose your mode switch pin (optional)
mode_switch = None  # you can add a GPIO for switching modes

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
sent_keycodes = {}  # Track which keycodes we've sent (by matrix index) to allow releasing if needed

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
    
    # Check if the newly pressed keys form a special key combination
    # Do this BEFORE sending individual keys to avoid sending modifiers
    if newly_pressed:
        combo_indices = currently_pressed[:]
        spectrum_name = get_spectrum_key_name(combo_indices)
        
        # Check if this is a special key that has a direct HID mapping
        if spectrum_name and spectrum_name in SPECIAL_KEY_HID_MAP:
            special_keycode = SPECIAL_KEY_HID_MAP[spectrum_name]
            if special_keycode is not None:
                # Release any modifiers that were already sent (they're part of this special key)
                caps_shift_idx = 25
                symbol_shift_idx = 36
                if caps_shift_idx in sent_keycodes:
                    keyboard.release(sent_keycodes[caps_shift_idx])
                    del sent_keycodes[caps_shift_idx]
                if symbol_shift_idx in sent_keycodes:
                    keyboard.release(sent_keycodes[symbol_shift_idx])
                    del sent_keycodes[symbol_shift_idx]
                # Also release the other key if it was already sent
                for idx in combo_indices:
                    if idx != caps_shift_idx and idx != symbol_shift_idx and idx in sent_keycodes:
                        keyboard.release(sent_keycodes[idx])
                        del sent_keycodes[idx]
                
                # Send the special HID keycode directly - don't send modifiers
                keyboard.press(special_keycode)
                # Skip sending individual keys for this iteration
                newly_pressed = []
    
    # Now send individual keys (if not part of a special key combo)
    for idx in newly_pressed:
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
        # Track that we sent this keycode
        sent_keycodes[idx] = keycode
    
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
                # Remove from tracking
                if idx in sent_keycodes:
                    del sent_keycodes[idx]
            # Reset reported key when all keys are released
            if len([i for i in range(matrix.key_count) if pressed[i]]) == 0:
                last_reported_key = None
                sent_keycodes.clear()
    
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
