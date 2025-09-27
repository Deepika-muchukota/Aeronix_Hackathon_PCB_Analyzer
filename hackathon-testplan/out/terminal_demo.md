# Bring-Up & Test Plan — Clemson LoRa Car Radio

## Setup
**S0. Quick continuity check: GND vs +5V/+3V3 not shorted**
- Equipment: DMM (diode/continuity)
- Expected: Rails not shorted to GND

**S1. ESD precautions; connect board to bench PSU and GND mat.**
- Equipment: ESD strap, bench PSU

**S2. Connect DMM probes to common GND and designated test points.**
- Equipment: DMM, probes

**S3. Set bench PSU to 5.0V and current limit to 200 mA; leave output disabled.**
- Equipment: Bench PSU
- Expected: PSU configured 5.0V, 0.2A limit

**S4. Enable PSU; verify current draw ≤ 0.2A, else power off and stop.**
- Equipment: Bench PSU, DMM
- Expected: Board stays below current limit

## Visual Inspection
**V0. Check component orientation, solder bridges, missing parts.**
- Equipment: Loupe
- Expected: IPC-610 Class 2 acceptable

## Voltage Rail Checks
**V1. Measure rail PWR_JACK**
- Equipment: DMM
- Expected: 5.00 V (allowed: 4.90–5.10 V)

**V2. Measure rail +3V3**
- Equipment: DMM
- Expected: 3.30 V (allowed: 3.20–3.40 V)

**V3. Measure rail +3V3_RF**
- Equipment: DMM
- Expected: 3.30 V (allowed: 3.20–3.40 V)

## Oscillator Checks
**O1. Probe oscillator Y1**
- Equipment: Oscilloscope
- Expected: ~16.000 MHz (allowed: 15.900–16.100 MHz)

**O2. Probe oscillator Y2**
- Equipment: Oscilloscope
- Expected: ~32.000 MHz (allowed: 31.900–32.100 MHz)

## Firmware Programming
**P1. Flash firmware and open serial console @115200 baud.**
- Equipment: Programmer, USB cable
- Expected: Device boots without faults; serial console opens at 115200 baud

## Functional Tests
**T1. Full BIT: Run `bit`**
- Equipment: PC serial console
- Expected: PASS

**T2. LoRa BIT: Run `bit.lora`**
- Equipment: PC serial console
- Expected: PASS

**T3. GPS BIT: Run `bit.gps`**
- Equipment: PC serial console
- Expected: PASS

**T4. IMU BIT: Run `bit.imu`**
- Equipment: PC serial console
- Expected: PASS

**T5. I2C BIT: Run `bit.i2c`**
- Equipment: PC serial console
- Expected: PASS

**T6. GPS Status: Run `gps.status`**
- Equipment: PC serial console
- Expected: Readable status

**T7. IMU Status: Run `imu.status`**
- Equipment: PC serial console
- Expected: Readable status

**T8. SPI Read: Run `spi.read <dev> <bytes>`**
- Equipment: PC serial console
- Expected: Returns <bytes> from <dev>

## Close-out
**C1. Power-down and disconnect all equipment.**
- Equipment: None
- Expected: Board safely powered off, all connections removed

---
### Notes
Generated offline via deterministic template. Review tolerances and test point references before lab use.