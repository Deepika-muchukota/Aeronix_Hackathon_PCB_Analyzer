from __future__ import annotations
from app.web import infer_entities_from_text

def test_infer_from_text_finds_rails_and_oscs():
    text = "Nets: +5V +3V3  Components: SX1276 LSM6DSOX MAX-M10S  Clocks: 16MHz, 32MHz"
    ent = infer_entities_from_text(text, title="Blob")
    rail_names = {r.name for r in ent.rails}
    assert any("5V" in n for n in rail_names)
    assert any("3.3V" in n for n in rail_names)
    assert any(int(o.frequency_hz/1e6) == 16 for o in ent.oscillators)
    # functional tests inferred from parts
    fn = {t.name for t in ent.functional_tests}
    assert "LoRa BIT" in fn and "IMU BIT" in fn and "GPS BIT" in fn
