# PID on one axis -> two motor outputs (written while learning, Nov 21-22, 2026).
# Bench version: prints the motor commands instead of driving the motors.
# right = throttle + correction, left = throttle - correction
# correction = Kp*angle + Ki*kopilka + Kd*rate
#   kopilka ("piggy bank") = sum of angle*dt, limited to +-L (anti-windup)

from machine import Pin, I2C
import time
import struct

# ========= Settings =========
MPU = 0x68
throttle_tohold = 50   # base throttle, %
Kp = 0.9               # numbers are placeholders until tuned on a test stand
Ki = 0.1
Kd = 0.7
I_MAX = 10             # I may add at most 10 % of power
L = I_MAX / Ki         # piggy bank limit
# TODO: guard against Ki = 0
# TODO: if throttle < ~15 %, kopilka = 0 (drone on the ground)

# ========= Sensor =========
i2c = I2C(0, sda=Pin(5), scl=Pin(6), freq=400000)
print(i2c.scan())                         # expect [104]
i2c.writeto_mem(MPU, 0x6B, b'\x00')       # wake the sensor
time.sleep(3)

def read_gx_d():
    data = i2c.readfrom_mem(MPU, 0x3B, 14)
    ax, ay, az, temp, gx, gy, gz = struct.unpack('>hhhhhhh', data)
    return gx / 131

# ========= Calibration =========
summa = 0
length = 5000
for g in range(length):
    summa += read_gx_d()
mpu_error = summa / length
print("mpu_error:", mpu_error)

# ========= PID =========
def right(derivative, kopilka):
    a = throttle_tohold + Kp*angle_x + Ki*kopilka + Kd*derivative
    return max(0, min(100, round(a, 1)))      # clamp to 0..100 %

def left(derivative, kopilka):
    a = throttle_tohold - Kp*angle_x - Ki*kopilka - Kd*derivative
    return max(0, min(100, round(a, 1)))

# ========= Main loop =========
angle_x = 0
kopilka = 0
past = time.ticks_us()

while True:
    present = time.ticks_us()
    dt = time.ticks_diff(present, past) / 1_000_000
    past = present

    rate_x = read_gx_d() - mpu_error
    angle_x += rate_x * dt
    kopilka += angle_x * dt
    kopilka = max(-L, min(L, kopilka))        # anti-windup: limit the stored value itself

    r = right(rate_x, kopilka)
    l = left(rate_x, kopilka)
    print(f"{angle_x:.2f}, {kopilka:.2f}, {r}, {l}")
    time.sleep(0.01)
