# Bring-Up & Test Plan — Unknown Board

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

## Firmware Programming
**P1. Flash firmware and open serial console @115200 baud.**
- Equipment: Programmer, USB cable
- Expected: Device boots without faults; serial console opens at 115200 baud

## Functional Tests
**T1. Power-On Self Test: Run `post`**
- Equipment: PC serial console
- Expected: PASS

**T2. Communication Test: Run `comm_test`**
- Equipment: PC serial console
- Expected: All interfaces responsive

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

## Close-out
**C1. Power-down and disconnect all equipment.**
- Equipment: None
- Expected: Board safely powered off, all connections removed

---
### Notes
Generated offline via deterministic template. Review tolerances and test point references before lab use.

Coverage Summary:
- rails: 0 found / 0 tested
- oscillators: 0 found / 0 tested
- functional_tests: 2 tests / 2 steps

LLM Enhancements:
# Bring-Up/Test Procedure for Unknown Board

## Setup
1. **Equipment Required:**
   - Power supply (0-12V, adjustable)
   - Multimeter
   - Oscilloscope
   - Communication interface (USB/Serial)
   - Test software for firmware programming
   - Test jig (if applicable)

2. **Safety Notes:**
   - Ensure all equipment is properly grounded.
   - Use ESD protection when handling the board.
   - Verify power supply settings before connecting to the board.

## Visual Inspection
1. Inspect the board for:
   - Physical damage (cracks, burns, etc.)
   - Proper soldering of components
   - Correct component placement
   - Cleanliness (no dust, debris, or solder splashes)

2. **Pass/Fail Criteria:**
   - **Pass:** No visible defects or issues.
   - **Fail:** Any visible damage or improper assembly.

## Voltage Rail Checks
1. **Procedure:**
   - Connect the power supply to the board.
   - Set the power supply to the required voltage (as per board specifications).

2. **Expected Values:**
   - Check all voltage rails (e.g., VCC, VDD, etc.).
   - Expected values: 3.3V ± 5%, 5V ± 5%, 12V ± 5% (adjust according to board specs).

3. **Pass/Fail Criteria:**
   - **Pass:** All voltage rails within specified tolerances.
   - **Fail:** Any voltage rail outside specified tolerances.

## Oscillator Checks
1. **Procedure:**
   - Use an oscilloscope to measure the output frequency of each oscillator on the board.

2. **Expected Values:**
   - Check frequency against specifications (e.g., 10MHz ± 100kHz).

3. **Pass/Fail Criteria:**
   - **Pass:** Frequency within specified tolerances.
   - **Fail:** Frequency outside specified tolerances.

## Firmware Programming
1. **Procedure:**
   - Connect the communication interface to the board.
   - Load the firmware using the provided test software.

2. **Safety Notes:**
   - Ensure the board is powered during programming.
   - Follow the manufacturer's instructions for firmware loading.

3. **Pass/Fail Criteria:**
   - **Pass:** Firmware loads successfully without errors.
   - **Fail:** Any errors during the firmware loading process.

## Functional Tests
1. **Power-On Self Test (POST):**
   - Execute command: `post`
   - **Expected Outcome:** All self-test checks pass without errors.

2. **Communication Test:**
   - Execute command: `comm_test`
   - **Expected Outcome:** Successful communication established with expected responses.

3. **Pass/Fail Criteria:**
   - **Pass:** All functional tests complete successfully.
   - **Fail:** Any test fails or produces errors.

## Notes
- Document all test results and observations.
- If any tests fail, troubleshoot the respective areas before re-testing.
- Ensure to follow all safety protocols throughout the testing process.

Validation Notes:
- No rails found; add at least one power rail.