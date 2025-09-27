from __future__ import annotations
from typing import List
from core.models import ParsedEntities, TestPlan


def validate_entities(ent: ParsedEntities) -> List[str]:
    issues = []
    if not ent.rails:
        issues.append("No rails found; add at least one power rail.")
    seen = set()
    for r in ent.rails:
        key = (r.name.lower(), round(r.voltage, 3))
        if key in seen:
            issues.append(f"Duplicate rail entry: {r.name} {r.voltage}V")
        seen.add(key)
    return issues


def annotate_plan(plan: TestPlan, issues: List[str]) -> TestPlan:
    if not issues:
        return plan
    extra = "\n".join(f"- {i}" for i in issues)
    plan.notes = (plan.notes or "") + "\n\nValidation Notes:\n" + extra
    return plan
