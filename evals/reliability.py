"""Route evaluation defects without turning missing evidence into behavior failures."""

from __future__ import annotations

from typing import Literal

from evals.assessment_models import AssessmentResult
from evals.evidence import EvidenceRun
from evals.recording import EvaluationIssue


def reconcile(
    run: EvidenceRun,
    result: AssessmentResult,
    *,
    check_recording: bool = True,
    reviewed_recording: bool = False,
) -> None:
    """Preserve direct failures and route unsupported verdicts to investigation."""
    frames = [f for f in run.frames if f.event == "message"]
    for frame in run.frames if check_recording and not reviewed_recording else []:
        for problem in frame.recording.problems:
            result.issues.append(
                EvaluationIssue(
                    "capture",
                    f"Step {frame.step}: {problem}",
                    "Repair capture and rerun; retained evidence may "
                    "establish unaffected criteria.",
                )
            )
    for criterion in result.criteria:
        reason = criterion.get("reason")
        channel = str(criterion.get("channel", "actions"))
        complete = bool(frames) and all(
            f.completed
            and f.recording.actions == "complete"
            and (
                channel == "actions" or f.recording.channels.get(channel) == "complete"
            )
            for f in frames
        )
        if (
            check_recording
            and reason == "omitted_action"
            and criterion["verdict"] == "not_met"
            and not complete
        ):
            criterion["original_verdict"] = "not_met"
            criterion["original_reason"] = reason
            criterion["verdict"] = "uncertain"
            criterion["reason"] = reason = "missing_evidence"
        if criterion["verdict"] != "uncertain":
            continue
        identifier = str(criterion["criterion"])
        kind: Literal["capture", "criterion", "assessment"]
        if reason == "missing_evidence":
            kind, action = (
                "capture",
                "Check recording coverage; repair missing capture and "
                "rerun if observations are unavailable.",
            )
        elif reason == "ambiguous_requirement":
            kind, action = (
                "criterion",
                "Compare the criterion with accepted intent; clarify it "
                "and start a fresh comparison if expectations change.",
            )
        else:
            kind, action = (
                "assessment",
                "Investigate the cited evidence and judgment with "
                "calibration; do not resolve disagreement by vote.",
            )
        result.issues.append(
            EvaluationIssue(kind, str(criterion["evidence"]), action, identifier)
        )
    # Only required criteria determine behavior; callers mark that property explicitly.
    required = [c for c in result.criteria if c.get("required", True)]
    required_ids = {str(c["criterion"]) for c in required}
    blocking_issues = any(
        i.criterion is None or i.criterion in required_ids for i in result.issues
    )
    if result.status not in {"error", "limit"}:
        result.status = (
            "fail"
            if any(c["verdict"] == "not_met" for c in required)
            else "inconclusive"
            if blocking_issues or any(c["verdict"] == "uncertain" for c in required)
            else "pass"
        )
