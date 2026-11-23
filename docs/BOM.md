# Bill of Materials

Prices are Taobao/Tmall prices in November 2026 (after discounts), in CNY. "~" = approximate or not recorded exactly.

## On the drone

| Part | Qty | Unit ¥ | Notes |
|---|---|---|---|
| Seeed XIAO ESP32-S3 (no camera) | 1 | 35.00 | Flight computer |
| AO3400A N-MOSFET, SOT-23 (UMW, marking X0DV), pack of 20 | 1 | ~4 | One per motor, rest are spares |
| SS34 Schottky diode, SMA | 4+ | ~2 per pack | Flyback, one per motor |
| 10 kΩ 0805 resistor | 4+ | ~ | Gate pull-down, one per motor |
| Perfboard, 2.54 mm, double-sided | 1 | ~ | A 4×4-hole piece is the whole driver board |
| 8520 coreless motor, 1 mm shaft, red/blue wires | 2 | ~5.70 | One rotation direction |
| 8520 coreless motor, 1 mm shaft, black/white wires | 2 | ~5.24 | Other rotation direction |
| 55 mm two-blade propellers, 1 mm shaft (pair) | 8 | 2.58 | Each pair = one CW + one CCW |
| 75 mm propellers | ~ | ~ | Arrived instead of 65 mm; to be compared |
| MPU6050 GY-521 module | 2 | 14.06 | 1 + 1 spare |
| 1S LiPo 3.7 V 550 mAh (902240), PH2.0 | 3 | 17.17 | Built-in protection board, 15.5 g measured |
| 1000 µF 10 V electrolytic capacitor (20 pcs) | 1 | 2.61 | Bulk capacitor on the power rail |
| PH2.0 board-side connector, 20 AWG | 1 | 1.80 | Main battery lead |
| 26 AWG silicone wire, 5 m | 1 | 3.99 | Power wiring |

## Bought, then replaced

| Part | Qty | Unit ¥ | Why replaced |
|---|---|---|---|
| DRV8833 dual H-bridge module | 6 | 5.70 | ~20 g thrust per motor vs ~35 g direct — too much loss on 1S |

## Borrowed from the lab for testing

- IRLB8721 MOSFET (TO-220) + 1N5822 diode — single-channel bench test that proved MOSFETs work (33 g thrust)
- Fluke 107 multimeter

## Still needed

- Frame — designing in CAD, printing on a Bambu printer
- Spare motors (they're consumables)
- Own multimeter, flux, solder wick, fine tweezers
- Later: distance sensor (VL53L1X) for altitude hold
