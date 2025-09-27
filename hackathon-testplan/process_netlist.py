#!/usr/bin/env python3
"""
Quick script to process a netlist file and generate a test plan
Usage: python process_netlist.py <netlist_file> [output_file]
"""

import sys
import json
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ingest.netlist_parser import parse_netlist, extract_test_points
from core.generator import generate_plan_offline
from rules.validator import validate_entities, annotate_plan

def main():
    if len(sys.argv) < 2:
        print("Usage: python process_netlist.py <netlist_file> [output_file]")
        print("Example: python process_netlist.py my_board.netlist")
        sys.exit(1)
    
    netlist_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "out/board_testplan.md"
    
    print(f"🔧 Processing netlist: {netlist_file}")
    
    try:
        # Parse the netlist
        entities = parse_netlist(netlist_file)
        print(f"📋 Extracted entities:")
        print(f"   - Title: {entities.title}")
        print(f"   - Power rails: {len(entities.rails)}")
        for rail in entities.rails:
            print(f"     * {rail.name}: {rail.voltage}V")
        print(f"   - Oscillators: {len(entities.oscillators)}")
        for osc in entities.oscillators:
            print(f"     * {osc.ref}: {osc.frequency_hz/1e6:.1f} MHz")
        print(f"   - Functional tests: {len(entities.functional_tests)}")
        
        # Extract test points
        test_points = extract_test_points(netlist_file)
        if test_points:
            print(f"   - Test points: {len(test_points)}")
            for tp in test_points[:5]:  # Show first 5
                print(f"     * {tp['ref']} on {tp['net']}")
            if len(test_points) > 5:
                print(f"     ... and {len(test_points) - 5} more")
        
        # Generate test plan
        issues = validate_entities(entities)
        plan = generate_plan_offline(entities)
        plan = annotate_plan(plan, issues)
        
        # Save output
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(plan.to_markdown())
        
        print(f"✅ Generated test plan: {output_path}")
        print(f"📄 Plan contains {len(plan.steps)} test steps")
        
        # Also save extracted entities as JSON for reference
        entities_json = output_path.with_suffix('.entities.json')
        entities_json.write_text(json.dumps(entities.model_dump(), indent=2))
        print(f"💾 Saved entities JSON: {entities_json}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
