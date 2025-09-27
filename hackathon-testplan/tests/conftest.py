# tests/conftest.py
from __future__ import annotations
import json, os, tempfile, sys
from pathlib import Path
import pytest

# Add project root to Python path for tests
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def tmp(tmp_path: Path):  # shorter alias
    return tmp_path

@pytest.fixture
def write(tmp):
    def _write(rel: str, data: str | bytes, mode: str = "w"):
        p = (tmp / rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        if "b" in mode:
            p.write_bytes(data if isinstance(data, bytes) else data.encode())
        else:
            p.write_text(data if isinstance(data, str) else data.decode())
        return p
    return _write

@pytest.fixture
def sample_entities():
    return {
        "title":"Smoke",
        "rails":[{"name":"+5V","voltage":5.0,"tolerance_mv":100},
                 {"name":"+3V3","voltage":3.3,"tolerance_mv":100}],
        "oscillators":[{"ref":"Y1","frequency_hz":16_000_000,"tolerance_hz":100_000}],
        "functional_tests":[{"name":"Ping","command":"bit","expected":"PASS"}],
    }

def real_fixture(path_env: str) -> Path | None:
    p = os.getenv(path_env)
    return Path(p) if p and Path(p).exists() else None
