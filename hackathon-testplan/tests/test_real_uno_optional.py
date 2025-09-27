# tests/test_real_uno_optional.py
from __future__ import annotations
import os
from pathlib import Path
import pytest
from ingest.bom_parser import parse_bom
from ingest.netlist_parser import parse_netlist

@pytest.mark.skipif(not os.getenv("UNO_BOM_XLSX") or not Path(os.getenv("UNO_BOM_XLSX","")).exists(), reason="UNO_BOM_XLSX not set or file not found")
def test_uno_bom_xlsx_env():
    rows = parse_bom(os.getenv("UNO_BOM_XLSX"))
    assert rows, "BOM appears empty"
    assert any("16" in v and "MHZ" in v.upper() for _, v in rows)

@pytest.mark.skipif(not os.getenv("UNO_D356") or not Path(os.getenv("UNO_D356","")).exists(), reason="UNO_D356 not set or file not found")
def test_uno_netlist_d356_env():
    ent = parse_netlist(os.getenv("UNO_D356"))
    names = {r.name for r in ent.rails}
    assert any("5V" in n for n in names)
    assert any("3V3" in n for n in names)
