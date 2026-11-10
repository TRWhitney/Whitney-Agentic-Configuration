"""Validated judge responses and concise assessment results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from pydantic import Field, model_validator

from evals.models import Definition, Identifier, NonemptyText
from evals.recording import EvaluationIssue

Outcome = Literal["pass", "fail", "inconclusive", "error", "limit"]

Verdict = Literal["met", "not_met", "uncertain"]


class CriterionAssessment(Definition):
    verdict: Verdict
    reason: (
        Literal[
            "observed",
            "omitted_action",
            "missing_evidence",
            "ambiguous_requirement",
            "conflicting_evidence",
        ]
        | None
    ) = None
    channel: Literal[
        "actions", "commands", "browser", "images", "children", "artifacts"
    ] = "actions"
    evidence: list[NonemptyText] = Field(min_length=1)

    @model_validator(mode="after")
    def consistent_reason(self) -> CriterionAssessment:
        if (
            self.reason
            in {"missing_evidence", "ambiguous_requirement", "conflicting_evidence"}
            and self.verdict != "uncertain"
        ):
            raise ValueError(
                "An unresolved evaluation problem requires an uncertain verdict."
            )
        if self.reason == "omitted_action" and self.verdict != "not_met":
            raise ValueError("An omitted required action requires a not_met verdict.")
        if self.reason == "observed" and self.verdict == "uncertain":
            raise ValueError("An uncertain verdict requires its unresolved cause.")
        return self


class CriterionJudgment(CriterionAssessment):
    criterion: Identifier


class CandidateJudgment(Definition):
    label: Identifier
    criteria: list[CriterionJudgment] = Field(min_length=1)


class JudgeResponse(Definition):
    candidates: list[CandidateJudgment] = Field(min_length=1)


@dataclass
class AssessmentResult:
    status: Outcome
    model: str
    criteria: list[dict[str, object]] = field(default_factory=list)
    detail: str = ""
    tokens: int | None = None
    metrics: dict[str, float | int] = field(default_factory=dict)
    issues: list[EvaluationIssue] = field(default_factory=list)
