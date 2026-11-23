# Tilt angle from the gyroscope (written while learning, Nov 21, 2026).
# 1. calibrate: average the gyro while the board lies still -> that's its error
# 2. angle += (rate - error) * dt, with dt measured every loop
# Result: 90 deg reads 90 deg; drift ~2.2 deg in ~7 min.
# Board: XIAO ESP32-S3. MPU6050: SDA -> D4 (GPIO5), SCL -> D5 (GPIO6).

from machine import Pin, I2C
import time
import struct

MPU = 0x68
# First wiring: SDA = GPIO5 (D4), SCL = GPIO6 (D5). On the frame: sda=Pin(9), scl=Pin(8)
i2c = I2C(0, sda=Pin(5), scl=Pin(6), freq=400000)
print(i2c.scan())                         # expect [104]
i2c.writeto_mem(MPU, 0x6B, b'\x00')       # wake the sensor
time.sleep(3)                             # let it settle (changed the offset from -2.02 to -1.55)

def read_gx_d():
    data = i2c.readfrom_mem(MPU, 0x3B, 14)
    ax, ay, az, temp, gx, gy, gz = struct.unpack('>hhhhhhh', data)
    return gx / 131                       # deg/s at the default +-250 deg/s range

# --- calibration: don't touch the board ---
summa = 0
length = 5000
for g in range(length):
    summa += read_gx_d()
mpu_error = summa / length
print("mpu_error:", mpu_error)

# --- angle ---
angle_x = 0
past = time.ticks_us()
while True:
    present = time.ticks_us()
    dt = time.ticks_diff(present, past) / 1_000_000    # microseconds -> seconds
    past = present

    rate_x = read_gx_d() - mpu_error      # clean rotation speed = derivative of the angle
    angle_x += rate_x * dt                # angle = sum of (speed x time)
    print(f"{dt:.4f}  {angle_x:.2f}")
    time.sleep(0.01)
