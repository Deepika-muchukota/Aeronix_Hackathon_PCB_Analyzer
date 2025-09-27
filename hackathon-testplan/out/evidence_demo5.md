# Bring-Up & Test Plan — test_evidence2.txt

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
**V1. Measure rail +3.3V**
- Equipment: DMM
- Expected: 3.30 V (allowed: 3.20–3.40 V)

**V2. Measure rail +5V**
- Equipment: DMM
- Expected: 5.00 V (allowed: 4.90–5.10 V)

## Oscillator Checks
**O1. Probe oscillator Y1**
- Equipment: Oscilloscope
- Expected: ~16.000 MHz (allowed: 15.900–16.100 MHz)
- Evidence:
  - Y1 16MHZ crystal for main MCU

**O2. Probe oscillator Y2**
- Equipment: Oscilloscope
- Expected: ~32.000 MHz (allowed: 31.900–32.100 MHz)
- Evidence:
  - Y2 32MHZ crystal for RF section

## Firmware Programming
**P1. Flash firmware and open serial console @115200 baud.**
- Equipment: Programmer, USB cable
- Expected: Device boots without faults; serial console opens at 115200 baud

## Functional Tests
**T1. LoRa BIT: Run `bit.lora`**
- Equipment: PC serial console
- Expected: PASS

**T2. GPS BIT: Run `bit.gps`**
- Equipment: PC serial console
- Expected: PASS

**T3. GPS Status: Run `gps.status`**
- Equipment: PC serial console
- Expected: Readable status

**T4. IMU BIT: Run `bit.imu`**
- Equipment: PC serial console
- Expected: PASS

**T5. IMU Status: Run `imu.status`**
- Equipment: PC serial console
- Expected: Readable status

**T6. I2C BIT: Run `bit.i2c`**
- Equipment: PC serial console
- Expected: PASS

## Edge Cases & Fail-safes
**N1. Verify over-current protection: gradually increase load until PSU current limit triggers**
- Equipment: Variable load, DMM
- Expected: PSU shuts down at 200mA limit
- Evidence:
  - Current limit protection required for safety

**N2. Brown-out test: reduce input voltage to 4.0V and verify graceful shutdown**
- Equipment: Variable PSU, DMM
- Expected: System shuts down cleanly without damage
- Evidence:
  - Brown-out protection standard for 5V systems

**N3. I2C bus scan: probe all addresses 0x08-0x77 for unexpected devices**
- Equipment: I2C analyzer or scope
- Expected: Only expected devices respond
- Evidence:
  - I2C bus integrity check for fault detection

## Close-out
**C1. Power-down and disconnect all equipment.**
- Equipment: None
- Expected: Board safely powered off, all connections removed

---
### Notes
Generated offline via deterministic template. Review tolerances and test point references before lab use.

Coverage Summary:
- rails: 2 found / 2 tested
- oscillators: 2 found / 2 tested
- functional_tests: 6 tests / 6 steps

LLM Enhancements:
# Hardware Bring-Up/Test Procedure

## Setup
1. **Equipment Required:**
   - Multimeter
   - Oscilloscope
   - Power Supply
   - Test Fixture
   - Computer with appropriate software for firmware programming and functional tests

2. **Safety Notes:**
   - Ensure all equipment is properly grounded.
   - Follow ESD precautions when handling the board.
   - Verify that the power supply is set to the correct voltage levels before connecting to the board.

## Visual Inspection
1. Inspect the board for:
   - Physical damage (cracks, burns, etc.)
   - Proper soldering of components
   - Correct placement of components
   - No foreign objects or debris on the board

2. **Pass/Fail Criteria:**
   - **Pass:** No visible defects or issues.
   - **Fail:** Any visible defects or issues.

## Voltage Rail Checks
1. **Procedure:**
   - Connect the power supply to the board.
   - Measure the voltage at the designated test points for each rail.

2. **Expected Values:**
   - +3.3V: 3.3 V ±100 mV
   - +5V: 5.0 V ±100 mV

3. **Pass/Fail Criteria:**
   - **Pass:** Measured voltages are within specified tolerances.
   - **Fail:** Any measured voltage outside specified tolerances.

## Oscillator Checks
1. **Procedure:**
   - Use an oscilloscope to measure the output frequency of each oscillator.

2. **Expected Values:**
   - Y1: 16.0 MHz ±100 kHz
   - Y2: 32.0 MHz ±100 kHz

3. **Pass/Fail Criteria:**
   - **Pass:** Measured frequencies are within specified tolerances.
   - **Fail:** Any measured frequency outside specified tolerances.

## Firmware Programming
1. **Procedure:**
   - Connect the board to the computer.
   - Load the firmware using the appropriate programming software.

2. **Pass/Fail Criteria:**
   - **Pass:** Firmware loads successfully without errors.
   - **Fail:** Any errors during firmware loading.

## Functional Tests
1. **Procedure:**
   - Execute the following commands sequentially:
     - LoRa BIT: `cmd=bit.lora`
     - GPS BIT: `cmd=bit.gps`
     - GPS Status: `cmd=gps.status`
     - IMU BIT: `cmd=bit.imu`
     - IMU Status: `cmd=imu.status`
     - I2C BIT: `cmd=bit.i2c`

2. **Pass/Fail Criteria:**
   - **Pass:** All tests return expected results without errors.
   - **Fail:** Any test fails or returns unexpected results.

## Notes
- Ensure all tests are conducted in a controlled environment to avoid external interference.
- Document all measurements and results for future reference.
- If any test fails, troubleshoot the specific area before proceeding with further tests.