# Roll + pitch PID, mixed into four motors. My flight code as of Nov 23, 2026.
# Comments are in Russian — that's how I wrote it.

from machine import Pin, PWM, I2C
import time
import struct

# ========= Моторы — САМЫМ ПЕРВЫМ, сразу в 0 =========
# Слоты миксера (см. mix): 1 правый перед, 2 левый перед, 3 левый зад, 4 правый зад.
# Порядок PINS должен попадать в эти углы на РЕАЛЬНОЙ раме — проверь motors_manual.py
# ("20 0 0 0" = правый передний). Неправильная нумерация: FAILURES.md #23.
PINS = [44, 7, 5, 6]                      # GPIO для M1, M2, M3, M4
motors = [PWM(Pin(g), freq=20000, duty_u16=0) for g in PINS]

def stop_all():
    for m in motors:
        m.duty_u16(0)

stop_all()

# ========= Светодиод-индикатор (горит от 0) =========
# горит = калибровка | погас = работает | часто мигает = нет MPU | медленно мигает = ошибка в цикле
led = Pin(21, Pin.OUT)
led.value(0)

def blink_forever(period):
    while True:
        led.value(not led.value())
        time.sleep(period)

# ========= Настройки =========
MOTORS_ON = True   # False = моторы не крутятся, только печать (проверка знаков)
                    # True  = моторы работают
MAX_PCT =30        # потолок газа на первых тестах
RUN_TIME_S = 50     # с моторами: через столько секунд всё выключится само
STOP_ANGLE = 85     # с моторами: наклон больше этого — аварийный стоп

MPU = 0x68
throttle_tohold = 15    # базовый газ, % (поставь свой порог трогания моторов)
Kp = 0.9
Ki = 0.5
Kd = 0.7
Kopilka_blocker = 10    # I не даёт больше 10% мощности

# Оси. После теста наклоном меняй ТОЛЬКО здесь, формулы не трогай.
# Нужно: опустил нос → angle_x растёт; опустил левую сторону → angle_y растёт
SWAP_XY = False     # True, если стрелка X на плате MPU смотрит вперёд
SIGN_X = -1          # -1, если angle_x идёт не в ту сторону
SIGN_Y = 1          # -1, если angle_y идёт не в ту сторону

# ========= Датчик =========
i2c = I2C(0, sda=Pin(9), scl=Pin(8), freq=100000)
found = i2c.scan()
print(found)                               # ждём [104]
if MPU not in found:
    blink_forever(0.1)                     # MPU не найден → быстрое мигание
i2c.writeto_mem(MPU, 0x6B, b'\x00')        # разбудить датчик
time.sleep(3)

def read_gyro():
    data = i2c.readfrom_mem(MPU, 0x43, 6)  # gx, gy, gz одним чтением
    gx, gy, gz = struct.unpack('>hhh', data)
    gx, gy = gx / 131, gy / 131            # °/с
    if SWAP_XY:
        gx, gy = gy, gx
    return SIGN_X * gx, SIGN_Y * gy

# ========= Калибровка (не трогай дрон) =========
summa_x = 0
summa_y = 0
length = 5000
for _ in range(length):
    gx, gy = read_gyro()
    summa_x += gx
    summa_y += gy
mpu_error_x = summa_x / length
mpu_error_y = summa_y / length
print("mpu_error_x:", mpu_error_x)
print("mpu_error_y:", mpu_error_y)

# ========= Миксер =========
# px > 0 → передние (M1, M2) сильнее;  py > 0 → левые (M2, M3) сильнее
def mix(px, py):
    m1 = throttle_tohold + px - py   # правый верх
    m2 = throttle_tohold + px + py   # левый верх
    m3 = throttle_tohold - px + py   # левый низ
    m4 = throttle_tohold - px - py   # правый низ
    return [max(0, min(MAX_PCT, round(v, 1))) for v in (m1, m2, m3, m4)]

# TODO 2: если газ ниже ~15%, kopilka = 0

led.value(1)                               # калибровка закончилась → погас

# ========= Основной цикл =========
L = Kopilka_blocker / Ki
angle_x = 0
angle_y = 0
kopilka_x = 0
kopilka_y = 0
start = past = time.ticks_us()
n = 0
error = None

try:
    while True:
        present = time.ticks_us()
        dt = time.ticks_diff(present, past) / 1_000_000   # мкс → секунды
        past = present

        gx, gy = read_gyro()
        rate_x = gx - mpu_error_x
        rate_y = gy - mpu_error_y
        angle_x += rate_x * dt
        angle_y += rate_y * dt

        if MOTORS_ON:
            if time.ticks_diff(present, start) > RUN_TIME_S * 1_000_000:
                print("Время вышло — стоп")
                break
            if abs(angle_x) > STOP_ANGLE or abs(angle_y) > STOP_ANGLE:
                print("Слишком большой наклон — стоп")
                break

        kopilka_x = max(-L, min(L, kopilka_x + angle_x * dt))
        kopilka_y = max(-L, min(L, kopilka_y + angle_y * dt))

        px = Kp * angle_x + Ki * kopilka_x + Kd * rate_x
        py = Kp * angle_y + Ki * kopilka_y + Kd * rate_y
        out = mix(px, py)

        if MOTORS_ON:
            for m, p in zip(motors, out):
                m.duty_u16(int(p / 100 * 65535))

        n += 1
        if n % 5 == 0:
            print(f"x {angle_x:6.1f}  y {angle_y:6.1f} | M1 {out[0]}  M2 {out[1]}  M3 {out[2]}  M4 {out[3]}")
        time.sleep(0.01)
except Exception as e:
    error = e
finally:
    stop_all()
    for m in motors:
        m.deinit()
    for g in PINS:
        Pin(g, Pin.OUT, value=0)    # после deinit держим пины в 0
    print("Моторы выключены")

if error:
    print("Ошибка:", error)
    blink_forever(0.5)                     # ошибка в цикле → медленное мигание