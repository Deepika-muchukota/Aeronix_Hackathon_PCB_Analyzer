from __future__ import annotations
import zipfile
from pathlib import Path
from typing import List


def extract_zip(zip_path: str, out_dir: str) -> List[str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(out)
        return [str(out / n) for n in zf.namelist()]
