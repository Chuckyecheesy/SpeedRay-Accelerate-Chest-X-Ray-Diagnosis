"""Prompts for SpeedRay backend."""

REPORT_PROMPT = """Generate a very short report that discusses ONLY the single finding named below.
Rules: Do NOT list other body systems (e.g. lungs, pleura, mediastinum, cardiovascular). Do NOT say "no other findings" or "no other abnormalities." Do NOT add a second impression item. Only describe the one detected finding (e.g. if it is Pneumonia, talk only about pneumonia).
Output format:
1) Summary: one sentence about the detected finding only.
2) Findings: one short paragraph describing only that finding (location, appearance). Nothing else.
3) Impression: one line with the single diagnosis only (e.g. "Pneumonia" or "Right lower lobe pneumonia.")."""


def get_report_prompt() -> str:
    return REPORT_PROMPT
