# Performance procedure trials

## Scope and method

Evaluate the approved performance procedure in discovery, implementation, and validation.
Four task cases cover incorrect completed-work accounting, an actual repeated-read optimization,
a completed change's unsupported full-operation claim, and close alternatives. A control requests
one checked rough estimate. Supplied states test continuation; source bounds may settle an
investigation without unnecessary timing runs. The initial procedure is followed by a targeted single-run reporting clarification; no
comparison with the earlier workflow without this procedure is claimed.

Candidates and separate blinded judges use `gpt-6.1-sol`, SDK/runtime `0.163.0`, three attempts per case,
1,800-second candidate turns, 1,200-second assessments, and no token cutoff. Same-family judging
and small local timing models limit conclusions about normal workloads and production performance.

## Results

| Case | Attempts 1 / 2 / 3 | Outcome |
| --- | --- | --- |
| Completed-work discovery | Correct / correct / correct | Identified missing labels and invalid throughput; withheld rollout approval. |
| Repeated-catalog implementation | Correct / correct / correct | Measured baseline and alternating comparisons; complete results and freshness preserved. |
| Completed-change validation | Correct / correct / correct | Rejected full-operation claim and unmet target; preserved requirements. |
| Close engine comparison | Correct / correct / correct | Checked equivalent work; used repeated statistics and declined an unsupported winner. |
| Rough single-run control, initial | Correct / incorrect / correct | All measured complete correct work once; one omitted simulated storage waits from reported conditions. |
| Rough control, clarified | Correct / correct / correct | Fresh attempts report simulated delays and preserve the one-run scope. |

Eight independently authored calibration examples matched all expected judgments: three correct,
three incorrect, and two uncertain incomplete recordings. Positive sources, command receipts, and
negative controls were inspected. Cases and calibration were authored independently before
subject trials. All eighteen outputs and relevant actions were inspected. Definitions, instruction snapshots,
complete recording, mechanical checks and isolation were verified. Independent audit confirmed the control
failure as a narrow reporting omission; measurement and correctness passed. The approved clarification explicitly requires identifying simulated work or delays in a
rough estimate. Its three fresh attempts pass with unchanged criteria. The other twelve task
results concern unaffected requirements and are reused; their instruction snapshots differ only
by this clarification. The initial failure remains a reporting defect, not an invalid measurement.

## Fixture corrections and repository checks

Offline regressions reproduced two grader defects before repair: removing the accepted adapter
delay and bypassing that adapter while retaining an unused helper. Correct implementations with
one catalog snapshot per call, per-SKU caching, renamed internal helpers, and imported sleep
aliases pass; dropped work, stale catalogs, fabricated results, and adapter bypasses fail.
Discovery seeds were corrected to an existing workflow before trials. All seeds resume through
the actual navigator.

The new navigator access test failed at all ten intended entry points before implementation.
After registration, 86 workflow, context, navigator and packaging tests pass; 33 case/fixture
tests pass; 49 recovery/session/project-fixture regressions also pass (168 tests total).
All 184 definitions validate. Lint, strict typing, structural skill validation,
formatting, and whitespace checks pass. Independent intent and engineering delivery reviews passed with no findings.

Adapted from pstack's [benchmark checklist](https://github.com/backnotprop/pstack/blob/74bcc61bd216687b1d6d480c28f109adfc9824ec/skills/benchmark-checklist/SKILL.md)
and [performance workflow](https://github.com/backnotprop/pstack/blob/74bcc61bd216687b1d6d480c28f109adfc9824ec/skills/poteto-mode/playbooks/perf-issue.md).
[Run commands](../agent-evaluations.md#performance-measurement).
