"""Recording coverage, independent of candidate completion and behavior."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Recording:
    # Complete covers supported native action events, not hidden reasoning or all tools.
    actions: Literal["complete", "partial", "unknown"] = "unknown"
    problems: list[str] = field(default_factory=list)
    channels: dict[str, Literal["complete", "partial", "unknown"]] = field(
        default_factory=dict
    )


@dataclass
class EvaluationIssue:
    kind: Literal["capture", "criterion", "assessment"]
    detail: str
    next_action: str
    criterion: str | None = None
