# Read the MPU6050 over I2C and print acceleration, rotation and temperature.
# Board: Seeed XIAO ESP32-S3, MicroPython.
# Wiring: VCC -> 3V3, GND -> GND, SDA -> D4 (GPIO5), SCL -> D5 (GPIO6).

from machine import Pin, I2C
import struct
import time

MPU = 0x68  # I2C address (shows up as 104 in i2c.scan())

# First wiring: SDA = GPIO5 (D4), SCL = GPIO6 (D5). On the frame: sda=Pin(9), scl=Pin(8)
i2c = I2C(0, sda=Pin(5), scl=Pin(6), freq=400000)
print("I2C devices:", i2c.scan())   # expect [104]

i2c.writeto_mem(MPU, 0x6B, b'\x00')  # wake up: the MPU6050 boots asleep

while True:
    data = i2c.readfrom_mem(MPU, 0x3B, 14)  # accel(6) + temp(2) + gyro(6)
    ax, ay, az, temp, gx, gy, gz = struct.unpack('>hhhhhhh', data)

    # default ranges: ±2 g -> 16384 per g, ±250 °/s -> 131 per °/s
    print(f"Accel g: {ax/16384:.2f} {ay/16384:.2f} {az/16384:.2f} | "
          f"Gyro °/s: {gx/131:.1f} {gy/131:.1f} {gz/131:.1f} | "
          f"Temp: {temp/340 + 36.53:.1f} C")
    time.sleep(0.2)
