from __future__ import annotations
from core.models import ParsedEntities

SYSTEM_PROMPT = (
    "You are a hardware test engineer. Convert parsed board info into a step-by-step bring-up/test "
    "procedure. Include setup, equipment, expected values (with tolerances), and clear pass/fail criteria."
)


def build_user_prompt(entities: ParsedEntities) -> str:
    lines = [
        "Parsed Entities:",
        f"- title: {entities.title}",
        "- rails:",
    ]
    for r in entities.rails:
        lines.append(f"  - {r.name}: {r.voltage} V ±{r.tolerance_mv} mV")
    lines.append("- oscillators:")
    for o in entities.oscillators:
        lines.append(f"  - {o.ref}: {o.frequency_hz} Hz ±{o.tolerance_hz} Hz")
    lines.append("- functional_tests:")
    for t in entities.functional_tests:
        lines.append(f"  - {t.name}: cmd={t.command}")

    lines.append(
        "\nOutput a Markdown document with sections: Setup, Visual Inspection, Voltage Rail Checks, "
        "Oscillator Checks, Firmware Programming, Functional Tests, and short Notes."
    )
    return "\n".join(lines)
