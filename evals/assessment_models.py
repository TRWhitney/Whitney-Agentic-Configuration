"""Validated judge responses and concise assessment results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from pydantic import Field

from evals.models import Definition, Identifier, NonemptyText

Outcome = Literal["pass", "fail", "inconclusive", "error", "limit"]

Verdict = Literal["met", "not_met", "uncertain"]


class CriterionAssessment(Definition):
    verdict: Verdict
    evidence: list[NonemptyText] = Field(min_length=1)


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
