# Spin the motors one after another: checks wiring, numbering and direction.
# Board: Seeed XIAO ESP32-S3, MicroPython. Run WITHOUT propellers first.

from machine import Pin, PWM
import time

# Same order as PINS in pid_4motors.py. First wiring: [1, 43, 44, 8]
PINS = [44, 7, 5, 6]           # D7, D8, D4, D5 (on the frame)
THROTTLE = 25                  # %
ON_TIME = 2                    # s
PAUSE = 1                      # s

for g in PINS:                 # all motors off before anything else
    Pin(g, Pin.OUT, value=0)
motors = [PWM(Pin(g), freq=20000, duty_u16=0) for g in PINS]

def to_duty(p):
    p = max(0, min(100, p))
    return int(p / 100 * 65535)

try:
    while True:
        for i, m in enumerate(motors):
            print("Motor", i + 1)
            m.duty_u16(to_duty(THROTTLE))
            time.sleep(ON_TIME)
            m.duty_u16(0)
            time.sleep(PAUSE)
finally:
    for m in motors:
        m.duty_u16(0)
        m.deinit()
    for g in PINS:
        Pin(g, Pin.OUT, value=0)
