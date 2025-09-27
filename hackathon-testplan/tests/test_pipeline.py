from __future__ import annotations
import json
from core.models import ParsedEntities
from core.generator import generate_plan_offline


def test_offline_plan():
    data = {
        "title": "SmokeTest",
        "rails": [{"name": "+5V", "voltage": 5.0, "tolerance_mv": 100}],
        "oscillators": [{"ref": "Y1", "frequency_hz": 16_000_000, "tolerance_hz": 100_000}],
        "functional_tests": [{"name": "Ping", "command": "bit.ping", "expected": "PASS"}],
    }
    ent = ParsedEntities.model_validate(data)
    plan = generate_plan_offline(ent)
    assert plan.title.startswith("Bring-Up & Test Plan")
    md = plan.to_markdown()
    assert "Voltage Rail Checks" in md
    assert "Oscillator Checks" in md
