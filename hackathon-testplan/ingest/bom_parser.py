from __future__ import annotations
from typing import List, Tuple
from pathlib import Path

try:
    import openpyxl  # type: ignore
except Exception:
    openpyxl = None


def parse_bom(path: str) -> List[Tuple[str, str]]:
    """Return list of (refdes, value) if possible. Otherwise empty.
    Accepts .xlsx or .csv (very simple)."""
    p = Path(path)
    if not p.exists():
        return []

    if p.suffix.lower() == ".csv":
        rows = []
        import csv
        with open(p, newline="", encoding="utf-8", errors="ignore") as f:
            for r in csv.reader(f):
                if len(r) >= 2:
                    rows.append((r[0].strip(), r[1].strip()))
        return rows

    if p.suffix.lower() in (".xlsx", ".xlsm") and openpyxl is not None:
        wb = openpyxl.load_workbook(p)
        ws = wb.active
        rows = []
        for row in ws.iter_rows(values_only=True):
            if not row or len(row) < 2:
                continue
            ref, val = str(row[0]).strip(), str(row[1]).strip()
            rows.append((ref, val))
        return rows

    return []
