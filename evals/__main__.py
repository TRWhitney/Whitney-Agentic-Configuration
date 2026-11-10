"""Validate, select, and run the agent case corpus."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from evals.assessment import apply_assessment, assess
from evals.audit import audit
from evals.evidence import EvidenceRun
from evals.models import CaseSpec, load_cases, select_cases
from evals.output_paths import external_output
from evals.runner import CaseResult, DriverFactory, run_case

ROOT = Path(__file__).resolve().parents[1]


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("Must be positive.")
    return parsed


def nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("Must be nonnegative.")
    return parsed


def package_version(name: str) -> str | None:
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def main(
    arguments: Sequence[str] | None = None,
    *,
    driver_factory: DriverFactory | None = None,
    judge_factory: DriverFactory | None = None,
) -> int:
    parser = argparse.ArgumentParser(description="Run agent workflow cases.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "list", "run", "schema", "audit"):
        command = commands.add_parser(name)
        if name != "schema":
            command.add_argument(
                "--cases", type=Path, default=Path(__file__).parent / "cases"
            )
        if name in ("list", "run", "audit"):
            command.add_argument("--case", action="append", default=[])
            command.add_argument("--tag", action="append", default=[])
            command.add_argument("--integration", action="store_true")
            command.add_argument(
                "--purpose",
                action="append",
                default=[],
                choices=("focused", "task", "control"),
            )
        if name == "run":
            command.add_argument("--model", required=True)
            command.add_argument("--repeat", type=positive_int, default=1)
            command.add_argument(
                "--variant", action="append", default=[], metavar="NAME=SOURCE"
            )
            command.add_argument("--timeout", type=positive_int, default=600)
            command.add_argument("--max-tokens", type=nonnegative_int, default=0)
            command.add_argument("--report", type=Path)
            command.add_argument("--judge-model")
            command.add_argument(
                "--calibration", type=Path, action="append", default=[]
            )
            command.add_argument("--judge-timeout", type=positive_int, default=600)
            command.add_argument("--judge-max-tokens", type=nonnegative_int, default=0)
            command.add_argument("--review-dir", type=Path)
            command.add_argument("--diagnose", action="store_true")
    args = parser.parse_args(arguments)
    try:
        if args.command == "schema":
            print(json.dumps(CaseSpec.model_json_schema(), indent=2))
            return 0
        cases = load_cases(args.cases)
        if args.command == "validate":
            print(f"{len(cases)} cases valid.")
            return 0
        cases = select_cases(
            cases,
            ids=set(args.case),
            tags=set(args.tag),
            integration=args.integration,
            purposes=set(args.purpose),
        )
        if args.command == "audit":
            print(json.dumps(audit(cases), indent=2))
            return 0
        if args.command == "list":
            for case in cases:
                category = "integration" if case.integration else "routine"
                print(f"{case.id}\t{category}\t{case.purpose}\t{','.join(case.tags)}")
            return 0
        variants: dict[str, Path] = {}
        for definition in args.variant:
            label, separator, location = definition.partition("=")
            if not separator or not label or label in variants:
                raise ValueError("Variants must have unique names and use NAME=SOURCE.")
            source = Path(location).expanduser().resolve()
            if (
                not (source / "skills").is_dir()
                or not (source / "config/global-agents.md").is_file()
            ):
                raise ValueError(f"Not an instruction source: {source}")
            variants[label] = source
        if not variants:
            variants["current"] = ROOT
        report = external_output(args.report) if args.report else None
        if report is not None:
            if any(
                report.is_relative_to(source) for source in (ROOT, *variants.values())
            ):
                raise ValueError(
                    "Reports must be outside instruction source checkouts."
                )
            if report.exists():
                raise ValueError("Report already exists; choose a new file.")
        if driver_factory is None and package_version("openai-codex") is None:
            raise ValueError(
                "Install evaluation dependencies with uv sync --group eval."
            )
        for case in cases:
            if args.judge_model and not case.rubric:
                raise ValueError(f"{case.id} has no assessment rubric.")
        review = external_output(args.review_dir) if args.review_dir else None
        if review is not None:
            if any(review.is_relative_to(p) for p in (ROOT, *variants.values())):
                raise ValueError("Review evidence must be outside source checkouts.")
            if review.exists():
                raise ValueError("Review directory already exists.")
            if not args.judge_model:
                raise ValueError("Review evidence requires --judge-model.")
            review.mkdir(parents=True)
        if args.diagnose and (review is None or not args.judge_model):
            raise ValueError("--diagnose requires --review-dir and --judge-model.")
        diagnoses = []
        from evals.repair import diagnose_saved

        calibration_results = []
        for number, path in enumerate(args.calibration):
            if not args.judge_model:
                raise ValueError("Calibration requires --judge-model.")
            from evals.calibrate import evaluate

            code, calibration = evaluate(
                path,
                args.judge_model,
                timeout=args.judge_timeout,
                max_tokens=args.judge_max_tokens,
                driver_factory=judge_factory,
                review=review / f"calibration-{number + 1}" if review else None,
            )
            calibration_results.append(calibration)
            if code:
                if args.diagnose and review is not None:
                    diagnoses.append(
                        diagnose_saved(
                            review / f"calibration-{number + 1}",
                            args.judge_model,
                            timeout=args.judge_timeout,
                            max_tokens=args.judge_max_tokens,
                            driver_factory=judge_factory,
                        )
                    )
                output = json.dumps(
                    {
                        "evaluation_status": "needs_investigation",
                        "calibrations": calibration_results,
                        "diagnoses": diagnoses,
                        "results": [],
                    },
                    indent=2,
                )
                if report:
                    report.parent.mkdir(parents=True, exist_ok=True)
                    with report.open("x") as stream:
                        stream.write(output + "\n")
                print(output)
                return code
        framework = {
            path.name: path.read_text()
            for path in Path(__file__).parent.iterdir()
            if path.suffix in {".py", ".cjs"}
        }
        executions: list[CaseResult] = []
        evidence: dict[str, list[tuple[int, EvidenceRun]]] = {}
        metadata: list[dict[str, object]] = []
        for label, source in variants.items():
            for attempt in range(1, args.repeat + 1):
                for case in cases:
                    print(f"{label}: {case.id}, attempt {attempt}", file=sys.stderr)
                    run = EvidenceRun(
                        case.id,
                        args.model,
                        label,
                        definition=case.model_dump(mode="json"),
                    )
                    run.framework = dict(framework)
                    result = run_case(
                        case,
                        source,
                        args.model,
                        timeout=args.timeout,
                        max_tokens=args.max_tokens,
                        driver_factory=driver_factory,
                        on_observation=run.observe if args.judge_model else None,
                    )
                    run.isolation_status = result.isolation_status
                    run.checks = [asdict(check) for check in result.checks]
                    run.execution = {
                        "status": result.mechanical_status,
                        "detail": result.detail,
                    }
                    index = len(executions)
                    executions.append(result)
                    metadata.append({"variant": label, "attempt": attempt})
                    if args.judge_model:
                        evidence.setdefault(case.id, []).append((index, run))
        if args.judge_model:
            for case in cases:
                paired = evidence[case.id]
                judgments = assess(
                    case.rubric,
                    [run for _, run in paired],
                    args.judge_model,
                    timeout=args.judge_timeout,
                    max_tokens=args.judge_max_tokens,
                    driver_factory=judge_factory,
                    review_dir=review / case.id if review is not None else None,
                )
                for local_index, judgment in judgments.items():
                    apply_assessment(executions[paired[local_index][0]], judgment)
                if (
                    args.diagnose
                    and review is not None
                    and any(
                        j.issues or j.status in {"error", "limit"}
                        for j in judgments.values()
                    )
                ):
                    diagnoses.append(
                        diagnose_saved(
                            review / case.id,
                            args.judge_model,
                            timeout=args.judge_timeout,
                            max_tokens=args.judge_max_tokens,
                            driver_factory=judge_factory,
                        )
                    )
        results = [
            {
                **asdict(result),
                "behavior": result.behavior,
                "assessment_execution": result.assessment_execution,
                "evaluation_status": (
                    "needs_investigation"
                    if result.assessment
                    and (
                        result.assessment.issues
                        or result.assessment.status in {"error", "limit"}
                    )
                    else "not_assessed"
                    if result.assessment is None
                    else "no_problem_detected"
                ),
                **meta,
            }
            for result, meta in zip(executions, metadata, strict=True)
        ]
        for result, meta in zip(executions, metadata, strict=True):
            judge_status = (
                result.assessment.status if result.assessment else "not requested"
            )
            print(
                f"{result.case}, attempt {meta['attempt']}, {meta['variant']}: "
                f"behavior {result.behavior}; "
                f"assessment {result.assessment_execution} "
                f"({judge_status})",
                file=sys.stderr,
            )
            for check in result.checks:
                if not check.passed:
                    print(
                        f"  Failed {check.kind}, step {check.step}: {check.detail}",
                        file=sys.stderr,
                    )
            if result.assessment is not None:
                for criterion in result.assessment.criteria:
                    if criterion["verdict"] != "met":
                        print(
                            f"  {criterion['criterion']}: {criterion['verdict']}. "
                            + str(criterion["evidence"]),
                            file=sys.stderr,
                        )
                for issue in result.assessment.issues:
                    print(
                        f"  Eval {issue.kind}: {issue.detail} "
                        f"Next: {issue.next_action}",
                        file=sys.stderr,
                    )
            if result.detail:
                print("  " + result.detail, file=sys.stderr)
        groups: dict[tuple[str, str, str], Counter[str]] = {}
        for result, meta in zip(executions, metadata, strict=True):
            key = (
                result.case,
                result.purpose,
                str(meta["variant"]),
            )
            groups.setdefault(key, Counter())[result.status] += 1
        counts = Counter(str(item["status"]) for item in results)
        output = json.dumps(
            {
                "calibrations": calibration_results,
                "diagnoses": diagnoses,
                "sdk": package_version("openai-codex"),
                "bundled_runtime": package_version("openai-codex-cli-bin"),
                "assessment": "blinded-model" if args.judge_model else "code-checks",
                "behavior_counts": dict(Counter(r.behavior for r in executions)),
                "assessment_execution_counts": dict(
                    Counter(r.assessment_execution for r in executions)
                ),
                "assessment_counts": dict(
                    Counter(
                        result.assessment.status
                        for result in executions
                        if result.assessment is not None
                    )
                ),
                "groups": [
                    {
                        "case": key[0],
                        "purpose": key[1],
                        "variant": key[2],
                        "counts": dict(counts),
                    }
                    for key, counts in groups.items()
                ],
                "counts": {
                    name: counts[name]
                    for name in ("pass", "fail", "error", "limit", "inconclusive")
                },
                "results": results,
            },
            indent=2,
        )
        if report is not None:
            report.parent.mkdir(parents=True, exist_ok=True)
            with report.open("x", encoding="utf-8") as stream:
                stream.write(output + "\n")
        print(output)
        return (
            2
            if counts["error"]
            else 3
            if counts["limit"]
            else 1
            if counts["fail"]
            else 4
            if counts["inconclusive"]
            else 0
        )
    except (OSError, ValueError, ImportError) as error:
        print(f"Cannot run cases: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
