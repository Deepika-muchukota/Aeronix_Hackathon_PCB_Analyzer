#!/usr/bin/env python3
"""
Demo script for the Hackathon Test Plan Generator
Shows both offline and LLM-enhanced plan generation
"""

import json
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.models import ParsedEntities
from core.generator import generate_plan_offline
from nlp.llm_client import generate_plan_llm
from rules.validator import validate_entities, annotate_plan

def demo_offline_generation():
    """Demo offline deterministic plan generation"""
    print("🔧 Demo: Offline Test Plan Generation")
    print("=" * 50)
    
    # Load example entities
    with open("examples/lora_entities.json") as f:
        data = json.load(f)
    
    entities = ParsedEntities.model_validate(data)
    print(f"📋 Processing: {entities.title}")
    print(f"   - {len(entities.rails)} power rails")
    print(f"   - {len(entities.oscillators)} oscillators") 
    print(f"   - {len(entities.functional_tests)} functional tests")
    
    # Generate offline plan
    plan = generate_plan_offline(entities)
    issues = validate_entities(entities)
    plan = annotate_plan(plan, issues)
    
    print(f"\n📝 Generated plan with {len(plan.steps)} steps")
    print(f"   Sections: {', '.join(set(step.section for step in plan.steps))}")
    
    # Save to file
    output_path = Path("out/demo_offline.md")
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(plan.to_markdown())
    print(f"💾 Saved to: {output_path}")
    
    return plan

def demo_llm_generation():
    """Demo LLM-enhanced plan generation (if API key available)"""
    print("\n🤖 Demo: LLM-Enhanced Test Plan Generation")
    print("=" * 50)
    
    # Load example entities
    with open("examples/arduino_entities.json") as f:
        data = json.load(f)
    
    entities = ParsedEntities.model_validate(data)
    print(f"📋 Processing: {entities.title}")
    
    # Generate LLM plan (falls back to offline if no API key)
    plan = generate_plan_llm(entities)
    issues = validate_entities(entities)
    plan = annotate_plan(plan, issues)
    
    if plan.steps:
        print(f"📝 Generated structured plan with {len(plan.steps)} steps")
        output_path = Path("out/demo_llm.md")
        output_path.parent.mkdir(exist_ok=True)
        output_path.write_text(plan.to_markdown())
    else:
        print("📝 Generated LLM-enhanced markdown plan")
        output_path = Path("out/demo_llm.md")
        output_path.parent.mkdir(exist_ok=True)
        output_path.write_text(plan.notes or "")
    
    print(f"💾 Saved to: {output_path}")
    
    return plan

def main():
    print("🚀 Hackathon Test Plan Generator Demo")
    print("=" * 60)
    
    # Demo offline generation
    offline_plan = demo_offline_generation()
    
    # Demo LLM generation
    llm_plan = demo_llm_generation()
    
    print("\n✅ Demo completed!")
    print("\n📁 Generated files:")
    print("   - out/demo_offline.md (deterministic template)")
    print("   - out/demo_llm.md (LLM-enhanced or fallback)")
    print("\n🔧 To use the CLI:")
    print("   python -m app.cli examples/lora_entities.json --out out/my_plan.md")
    print("\n🌐 To use the web UI:")
    print("   streamlit run app/web.py")

if __name__ == "__main__":
    main()
