"""Load labeled examples without exposing their labels to the assessor."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field

from evals.assessment_models import Verdict
from evals.evidence import EvidenceFrame, EvidenceRun
from evals.models import (
    Definition,
    Identifier,
    NonemptyText,
    RelativePath,
    RubricCriterion,
)


class Example(Definition):
    id: Identifier
    request: NonemptyText
    files: dict[RelativePath, str]
    artifact_path: RelativePath
    artifact: NonemptyText
    reply: str = ""
    expected: Verdict
    reason: NonemptyText


class Calibration(Definition):
    rubric: list[RubricCriterion] = Field(min_length=1, max_length=1)
    examples: list[Example] = Field(min_length=1)


def load_calibration(
    path: Path,
) -> tuple[list[RubricCriterion], list[EvidenceRun], dict[str, Verdict]]:
    calibration = Calibration.model_validate_json(path.read_text(encoding="utf-8"))
    if len({e.id for e in calibration.examples}) != len(calibration.examples):
        raise ValueError("Calibration example IDs must be unique.")
    runs = []
    expected = {}
    for example in calibration.examples:
        run = EvidenceRun(example.id, "authored", "calibration", dict(example.files))
        run.frames.append(
            EvidenceFrame(
                0,
                "conversation-1",
                example.request,
                example.reply,
                {**example.files, example.artifact_path: example.artifact},
                [],
                None,
                {},
            )
        )
        runs.append(run)
        expected[example.id] = example.expected
    return calibration.rubric, runs, expected
