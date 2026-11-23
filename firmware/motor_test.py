# Spin one motor at a throttle % typed in the terminal. My first motor code (Nov 14).
# Board: Seeed XIAO ESP32-S3, MicroPython.
# Written for the DRV8833 (D0 -> IN1+IN3); works the same with the MOSFET
# board (D0 -> gate of one channel).
# Run WITHOUT a propeller on the bench.

from machine import Pin, PWM

D0 = 1  # XIAO label D0 = GPIO1 (GPIO0 is the BOOT button!)

pwm = PWM(Pin(D0), freq=20000)  # 20 kHz: above hearing range, motor doesn't whine
pwm.duty_u16(0)                 # start stopped

while True:
    try:
        percent = int(input("Throttle %: "))
    except ValueError:
        print("Type a number 0-100")
        continue
    percent = max(0, min(100, percent))          # clamp to 0..100
    pwm.duty_u16(int(percent / 100 * 65535))
    print("Throttle set to", percent, "%")
