from __future__ import annotations
from ingest.netlist_parser import parse_netlist

SAMPLE_D356 = """\
M48
C  Project Name : Test Board
327 5V U1
327 5V U2
327 3V3 U3
327 3V3 U4
327 GND U1
327 GND U2
317 Y1 U5
317 16MHZ U5
"""

def test_parse_netlist_basic(tmp, write):
    p = write("board.d356", SAMPLE_D356)
    ent = parse_netlist(str(p))
    names = {r.name for r in ent.rails}
    assert "5V" in "".join(names)
    assert any("3V3" in n for n in names)
