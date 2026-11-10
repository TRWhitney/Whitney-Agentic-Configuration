"""Assess independently labeled examples with an explicitly selected model."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from evals.assessment import assess
from evals.calibration import load_calibration
from evals.output_paths import external_output
from evals.runner import DriverFactory


def main(
    arguments: Sequence[str] | None = None,
    *,
    driver_factory: DriverFactory | None = None,
) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument(
        "--examples",
        type=Path,
        default=Path(__file__).parent / "calibration/prose-boundaries.json",
    )
    parser.add_argument("--review-dir", type=Path)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--max-tokens", type=int, default=0)
    args = parser.parse_args(arguments)
    try:
        review = external_output(args.review_dir) if args.review_dir else None
        if review is not None and review.is_relative_to(
            Path(__file__).resolve().parents[1]
        ):
            parser.error("Review evidence must be outside the checkout.")
        if args.timeout <= 0 or args.max_tokens < 0:
            parser.error("Time must be positive; token guard must be nonnegative.")
        code, summary = evaluate(
            args.examples,
            args.model,
            timeout=args.timeout,
            max_tokens=args.max_tokens,
            review=review,
            driver_factory=driver_factory,
        )
    except (OSError, ValueError) as error:
        print(f"Cannot calibrate: {error}", file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2))
    return code


def evaluate(
    examples: Path,
    model: str,
    *,
    timeout: float = 1200,
    max_tokens: int = 0,
    review: Path | None = None,
    driver_factory: DriverFactory | None = None,
) -> tuple[int, dict[str, object]]:
    rubric, runs, expected = load_calibration(examples)
    results = assess(
        rubric,
        runs,
        model,
        timeout=timeout,
        max_tokens=max_tokens,
        review_dir=review,
        driver_factory=driver_factory,
    )
    output = []
    for i, result in results.items():
        verdict = result.criteria[0]["verdict"] if result.criteria else None
        output.append(
            {
                "example": runs[i].case,
                "expected": expected[runs[i].case],
                "agrees": verdict == expected[runs[i].case]
                and result.status
                == {"met": "pass", "not_met": "fail", "uncertain": "inconclusive"}[
                    expected[runs[i].case]
                ],
                "assessment": asdict(result),
            }
        )
    clear = [r for r in output if r["expected"] != "uncertain"]
    summary: dict[str, object] = {
        "clear_examples": len(clear),
        "clear_agreements": sum(bool(r["agrees"]) for r in clear),
        "results": output,
    }
    if len(results) != len(runs) or any(
        r.status in {"error", "limit"} for r in results.values()
    ):
        return 2, summary
    return (1 if any(not r["agrees"] for r in output) else 0), summary


if __name__ == "__main__":
    raise SystemExit(main())
