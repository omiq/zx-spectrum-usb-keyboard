import time
import digitalio

class SpectrumMatrix:
    def __init__(self, row_pins, col_pins, settle_us=300):
        self.rows = []
        self.cols = []
        self.settle = settle_us / 1_000_000
        self.row_count = len(row_pins)
        self.col_count = len(col_pins)
        self.key_count = self.row_count * self.col_count

        for pin in row_pins:
            p = digitalio.DigitalInOut(pin)
            p.direction = digitalio.Direction.INPUT
            p.pull = digitalio.Pull.UP
            self.rows.append(p)

        for pin in col_pins:
            p = digitalio.DigitalInOut(pin)
            p.direction = digitalio.Direction.INPUT
            p.pull = digitalio.Pull.UP
            self.cols.append(p)

    def scan(self):
        result = [0] * self.key_count

        for c_index, c_pin in enumerate(self.cols):
            c_pin.direction = digitalio.Direction.OUTPUT
            c_pin.value = False
            time.sleep(self.settle)

            # Sample each row pin multiple times for more reliable detection
            # Require the pin to be low in multiple samples to confirm a key press
            for r_index, r_pin in enumerate(self.rows):
                # Sample the pin multiple times
                samples = []
                for _ in range(5):  # Sample 5 times
                    samples.append(not r_pin.value)
                    time.sleep(0.0001)  # 100us between samples
                
                # Require at least 3 out of 5 samples to be low to confirm key press
                # This helps filter out noise and ensures reliable detection
                if sum(samples) >= 3:
                    result[r_index * self.col_count + c_index] = 1

            c_pin.direction = digitalio.Direction.INPUT
            c_pin.pull = digitalio.Pull.UP
            time.sleep(self.settle)

        return result
