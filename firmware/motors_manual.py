# Four motors, throttle typed as "M1 M2 M3 M4" in percent (e.g. "20 0 0 0"),
# or one number for all four (e.g. "30"). "0" stops everything.
# Board: Seeed XIAO ESP32-S3, MicroPython. Driver: 4x AO3400A board.
# Run WITHOUT propellers first.

from machine import Pin, PWM

# Same order as PINS in pid_4motors.py, so "20 0 0 0" spins the motor
# that slot 1 of the mixer drives (should be front-right).
# First wiring (breadboard): [1, 43, 44, 8] = D0, D6, D7, D9
PINS = [44, 7, 5, 6]           # D7, D8, D4, D5 -> GPIO numbers (on the frame)

# Safety: drive every pin low first, then create PWM already at 0 % duty
for g in PINS:
    Pin(g, Pin.OUT, value=0)
motors = [PWM(Pin(g), freq=20000, duty_u16=0) for g in PINS]

def to_duty(p):
    p = max(0, min(100, p))                 # clamp to 0..100 %
    return int(p / 100 * 65535)

try:
    while True:
        line = input("M1 M2 M3 M4 %: ")
        try:
            values = [int(x) for x in line.split()]
        except ValueError:
            print("Numbers only, separated by spaces")
            continue
        if len(values) == 1:
            values = values * 4
        if len(values) != 4:
            print("Type 1 or 4 numbers")
            continue
        for m, v in zip(motors, values):
            m.duty_u16(to_duty(v))
        print("Throttle:", values)
finally:
    for m in motors:                        # Ctrl+C or any error -> all motors off
        m.duty_u16(0)
        m.deinit()
    for g in PINS:
        Pin(g, Pin.OUT, value=0)
