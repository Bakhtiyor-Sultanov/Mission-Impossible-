# "ENODEV" = nobody answers at address 0x68. This tries both pin orders and two
# bus speeds. [104] = MPU6050 found, [105] = address 0x69 (AD0 pulled high),
# [] everywhere = wiring/power problem (unplug everything for 10 s and check
# VCC-GND on the module, ~3.3 V).

from machine import Pin, I2C, SoftI2C

for sda, scl in ((5, 6), (6, 5), (9, 8), (8, 9)):   # first wiring, and on the frame
    for f in (100000, 400000):
        try:
            bus = I2C(0, sda=Pin(sda), scl=Pin(scl), freq=f)
            print("I2C  sda=%d scl=%d %d Hz ->" % (sda, scl, f), bus.scan())
        except Exception as e:
            print("I2C error:", e)
    bus = SoftI2C(sda=Pin(sda), scl=Pin(scl))
    print("Soft sda=%d scl=%d ->" % (sda, scl), bus.scan())
