from __future__ import annotations
from core.models import ParsedEntities
from rules.validator import validate_entities, annotate_plan
from core.generator import generate_plan_offline

def test_validate_entities_empty_rails():
    ent = ParsedEntities(
        title="Test",
        rails=[],
        oscillators=[],
        functional_tests=[]
    )
    issues = validate_entities(ent)
    assert "No rails found" in issues[0]

def test_validate_entities_duplicate_rails():
    ent = ParsedEntities(
        title="Test",
        rails=[
            {"name": "+5V", "voltage": 5.0, "tolerance_mv": 100},
            {"name": "+5V", "voltage": 5.0, "tolerance_mv": 100}
        ],
        oscillators=[],
        functional_tests=[]
    )
    issues = validate_entities(ent)
    assert "Duplicate rail entry" in issues[0]

def test_validate_entities_valid():
    ent = ParsedEntities(
        title="Test",
        rails=[
            {"name": "+5V", "voltage": 5.0, "tolerance_mv": 100},
            {"name": "+3V3", "voltage": 3.3, "tolerance_mv": 100}
        ],
        oscillators=[],
        functional_tests=[]
    )
    issues = validate_entities(ent)
    assert len(issues) == 0

def test_annotate_plan_with_issues():
    ent = ParsedEntities(
        title="Test",
        rails=[],
        oscillators=[],
        functional_tests=[]
    )
    plan = generate_plan_offline(ent)
    issues = validate_entities(ent)
    annotated_plan = annotate_plan(plan, issues)
    
    assert "Validation Notes" in annotated_plan.notes
    assert "No rails found" in annotated_plan.notes
