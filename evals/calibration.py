"""Load labeled examples without exposing their labels to the assessor."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field, JsonValue, model_validator

from evals.assessment_models import Verdict
from evals.evidence import EvidenceFrame, EvidenceRun
from evals.models import (
    Definition,
    Identifier,
    NonemptyText,
    RelativePath,
    RubricCriterion,
)
from evals.recording import Recording


class Example(Definition):
    id: Identifier
    request: NonemptyText
    files: dict[RelativePath, str]
    artifact_path: RelativePath | None = None
    artifact: NonemptyText | None = None
    commands: list[dict[str, JsonValue]] = Field(default_factory=list)
    recording: Recording = Field(default_factory=Recording)
    completed: bool = True

    @model_validator(mode="after")
    def paired_artifact(self) -> Example:
        if (self.artifact_path is None) != (self.artifact is None):
            raise ValueError("Artifact path and contents must be supplied together.")
        return self

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
                {
                    **example.files,
                    **(
                        {example.artifact_path: example.artifact}
                        if example.artifact_path is not None
                        and example.artifact is not None
                        else {}
                    ),
                },
                [dict(command) for command in example.commands],
                None,
                {},
                completed=example.completed,
                recording=example.recording,
            )
        )
        runs.append(run)
        expected[example.id] = example.expected
    return calibration.rubric, runs, expected
