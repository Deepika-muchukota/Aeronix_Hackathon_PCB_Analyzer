from __future__ import annotations
from typing import List
from core.models import ParsedEntities, TestPlan, TestStep

BASE_SETUP_STEPS = [
    TestStep(id="S0", section="Setup", description="Quick continuity check: GND vs +5V/+3V3 not shorted", equipment="DMM (diode/continuity)", expected="Rails not shorted to GND"),
    TestStep(id="S1", section="Setup", description="ESD precautions; connect board to bench PSU and GND mat.", equipment="ESD strap, bench PSU"),
    TestStep(id="S2", section="Setup", description="Connect DMM probes to common GND and designated test points.", equipment="DMM, probes"),
    TestStep(id="S3", section="Setup", description="Set bench PSU to 5.0V and current limit to 200 mA; leave output disabled.", equipment="Bench PSU", expected="PSU configured 5.0V, 0.2A limit"),
    TestStep(id="S4", section="Setup", description="Enable PSU; verify current draw ≤ 0.2A, else power off and stop.", equipment="Bench PSU, DMM", expected="Board stays below current limit"),
]


def _voltage_steps(entities: ParsedEntities) -> List[TestStep]:
    steps: List[TestStep] = []
    for idx, r in enumerate(entities.rails, start=1):
        lo = r.voltage - r.tolerance_mv/1000
        hi = r.voltage + r.tolerance_mv/1000
        steps.append(TestStep(
            id=f"V{idx}",
            section="Voltage Rail Checks",
            description=f"Measure rail {r.name}",
            equipment="DMM",
            expected=f"{r.voltage:.2f} V (allowed: {lo:.2f}–{hi:.2f} V)"
        ))
    return steps


def _osc_steps(entities: ParsedEntities) -> List[TestStep]:
    steps: List[TestStep] = []
    for idx, o in enumerate(entities.oscillators, start=1):
        lo = o.frequency_hz - o.tolerance_hz
        hi = o.frequency_hz + o.tolerance_hz
        mhz = o.frequency_hz/1e6
        steps.append(TestStep(
            id=f"O{idx}",
            section="Oscillator Checks",
            description=f"Probe oscillator {o.ref}",
            equipment="Oscilloscope",
            expected=f"~{mhz:.3f} MHz (allowed: {lo/1e6:.3f}–{hi/1e6:.3f} MHz)"
        ))
    return steps


def _functional_steps(entities: ParsedEntities) -> List[TestStep]:
    steps: List[TestStep] = []
    for idx, t in enumerate(entities.functional_tests, start=1):
        expected = t.expected or "Return PASS or expected telemetry"
        cmd = (f"Run `{t.command}`" if t.command else f"Execute {t.name}")
        steps.append(TestStep(
            id=f"T{idx}",
            section="Functional Tests",
            description=f"{t.name}: {cmd}",
            equipment="PC serial console",
            expected=expected
        ))
    return steps


def _negative_tests(entities: ParsedEntities) -> List[TestStep]:
    """Add boundary checks and edge cases"""
    steps: List[TestStep] = []
    
    # Over-current protection (already in setup, but add explicit test)
    steps.append(TestStep(
        id="N1",
        section="Edge Cases & Fail-safes",
        description="Verify over-current protection: gradually increase load until PSU current limit triggers",
        equipment="Variable load, DMM",
        expected="PSU shuts down at 200mA limit"
    ))
    
    # Brown-out reboot test
    steps.append(TestStep(
        id="N2", 
        section="Edge Cases & Fail-safes",
        description="Brown-out test: reduce input voltage to 4.0V and verify graceful shutdown",
        equipment="Variable PSU, DMM",
        expected="System shuts down cleanly without damage"
    ))
    
    # I2C bus scan if I2C detected
    if any("I2C" in t.name.upper() or "I2C" in (t.command or "").upper() for t in entities.functional_tests):
        steps.append(TestStep(
            id="N3",
            section="Edge Cases & Fail-safes", 
            description="I2C bus scan: probe all addresses 0x08-0x77 for unexpected devices",
            equipment="I2C analyzer or scope",
            expected="Only expected devices respond"
        ))
    
    return steps


def generate_plan_offline(entities: ParsedEntities) -> TestPlan:
    steps: List[TestStep] = []
    steps.extend(BASE_SETUP_STEPS)
    steps.append(TestStep(id="V0", section="Visual Inspection", description="Check component orientation, solder bridges, missing parts.", equipment="Loupe", expected="IPC-610 Class 2 acceptable"))
    steps.extend(_voltage_steps(entities))
    steps.extend(_osc_steps(entities))
    steps.append(TestStep(id="P1", section="Firmware Programming", description="Flash firmware and open serial console @115200 baud.", equipment="Programmer, USB cable", expected="Device boots without faults; serial console opens at 115200 baud"))
    steps.extend(_functional_steps(entities))
    
    # Add negative/edge tests
    steps.extend(_negative_tests(entities))
    
    steps.append(TestStep(id="C1", section="Close-out", description="Power-down and disconnect all equipment.", equipment="None", expected="Board safely powered off, all connections removed"))
    
    # Add coverage summary
    voltage_steps = [s for s in steps if s.section == "Voltage Rail Checks"]
    osc_steps = [s for s in steps if s.section == "Oscillator Checks"]
    func_steps = [s for s in steps if s.section == "Functional Tests"]
    
    covered = {
        "rails": f"{len(entities.rails)} found / {len(voltage_steps)} tested",
        "oscillators": f"{len(entities.oscillators)} found / {len(osc_steps)} tested", 
        "functional_tests": f"{len(entities.functional_tests)} tests / {len(func_steps)} steps"
    }
    
    notes = "Generated offline via deterministic template. Review tolerances and test point references before lab use."
    notes += "\n\nCoverage Summary:\n- " + "\n- ".join([f"{k}: {v}" for k, v in covered.items()])
    
    return TestPlan(title=f"Bring-Up & Test Plan — {entities.title}", steps=steps, notes=notes)
