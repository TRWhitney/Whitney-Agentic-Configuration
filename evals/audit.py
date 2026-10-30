"""Report corpus structure without declaring task quality from counts."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass
from statistics import median

from evals.models import CaseSpec, EditStep, MessageStep, SeedStep


@dataclass
class CaseAudit:
    id: str
    purpose: str
    message_count: int
    seed_steps: int
    fixture_characters: int
    visible_grading_scripts: list[str]
    process_cues: list[dict[str, str]]


# These are review cues, not verdicts. Cancellation, authorization, and method controls
# can contain process language. The tested behavior determines whether it coaches.
REQUEST_CUE = re.compile(
    r"(?i)\b(?:audit|review|verify|delegate|amend)\b|"
    r"\b(?:check|inspect|run|execute)\b.{0,80}"
    r"\b(?:checks?|tests?|suite|prototype|probe|implementation)\b|\buse wayfinding\b"
)
RECORD_CUE = re.compile(
    r"(?im)(?:^|[.!?]\s+)(?:[-*]\s+)?"
    r"(?:run|rerun|execute|invoke|verify|delegate|amend)\b|"
    r"\buse\s+(?:python3?|uv|checks/|tests/)"
)


def process_cues(case: CaseSpec) -> list[dict[str, str]]:
    sources: list[tuple[str, str, re.Pattern[str]]] = []
    for index, step in enumerate(case.steps):
        if isinstance(step, MessageStep):
            sources.append((f"message:{index}", step.prompt, REQUEST_CUE))
        if isinstance(step, EditStep):
            sources.extend(
                (f"edit:{index}:{p}", text, RECORD_CUE)
                for p, text in step.files.items()
            )
            sources.extend(
                (f"temporary-edit:{index}:{p}", text, RECORD_CUE)
                for p, text in step.temporary_files.items()
            )
    sources.extend(("file:" + p, text, RECORD_CUE) for p, text in case.files.items())
    sources.extend(
        ("uncommitted:" + p, text, RECORD_CUE)
        for p, text in case.uncommitted_files.items()
    )
    sources.extend(
        ("temporary:" + p, text, RECORD_CUE) for p, text in case.temporary_files.items()
    )
    return [
        {
            "source": source,
            "cue": match.group(0),
            "excerpt": text[max(0, match.start() - 80) : match.end() + 160],
        }
        for source, text, pattern in sources
        for match in pattern.finditer(text)
    ]


def case_audit(case: CaseSpec) -> CaseAudit:
    files = {**case.files, **case.uncommitted_files}
    return CaseAudit(
        case.id,
        case.purpose,
        sum(isinstance(step, MessageStep) for step in case.steps),
        sum(isinstance(step, SeedStep) for step in case.steps),
        sum(len(text) for text in files.values()),
        sorted(
            {
                check.path
                for step in case.steps
                for check in step.checks
                if check.kind == "python_check" and check.path in files
            }
        ),
        process_cues(case),
    )


def audit(cases: list[CaseSpec]) -> dict[str, object]:
    summaries = [case_audit(case) for case in cases]
    sizes = sorted(summary.fixture_characters for summary in summaries)
    checks = Counter(check.kind for c in cases for s in c.steps for check in s.checks)
    return {
        "cases": len(cases),
        "case_details": [asdict(summary) for summary in summaries],
        "purposes": dict(Counter(s.purpose for s in summaries)),
        "message_counts": dict(Counter(s.message_count for s in summaries)),
        "seeded_navigation": sum(s.seed_steps > 0 for s in summaries),
        "public_python_graders": sum(
            bool(s.visible_grading_scripts) for s in summaries
        ),
        "fixture_characters": {
            "min": sizes[0],
            "median": median(sizes),
            "max": sizes[-1],
        },
        "cases_with_process_cues": sum(bool(s.process_cues) for s in summaries),
        "rubric_cases": sum(bool(c.rubric) for c in cases),
        "checks": dict(checks),
    }
