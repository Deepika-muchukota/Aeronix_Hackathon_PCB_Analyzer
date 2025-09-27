from __future__ import annotations
from pathlib import Path
from typing import List

from pdfminer.high_level import extract_text

KEY_SECTIONS = ["Voltage", "Oscillator", "Programming", "Functional", "BIT", "Test"]


def extract_pdf_hints(pdf_path: str) -> List[str]:
    p = Path(pdf_path)
    if not p.exists():
        return []
    try:
        text = extract_text(pdf_path)
    except Exception:
        return []
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    hints = [ln for ln in lines if any(k.lower() in ln.lower() for k in KEY_SECTIONS)]
    return hints[:200]  # keep it light for MVP
