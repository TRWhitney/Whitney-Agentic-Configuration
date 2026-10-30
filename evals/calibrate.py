"""Assess independently labeled examples with an explicitly selected model."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from evals.assessment import assess
from evals.calibration import load_calibration


def main() -> int:
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
    args = parser.parse_args()
    review = args.review_dir.expanduser().resolve() if args.review_dir else None
    if review is not None and review.is_relative_to(
        Path(__file__).resolve().parents[1]
    ):
        parser.error("Review evidence must be outside the checkout.")
    if args.timeout <= 0 or args.max_tokens < 0:
        parser.error("Time must be positive; token guard must be nonnegative.")
    rubric, runs, expected = load_calibration(args.examples)
    results = assess(
        rubric,
        runs,
        args.model,
        timeout=args.timeout,
        max_tokens=args.max_tokens,
        review_dir=review,
    )
    output = []
    for i, result in results.items():
        verdict = result.criteria[0]["verdict"] if result.criteria else None
        output.append(
            {
                "example": runs[i].case,
                "expected": expected[runs[i].case],
                "agrees": verdict == expected[runs[i].case],
                "assessment": asdict(result),
            }
        )
    clear = [r for r in output if r["expected"] != "uncertain"]
    print(
        json.dumps(
            {
                "clear_examples": len(clear),
                "clear_agreements": sum(bool(r["agrees"]) for r in clear),
                "results": output,
            },
            indent=2,
        )
    )
    return 2 if any(r.status in {"error", "limit"} for r in results.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
