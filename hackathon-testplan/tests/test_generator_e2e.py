from __future__ import annotations
from core.models import ParsedEntities
from core.generator import generate_plan_offline

def test_generate_plan_sections(sample_entities):
    ent = ParsedEntities.model_validate(sample_entities)
    plan = generate_plan_offline(ent)
    md = plan.to_markdown()
    # core sections present
    for sec in ["Setup","Visual Inspection","Voltage Rail Checks","Oscillator Checks","Firmware Programming","Functional Tests"]:
        assert sec in md
    # correct tolerance windows appear
    assert "4.90–5.10 V" in md
    assert "3.20–3.40 V" in md
