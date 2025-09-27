from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

class PowerRail(BaseModel):
    name: str
    voltage: float
    tolerance_mv: int = 100

class Oscillator(BaseModel):
    ref: str
    frequency_hz: float
    tolerance_hz: int = 100_000

class FunctionalTest(BaseModel):
    name: str
    command: Optional[str] = None
    expected: Optional[str] = None

class ParsedEntities(BaseModel):
    title: str = "Untitled Board"
    rails: List[PowerRail] = Field(default_factory=list)
    oscillators: List[Oscillator] = Field(default_factory=list)
    functional_tests: List[FunctionalTest] = Field(default_factory=list)

class TestStep(BaseModel):
    id: str
    section: str
    description: str
    equipment: Optional[str] = None
    expected: Optional[str] = None

class TestPlan(BaseModel):
    title: str
    steps: List[TestStep]
    notes: Optional[str] = None

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", ""]
        current = None
        for s in self.steps:
            if s.section != current:
                lines.append(f"## {s.section}")
                current = s.section
            lines.append(f"**{s.id}. {s.description}**")
            if s.equipment:
                lines.append(f"- Equipment: {s.equipment}")
            if s.expected:
                lines.append(f"- Expected: {s.expected}")
            lines.append("")
        if self.notes:
            lines += ["---", "### Notes", self.notes]
        return "\n".join(lines)
