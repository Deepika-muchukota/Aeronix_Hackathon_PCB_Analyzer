from __future__ import annotations
import json
import sys
import argparse
from pathlib import Path
from rich import print

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.models import ParsedEntities
from core.generator import generate_plan_offline
from nlp.llm_client import generate_plan_llm
from rules.validator import validate_entities, annotate_plan
from ingest.netlist_parser import parse_netlist
from ingest.pdf_parser import extract_pdf_hints
from ingest.bom_parser import parse_bom
import re


def infer_entities_from_text(text: str, title: str = "Design") -> ParsedEntities:
    """Heuristically infer entities from text content"""
    T = text.upper()
    
    # Rails - look for voltage patterns
    rails = []
    voltage_patterns = [
        (r"\+?5V", 5.0), (r"\+?3V3", 3.3), (r"\+?3\.3V", 3.3),
        (r"VCC5", 5.0), (r"VCC3V3", 3.3), (r"PWR_JACK", 5.0)
    ]
    
    seen_voltages = set()
    for pattern, voltage in voltage_patterns:
        if re.search(pattern, T) and voltage not in seen_voltages:
            rails.append({"name": f"+{voltage:g}V" if voltage == 5.0 else f"+{voltage:g}V", 
                         "voltage": voltage, "tolerance_mv": 100})
            seen_voltages.add(voltage)
    
    # Oscillators - look for crystal references
    oscillators = []
    if "Y1" in T or "16MHZ" in T:
        oscillators.append({"ref": "Y1", "frequency_hz": 16000000, "tolerance_hz": 100000})
    if "Y2" in T or "32MHZ" in T:
        oscillators.append({"ref": "Y2", "frequency_hz": 32000000, "tolerance_hz": 100000})
    
    # Functional tests - infer from components
    functional_tests = []
    if "LORA" in T or "SX1276" in T:
        functional_tests.append({"name": "LoRa BIT", "command": "bit.lora", "expected": "PASS"})
    if "GPS" in T or "MAX-M10S" in T:
        functional_tests.append({"name": "GPS BIT", "command": "bit.gps", "expected": "PASS"})
    if "IMU" in T or "LSM6DSOX" in T:
        functional_tests.append({"name": "IMU BIT", "command": "bit.imu", "expected": "PASS"})
    if "I2C" in T:
        functional_tests.append({"name": "I2C BIT", "command": "bit.i2c", "expected": "PASS"})
    
    # Defaults if nothing found
    if not rails:
        rails = [{"name": "+5V", "voltage": 5.0, "tolerance_mv": 100},
                 {"name": "+3V3", "voltage": 3.3, "tolerance_mv": 100}]
    if not functional_tests:
        functional_tests.append({"name": "Full BIT", "command": "bit", "expected": "PASS"})
    
    return ParsedEntities.model_validate({
        "title": title,
        "rails": rails,
        "oscillators": oscillators,
        "functional_tests": functional_tests
    })


def auto_command(input_path: Path, out: Path = Path("out/plan.md"), offline: bool = False):
    """Auto-detect file type and generate plan"""
    suffix = input_path.suffix.lower()
    
    if suffix == ".json":
        data = json.loads(input_path.read_text())
        ent = ParsedEntities.model_validate(data)
    elif suffix in (".csv", ".xlsx", ".xlsm"):
        rows = parse_bom(str(input_path))
        blob = "\n".join(f"{r} {v}" for r, v in rows)
        ent = infer_entities_from_text(blob, title=input_path.name)
    elif suffix in (".schdoc", ".pcbdoc", ".prjpcb", ".bomdoc"):
        try:
            text = input_path.read_text(encoding="utf-8", errors="ignore")
        except:
            text = input_path.read_bytes().decode("latin-1", errors="ignore")
        ent = infer_entities_from_text(text, title=input_path.name)
    elif suffix == ".pdf":
        hints = extract_pdf_hints(str(input_path))
        text = "\n".join(hints)
        ent = infer_entities_from_text(text, title=input_path.name)
    elif suffix in (".txt", ".net", ".ipc"):
        ent = parse_netlist(str(input_path))
    else:
        print(f"[red]Error: Unsupported file type: {suffix}[/red]")
        sys.exit(1)

    plan = generate_plan_offline(ent) if offline else generate_plan_llm(ent)
    plan = annotate_plan(plan, validate_entities(ent))
    
    out.parent.mkdir(parents=True, exist_ok=True)
    entities_out = out.parent / "entities.json"
    entities_out.write_text(ent.model_dump_json(indent=2))
    
    md = plan.to_markdown() if plan.steps else (plan.notes or "")
    out.write_text(md)
    
    print(f"[green]Wrote {out} and {entities_out}[/green]")


def main():
    parser = argparse.ArgumentParser(description="Hardware bring-up/test plan generator")
    parser.add_argument("input", help="Path to design file (JSON, PDF, BOM, Altium, Netlist)")
    parser.add_argument("--out", default="out/testplan.md", help="Output markdown path")
    parser.add_argument("--offline", action="store_true", help="Force offline deterministic plan")
    parser.add_argument("--netlist", action="store_true", help="Input is a netlist file (IPC-D-356A format)")
    parser.add_argument("--auto", action="store_true", help="Auto-detect file type and generate both plan and entities")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[red]Error: File {input_path} does not exist[/red]")
        sys.exit(1)
    
    # Use auto command if requested
    if args.auto:
        auto_command(input_path, Path(args.out), args.offline)
        return
    
    # Parse input based on type
    if args.netlist or input_path.suffix.lower() in ['.net', '.txt', '.356']:
        print(f"[blue]Parsing netlist file: {input_path}[/blue]")
        try:
            ent = parse_netlist(str(input_path))
            print(f"[green]Extracted: {len(ent.rails)} rails, {len(ent.oscillators)} oscillators, {len(ent.functional_tests)} tests[/green]")
        except Exception as e:
            print(f"[red]Error parsing netlist: {e}[/red]")
            sys.exit(1)
    else:
        # Assume JSON format
        data = json.loads(input_path.read_text())
        ent = ParsedEntities.model_validate(data)

    issues = validate_entities(ent)
    plan = generate_plan_offline(ent) if args.offline else generate_plan_llm(ent)
    plan = annotate_plan(plan, issues)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    md = plan.to_markdown() if plan.steps else (plan.notes or "")
    out_path.write_text(md)
    print(f"[green]Wrote {out_path}[/green]")


if __name__ == "__main__":
    main()
