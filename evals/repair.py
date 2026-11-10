"""Investigate or reassess saved eval evidence, preserving earlier judgments."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from pydantic import TypeAdapter

from evals.assessment import assess, validate_judgment
from evals.assessment_models import AssessmentResult
from evals.evidence import EvidenceRun
from evals.models import CaseSpec, RubricCriterion, load_cases
from evals.output_paths import external_output
from evals.recording import EvaluationIssue
from evals.runner import DriverFactory

ROOT = Path(__file__).resolve().parents[1]


def external_new(path: Path, source: Path) -> Path:
    path = external_output(path)
    if path.is_relative_to(ROOT) or path.is_relative_to(source):
        raise ValueError(
            "Repair outputs must be outside the checkout and source evidence."
        )
    if path.exists():
        raise ValueError("Repair output already exists; preserve earlier judgments.")
    return path


def main(
    arguments: Sequence[str] | None = None,
    *,
    driver_factory: DriverFactory | None = None,
    quiet: bool = False,
) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("diagnose", "reassess"))
    parser.add_argument(
        "--evidence",
        type=Path,
        required=True,
        help="Existing per-case review directory.",
    )
    parser.add_argument("--model", required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--review-dir", type=Path, required=True)
    parser.add_argument("--cases", type=Path, default=ROOT / "evals/cases")
    parser.add_argument("--timeout", type=int, default=1200)
    parser.add_argument("--max-tokens", type=int, default=0)
    args = parser.parse_args(arguments)
    try:
        source = args.evidence.expanduser().resolve()
        if source.is_relative_to(ROOT):
            raise ValueError("Review evidence must be outside the checkout.")
        report = external_new(args.report, source)
        review = external_new(args.review_dir, source)
        if report.is_relative_to(review) or review.is_relative_to(report):
            raise ValueError("Report and review paths must be separate.")
        manifest = json.loads((source / "inputs/manifest.json").read_text())
        rubric = TypeAdapter(list[RubricCriterion]).validate_python(
            manifest["criteria"]
        )
        runs = TypeAdapter(list[EvidenceRun]).validate_json(
            (source / "evidence.json").read_text()
        )
        labels = json.loads((source / "labels.json").read_text())
        scored_results = (
            TypeAdapter(dict[str, AssessmentResult]).validate_json(
                (source / "assessment-results.json").read_text()
            )
            if (source / "assessment-results.json").exists()
            else {}
        )
        original_results = {
            index: asdict(result) for index, result in scored_results.items()
        }
        failed_assessment = any(
            result.status in {"error", "limit", "inconclusive"}
            for result in scored_results.values()
        )
        original_error = ""
        try:
            response = validate_judgment(
                (source / "response.txt").read_text(), set(labels), rubric
            )
            original = {
                labels[c.label]["index"]: [
                    d.model_dump(mode="json") for d in c.criteria
                ]
                for c in response.candidates
            }
        except (OSError, ValueError) as error:
            original_error = str(error)
            original = {i: [] for i in range(len(runs))}
        required_ids = {criterion.id for criterion in rubric if criterion.required}
        uncertain_required = any(
            c["criterion"] in required_ids and c["verdict"] == "uncertain"
            for criteria in original.values()
            for c in criteria
        )
        if set(original) != set(range(len(runs))):
            raise ValueError("Original judgments do not match saved runs.")
        recording_review: dict[str, object] | None = None
        reviewed_recording = False
        if args.operation == "reassess":
            cases = {c.id: c for c in load_cases(args.cases)}
            for run in runs:
                current = cases.get(run.case)
                if (
                    current is None
                    or current.rubric != rubric
                    or not run.definition
                    or CaseSpec.model_validate(run.definition) != current
                ):
                    raise ValueError(
                        "Case changed or its original definition is "
                        "unavailable; run a fresh comparison."
                    )
                if any(not f.completed for f in run.frames):
                    raise ValueError(
                        "Recording is incomplete; repair capture and run "
                        "a fresh comparison."
                    )
            if (
                original_error
                or failed_assessment
                or uncertain_required
                or any(f.recording.problems for run in runs for f in run.frames)
            ):
                audit_report = review.with_name(review.name + "-recording-review.json")
                audit_dir = review.with_name(review.name + "-recording-review")
                audit_code = main(
                    [
                        "diagnose",
                        "--evidence",
                        str(source),
                        "--model",
                        args.model,
                        "--report",
                        str(audit_report),
                        "--review-dir",
                        str(audit_dir),
                        "--timeout",
                        str(args.timeout),
                        "--max-tokens",
                        str(args.max_tokens),
                    ],
                    driver_factory=driver_factory,
                    quiet=True,
                )
                if not audit_report.exists():
                    raise ValueError(
                        "Recording review failed before producing evidence."
                    )
                audit = json.loads(audit_report.read_text())
                recording_review = {
                    "report": str(audit_report),
                    "exit_code": audit_code,
                    "findings": [
                        {
                            "index": row["index"],
                            "findings": row["findings"],
                            "issues": row["assessment"]["issues"],
                        }
                        for row in audit["results"]
                    ],
                }
                sufficient = {
                    row["index"]
                    for row in audit["results"]
                    if row["assessment"]["status"] not in {"error", "limit"}
                    and all(
                        any(
                            c["criterion"] == needed and c["verdict"] == "met"
                            for c in row["assessment"]["criteria"]
                        )
                        for needed in ("recording", "expectations")
                    )
                }
                if sufficient != set(range(len(runs))):
                    summary = {
                        "operation": "reassess",
                        "recording_review": recording_review,
                        "detail": "Review found unresolved expectations or missing "
                        "observations. Resolve the identified cause "
                        "before reassessment.",
                        "results": [],
                    }
                    report.parent.mkdir(parents=True, exist_ok=True)
                    with report.open("x") as stream:
                        json.dump(summary, stream, indent=2)
                    if not quiet:
                        print(json.dumps(summary, indent=2))
                    return 2 if audit_code == 2 else 1
                reviewed_recording = True
        else:
            for i, run in enumerate(runs):
                additions = {
                    **{
                        "__eval_review__/original-framework/" + name: text
                        for name, text in run.framework.items()
                    },
                    **{
                        "__eval_review__/current-framework/"
                        + path.name: path.read_text()
                        for path in Path(__file__).parent.iterdir()
                        if path.suffix in {".py", ".cjs"}
                    },
                    "__eval_review__/criteria.json": json.dumps(manifest["criteria"]),
                    "__eval_review__/judgment.json": json.dumps(
                        {"criteria": original[i], "error": original_error}
                    ),
                    "__eval_review__/assessment-results.json": json.dumps(
                        {
                            index: {
                                key: value
                                for key, value in result.items()
                                if key != "model"
                            }
                            for index, result in original_results.items()
                        }
                    ),
                    "__eval_review__/assessment.json": (
                        source / "judge-observation.json"
                    ).read_text()
                    if (source / "judge-observation.json").exists()
                    else "{}",
                    "__eval_review__/checks.json": json.dumps(
                        {"checks": run.checks, "execution": run.execution}
                    ),
                    "__eval_review__/definition.json": json.dumps(
                        {
                            k: v
                            for k, v in run.definition.items()
                            if k not in {"id", "tags"}
                        }
                    ),
                }
                if any(
                    set(additions) & set(files)
                    for files in [run.initial_files, *[f.files for f in run.frames]]
                ):
                    raise ValueError(
                        "Review artifact path collides with candidate work."
                    )
                run.initial_files.update(additions)
                for frame in run.frames:
                    frame.files.update(additions)
            rubric = [
                RubricCriterion(
                    id="expectations",
                    description=(
                        "The required original criteria follow the supplied task "
                        "and accepted "
                        "instructions, allow equivalent valid work, and "
                        "impose no invented"
                        " behavior. Cite a concrete contradiction for not_met; unclear "
                        "intent is uncertain. Do not invent new user requirements."
                    ),
                ),
                RubricCriterion(
                    id="recording",
                    description=(
                        "Read the original and current framework capture code "
                        "when available. "
                        "The supplied observations are sufficient to assess"
                        " each required original "
                        "requirement. Check action and channel coverage, "
                        "interruptions, "
                        "browser receipts, missing images and child "
                        "findings. A missing "
                        "observation is not an omitted action unless its "
                        "relevant record "
                        "is complete. Cite the affected original criterion and missing "
                        "source when not_met."
                    ),
                ),
                RubricCriterion(
                    id="capture-classification",
                    description=(
                        "The collection warnings and their effect on behavior "
                        "classification "
                        "are supported by the actual records "
                        "and the required criteria. "
                        "Distinguish unavailable observations "
                        "from unsupported warnings or "
                        "unrelated gaps. Cite the exact warning, records "
                        "and framework rule "
                        "when not_met. No warnings satisfies this criterion; an "
                        "unobservable cause remains uncertain."
                    ),
                ),
                RubricCriterion(
                    id="judgment",
                    description=(
                        "The original verdicts in "
                        "__eval_review__/judgment.json follow the"
                        " original criteria and evidence. Accept equivalent valid "
                        "representations. Cite the original criterion and "
                        "actual action or"
                        " artifact when a judgment is unsupported. Distinguish a real "
                        "candidate failure from recording defects, "
                        "ambiguous expectations "
                        "and assessor error. Do not resolve disagreement by vote."
                    ),
                ),
            ]
        results = assess(
            rubric,
            runs,
            args.model,
            timeout=args.timeout,
            max_tokens=args.max_tokens,
            driver_factory=driver_factory,
            review_dir=review,
            subject="evaluation" if args.operation == "diagnose" else "candidate",
            reviewed_recording=reviewed_recording,
        )
        output = []
        for i, result in results.items():
            changes = []
            findings = []
            if args.operation == "diagnose":
                for criterion in result.criteria:
                    if criterion["verdict"] == "met":
                        continue
                    target = str(criterion["criterion"])
                    actions = {
                        "expectations": (
                            "criterion",
                            "Check accepted intent and fixtures; clarify "
                            "expectations and start a fresh comparison if "
                            "they change.",
                        ),
                        "recording": (
                            "capture",
                            "Repair the identified observation source, prove "
                            "it with a regression, and rerun when evidence is"
                            " unavailable.",
                        ),
                        "capture-classification": (
                            "capture",
                            "Correct unsupported recording classification, "
                            "retain a regression, and reassess when "
                            "the underlying observations survive.",
                        ),
                        "judgment": (
                            "assessment",
                            "Add valid and invalid calibration examples, "
                            "repair the assessor or grader, and reassess "
                            "surviving evidence.",
                        ),
                    }
                    kind, next_action = actions[target]
                    findings.append(
                        {
                            "kind": kind,
                            "criterion": target,
                            "confirmed": criterion["verdict"] == "not_met",
                            "evidence": criterion["evidence"],
                            "next_action": next_action,
                        }
                    )
            if args.operation == "reassess":
                previous = {str(c["criterion"]): c["verdict"] for c in original[i]}
                for criterion in result.criteria:
                    if (
                        previous.get(str(criterion["criterion"]))
                        != criterion["verdict"]
                    ):
                        changes.append(
                            {
                                "criterion": criterion["criterion"],
                                "previous": previous.get(str(criterion["criterion"])),
                                "current": criterion["verdict"],
                            }
                        )
                if changes and previous:
                    result.issues.append(
                        EvaluationIssue(
                            "assessment",
                            "Reassessment differs from the original judgment.",
                            "Inspect the original and revised citations; "
                            "retain both judgments.",
                        )
                    )
            output.append(
                {
                    "case": runs[i].case,
                    "index": i,
                    "original_criteria": original[i],
                    "original_assessment_error": original_error,
                    "original_assessment": original_results.get(str(i)),
                    "original_checks": runs[i].checks,
                    "original_execution": runs[i].execution,
                    "behavior": (
                        "incorrect"
                        if any(c.get("passed") is False for c in runs[i].checks)
                        or result.status == "fail"
                        else "unknown"
                        if result.status != "pass"
                        or runs[i].execution.get("status", "pass") != "pass"
                        else "correct"
                    )
                    if args.operation == "reassess"
                    else "not_reassessed",
                    "assessment": asdict(result),
                    "changes": changes,
                    "findings": findings,
                }
            )
        report.parent.mkdir(parents=True, exist_ok=True)
        with report.open("x") as stream:
            json.dump(
                {
                    "operation": args.operation,
                    "recording_review": recording_review,
                    "results": output,
                },
                stream,
                indent=2,
            )
        if not quiet:
            print(
                json.dumps(
                    {
                        "operation": args.operation,
                        "recording_review": recording_review,
                        "report": str(report),
                        "results": output,
                    },
                    indent=2,
                )
            )
        if len(results) != len(runs) or any(
            r.status in {"error", "limit"} for r in results.values()
        ):
            return 2
        if args.operation == "reassess" and any(
            run.execution.get("status") in {"error", "limit"} for run in runs
        ):
            return 2
        return (
            1
            if any(r.status != "pass" or r.issues for r in results.values())
            or any(o["behavior"] in {"incorrect", "unknown"} for o in output)
            else 0
        )
    except (OSError, ValueError, KeyError) as error:
        print(f"Cannot {args.operation}: {error}", file=sys.stderr)
        return 2


def diagnose_saved(
    source: Path,
    model: str,
    *,
    timeout: int,
    max_tokens: int,
    driver_factory: DriverFactory | None = None,
) -> dict[str, object]:
    report = source.with_name(source.name + "-diagnosis.json")
    review = source.with_name(source.name + "-diagnosis")
    code = main(
        [
            "diagnose",
            "--evidence",
            str(source),
            "--model",
            model,
            "--report",
            str(report),
            "--review-dir",
            str(review),
            "--timeout",
            str(timeout),
            "--max-tokens",
            str(max_tokens),
        ],
        driver_factory=driver_factory,
        quiet=True,
    )
    return {"source": str(source), "report": str(report), "exit_code": code}


if __name__ == "__main__":
    raise SystemExit(main())
