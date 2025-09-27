from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys

def test_cli_generate(tmp, sample_entities):
    epath = tmp / "e.json"
    epath.write_text(json.dumps(sample_entities))
    out = tmp / "plan.md"
    
    # Use subprocess to test CLI
    result = subprocess.run([
        sys.executable, "-m", "app.cli", 
        str(epath), "--out", str(out), "--offline"
    ], capture_output=True, text=True)
    
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert out.exists()
    md = out.read_text()
    assert "Voltage Rail Checks" in md
