from __future__ import annotations
from ingest.bom_parser import parse_bom

def test_parse_bom_csv(tmp, write):
    p = write("bom.csv", "Ref,Value\nY1,16MHz\nU1,3V3 Regulator\n")
    rows = parse_bom(str(p))
    assert ("Y1","16MHz") in rows
    assert any("3V3" in v for _, v in rows)

def test_parse_bom_xlsx(tmp):
    # create a tiny xlsx file on the fly
    from openpyxl import Workbook
    p = tmp / "bom.xlsx"
    wb = Workbook(); ws = wb.active
    ws.append(["Ref","Value"]); ws.append(["Y1","16MHz"]); ws.append(["JP1","+5V"])
    wb.save(p)
    rows = parse_bom(str(p))
    assert ("Y1","16MHz") in rows
    assert ("JP1","+5V") in rows
