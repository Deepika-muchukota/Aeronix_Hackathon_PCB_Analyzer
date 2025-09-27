#!/usr/bin/env python3
"""
Demo script to show file merging and evidence collection
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.web import infer_entities_from_text

def demo_file_merging():
    print("🔄 FILE MERGING DEMO")
    print("=" * 50)
    
    # Simulate multiple files being merged
    bom_text = """
    BOM.xlsx content:
    R1, 10k, Resistor
    U1, SX1276, LoRa Module  
    U2, MAX-M10S, GPS Receiver
    U3, LSM6DSOX, IMU Sensor
    """
    
    schematic_text = """
    Schematic.SchDoc content:
    NET +3V3
    NET +5V  
    NET I2C_SCL
    NET I2C_SDA
    Y1 16MHz Crystal
    """
    
    manual_text = """
    Manual.pdf content:
    The system uses 3.3V for GPS module
    Power input is 5V from external supply
    I2C bus connects all sensors
    """
    
    # Merge all texts
    merged_text = bom_text + "\n" + schematic_text + "\n" + manual_text
    print("📁 Files being merged:")
    print("  - BOM.xlsx (component list)")
    print("  - Schematic.SchDoc (net names)")  
    print("  - Manual.pdf (descriptions)")
    print()
    
    # Process merged text
    ent = infer_entities_from_text(merged_text, "BOM.xlsx | Schematic.SchDoc | Manual.pdf")
    
    print("🔍 EXTRACTED ENTITIES:")
    print(f"Title: {ent.title}")
    print(f"Rails: {len(ent.rails)}")
    print(f"Oscillators: {len(ent.oscillators)}")
    print(f"Functional Tests: {len(ent.functional_tests)}")
    print()
    
    return ent

def demo_evidence_system(ent):
    print("📋 EVIDENCE SYSTEM DEMO")
    print("=" * 50)
    
    print("Evidence shows the SOURCE of each test step:")
    print()
    
    for rail in ent.rails:
        print(f"🔌 Rail: {rail.name} ({rail.voltage}V)")
        for ev in rail.evidence:
            print(f"   📄 {ev}")
        print()
    
    for osc in ent.oscillators:
        print(f"⏰ Oscillator: {osc.ref} ({osc.frequency_hz/1e6:.1f}MHz)")
        for ev in osc.evidence:
            print(f"   📄 {ev}")
        print()
    
    for test in ent.functional_tests:
        print(f"🧪 Test: {test.name}")
        for ev in test.evidence:
            print(f"   📄 {ev}")
        print()

def demo_test_plan_generation(ent):
    print("📝 TEST PLAN GENERATION")
    print("=" * 50)
    
    from core.generator import generate_plan_offline
    
    plan = generate_plan_offline(ent)
    
    print("Generated test plan sections:")
    sections = {}
    for step in plan.steps:
        if step.section not in sections:
            sections[step.section] = []
        sections[step.section].append(step)
    
    for section, steps in sections.items():
        print(f"  📋 {section}: {len(steps)} steps")
        for step in steps[:2]:  # Show first 2 steps of each section
            print(f"    - {step.id}: {step.description}")
            if step.evidence:
                print(f"      Evidence: {step.evidence[0][:60]}...")
        if len(steps) > 2:
            print(f"    ... and {len(steps)-2} more steps")
        print()
    
    print("📊 Coverage Summary:")
    print(plan.notes.split("Coverage Summary:")[1].strip())

if __name__ == "__main__":
    print("🎯 HACKATHON TEST PLAN GENERATOR DEMO")
    print("=" * 60)
    print()
    
    # Demo 1: File Merging
    ent = demo_file_merging()
    
    # Demo 2: Evidence System  
    demo_evidence_system(ent)
    
    # Demo 3: Test Plan Generation
    demo_test_plan_generation(ent)
    
    print("✅ Demo complete! This shows how:")
    print("   1. Multiple files are merged into one text blob")
    print("   2. Evidence tracks which file/line triggered each test")
    print("   3. Test plans are generated with full traceability")
