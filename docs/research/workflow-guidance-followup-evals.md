# Further procedure guidance evaluations

## Question

Does the agent reject unsupported review blockers, remove obsolete code, reuse existing
parsers, keep proposed terms unsettled, link shared definitions, and check original sources?

## Method

Run seven further guidance cases twice with gpt-6.1-sol and Codex SDK/runtime 0.163.0. Each
attempt allows 600,000 reported tokens and 360 seconds. Reuse the existing disposable projects,
prepared Python checks, file checks, reply patterns, and saved-state checks. Apps and tool network
access remain disabled. Research uses supplied local excerpts. No compaction is requested.

## Results

All 14 attempts pass against the final checks. No runtime error, allowance limit, or external
service call occurred. Reported usage ranged from 78,244 to 372,638 tokens, including repeated
input across calls. Workflow instructions remain unchanged.

| Target | Case | First attempt | Repeat |
| --- | --- | --- | --- |
| 11 | [Unsupported review blockers](../../evals/cases/unsupported-review-does-not-block.json) | Pass | Pass |
| 15 | [Remove obsolete export paths](../../evals/cases/remove-obsolete-export-paths.json) | Pass | Pass |
| 16 | [Reuse the quantity parser](../../evals/cases/reuse-existing-quantity-parser.json) | Pass | Pass |
| 17 | [Keep a proposed term unsettled](../../evals/cases/proposed-domain-term-stays-proposed.json) | Pass | Pass |
| 19 | [Link the shared definition](../../evals/cases/link-shared-domain-definition.json) | Pass | Pass |
| 20 | [Check the original source behind copied claims](../../evals/cases/copied-claims-need-original-source.json) | Pass | Pass |
| 21 | [Explain conflicting versions and account limits](../../evals/cases/conflicting-sources-need-version-and-conditions.json) | Pass | Pass |

Both review assessments reject the stylistic change and unsupported input expansion as blockers
without editing code. Export defaults to JSON, rejects CSV options, and retains no checked CSV
symbols. Import uses the existing quantity parser and standard CSV reader. Proposed terminology
stays in planning; the accepted definition lives in the glossary and is linked from the record.
Both research cases identify the Basic-account limit, cite the original manual, and explain the
source chain or the version and account differences.

## Check quality

Offline examples reject leftover CSV code, hardcoded export output, a duplicate parser,
discarded parser results, a premature glossary entry, copied definitions, missing links,
unsupported blockers, inverted account limits, missing citations, and copied claims presented as
independent confirmation. All 278 infrastructure tests pass. All 97 definitions validate; Ruff
and mypy pass.

The first term-proposal check wrongly required a question mark. Both replies already marked the
term unaccepted. The corrected check accepts that explicit status, and the same captures pass
without further model calls. Export checks permit documentation to mention a removed option.

## Limits

Two attempts with one model do not establish reliability. Text and syntax checks cover the
prepared examples, not every valid paraphrase or possible duplicate implementation. Local
excerpts do not test web search. Child-agent assignments and correction-review boundaries remain
untested. Earlier recorded failures remain open. [Earlier guidance results](workflow-guidance-evals.md).
