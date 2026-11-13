# Unslop writing trials

Six new writing cases and controls pass all eighteen repository-version attempts. Existing evals
still expose failures. No accepted skill prose changed.

## Method

Sources start at `8373b87`: accepted unslop versus Poteto `18e0e90`, with no other instruction
differences. Tasks, settings and private criteria were fixed within comparisons. Candidates and
a separate blinded judge used gpt-6.1-sol, 1800/1200-second allowances and disabled token guards.
The same-family limitation remains. All 298 candidate assessments completed. Complete outputs,
relevant actions, available child findings, and GUI images/structures were inspected. Installed
source bytes and isolation matched all 298 attempts; successful unslop reads were observed in
all 72 writing attempts, separately from quality.

## Writing comparison

C/I/U mean inspected correct/incorrect/unknown. Each cell lists three attempts in order.
Repository writing totals are 35C/1I; Poteto 34C/2I. These trials establish no general advantage.

| Case | Poteto | Repository |
| --- | --- | --- |
| unslop-clear-writing | C/C/C | C/C/C |
| unslop-concise-explanation | C/C/C | C/C/C |
| unslop-final-reply | C/C/C | C/C/C |
| unslop-revisions-retain-decisions | C/C/C | C/C/C |
| unslop-technical-terms | C/C/C | C/C/C |
| unslop-vague-explanation | C/C/C | C/C/C |
| followup-keeps-process-out-of-prose | C/C/C | C/C/C |
| github-pr-description-small | C/C/I | C/C/C |
| github-pr-description | C/C/I | I/C/C |
| narrow-prose-correction | C/C/C | C/C/C |
| useful-source-uncertainty-stays-visible | C/C/C | C/C/C |
| writing-preferences-stay-out-of-prose | C/C/C | C/C/C |

## Fresh follow-ups

These 72 attempts include three per source for every revised criterion and relevant controls.
Earlier superseded judgments remain below. Assessment completion does not establish correctness.

| Case or repair | Poteto | Repository |
| --- | --- | --- |
| agent-created-state-compaction | I/C/C | I/C/C |
| commit-completed-work-across-tree | C/C/C | C/C/C |
| completed-prerequisite-is-missing | C/C/I | C/C/C |
| correction-review-stays-bounded | C/C/C | C/C/C |
| review-stays-read-only | C/C/C | C/C/C |
| diagnosis-needs-design | C/C/C | C/C/C |
| evidence-reopens-design | C/C/C | C/C/C |
| gui-incomplete-audit, capture repair | I/C/C | C/C/C |
| gui-keyboard-naming, corrected criterion | C/C/C | U/C/U |
| requirements-change-during-implementation | C/C/I | C/C/C |
| missing-implementation-ticket | C/C/C | C/C/C |
| gui-keyboard-naming, navigation recording | C/C/C | C/C/C |

## Failures and limits

| Attempts | Failed or unresolved criteria | Observed behavior |
| --- | --- | --- |
| Original agent-created-state-compaction | criterion-4 | Recovered decisions and records, but omitted the next question. |
| Original github-pr-description | revision-evidence | Filed body omitted known unavailable CI results; disclosure elsewhere did not satisfy it. |
| Original no-documentation-change-needed | finish-small-change | Completed the label change, but omitted the required explanation that documentation needed no change. |
| Original review-reports-outside-data-loss | ownership-and-report; review-evidence | Reported the confirmed empty-selection deletion bug without repairing it or retaining its regression test. |
| Original wayfinding-derives-settled-choices | derive-availability; reserve-material-choice; consistent-planning-state | Asked for approval of settled occupancy arithmetic instead of the unresolved insufficient-capacity behavior. |
| Writing small PR, Poteto3 | issue reference | Omitted required footer. |
| Writing large PR, Poteto3/repository1 | revision-evidence | Omitted known unavailable CI results from filed bodies. Judges falsely passed both, including two unchanged-work reassessments. |
| Follow-up prerequisite, Poteto3 | no-speculation; record-real-blocker | Implemented search and export together. Its additional prerequisite-identification rejection is disputed: missing search was identified. |
| Follow-up requirements, Poteto3 | criterion-2 | Updated status/ticket but left CSV-only and all-decisions-settled claims in the specification. |
| Capture follow-up, Poteto1 | finished-workspace | Narrow populated search height changed71→57px when cleared. |
| Earlier keyboard follow-up, repository1/3 | report | Ctrl+r and same title did not prove claimed reload; original recording cannot resolve it. |
| Original initial-review-without-priming | criterion-2 | Original negative judgment overturned after source-based adjudication: narrow wording-check evidence is required validation context, not a review verdict. Original failure and later passing reassessment retained. |

## Eval repairs and excluded judgments

| Defect or trial | Resolution and retained evidence |
| --- | --- |
| Three transfer-guide false failures; ambiguous prose calibration falsely certain | Supported source limits were mistaken for compliance reports. Shared assessor clarification; both reassessments pass all six unchanged outputs. |
| Supplied validation history rejected | Accept supplied factual history for unchanged work. Frozen failed case passes; three independent controls retain stale/invented-validation failures. |
| Two invalid diagnoses; corrected recording calibration initially six errors | Shared assessor distinguishes observed recording loss from uncertain coverage. Six final examples agree. Two earlier wrong-fixture runs excluded: archive metadata was placed outside supplied files. |
| Extra PR artifact-disclosure assessor sentences | Did not fix large-packet false passes; reverted. Five independent evidence examples pass despite this unresolved assessor limitation. |
| Eight superseded criteria, S below | Missing prerequisite may be repaired; native hidden assignments ungraded; allowed diagnosis route accepted; requested factual design update needs no invented approval; keyboard continuation does not demand an exact focus target; one next question is enough; readiness question needs no unrequested ticket draft. Fresh comparisons replace these scores. |
| Six mechanical corrections, M below | Optional owned commit record; issue updates/existing PR comments allowed in three planning cases; corrigible summary excluded from source freeze; specific pre-fix failure accepted inside a successful compound shell. Retained outputs rechecked with adverse regression controls. |
| Lost sleep items | Native payload retention repaired; unknown events remain partial. Fresh capture attempts contained no sleep, so only adapter tests exercise that path. |
| Reload evidence | General main-document identity/load and same-document events now distinguish navigation. Real headless Ctrl+r did not reload. Final six attempts have sufficient evidence; earlier unknowns remain. Seven other keypress-only reload claims were outside frozen criteria. |

All 59 final calibration labels agree, including three deliberately uncertain examples. Calibration
does not remove the documented false passes. Six email rhetorical questions, one unobserved
child review, and a reopened-design record's stale committed-status sentence remain outside the
selected criteria. No uniform final 160-case run or failure rate is claimed.

Framework: 548 tests, Ruff lint/format, strict mypy and 160 definitions pass. Independent intent and engineering reviews pass. Raw evidence was inspected and reviewed outside Git,
then deleted before delivery.

## Original corpus, one attempt per case

Original engine totals: 134C/17I/3U; all 154 assessments completed. The inspected column applies
accepted intent. S marks superseded criteria, excluded from current-comparison totals; M marks
mechanical corrections. This table preserves every original attempt alongside its stored grade.

| Case | Purpose | Inspected | Original engine | Repair |
| --- | --- | --- | --- | --- |
| agent-created-state-compaction | control | I | I |  |
| all-tickets-blocked | task | C | C |  |
| amend-preserves-earlier-edit | task | C | C |  |
| broken-verification-setup | task | C | C |  |
| cancel-without-replacement | task | C | C |  |
| changed-decision-tickets | task | C | C |  |
| choose-ready-ticket | task | C | C |  |
| choose-reversible-implementation-detail | task | C | C |  |
| cleanup-distinguishes-data-checks-and-captures | task | C | C |  |
| cleanup-keeps-other-conversation-evidence | task | C | C |  |
| cleanup-preserves-supplied-input | task | C | C |  |
| combine-related-planning-records | task | C | C |  |
| commit-completed-work-across-tree | task | C | I | M |
| commit-hook-keeps-delivery-pending | task | C | C |  |
| complete-dependent-tickets | task | C | C |  |
| complete-local-workflow | task | C | C |  |
| complete-research-investigation | task | C | C |  |
| completed-prerequisite-is-missing | task | C | I | S |
| conflicting-sources-need-version-and-conditions | task | C | C |  |
| conflicting-specification-ticket | task | C | C |  |
| contractual-service-interaction | task | C | C |  |
| conversations-share-current-document | task | C | C |  |
| copied-claims-need-original-source | task | C | C |  |
| correction-review-stays-bounded | task | C | U | S |
| correction-without-reminder | task | C | C |  |
| cyclic-ticket-dependencies | task | C | C |  |
| damaged-navigation-record | task | C | C |  |
| delegate-explicit-file-and-git-permissions | focused | C | C |  |
| delegated-parts-fail-together | task | C | C |  |
| delivery-retains-accepted-prototype | task | C | C |  |
| design-changed-after-planning-merge | task | C | C |  |
| diagnosis-keeps-failed-attempt | task | C | C |  |
| diagnosis-needs-design | task | C | I | S |
| diagnosis-without-reproduction | task | C | C |  |
| documentation-examples-run | task | C | C |  |
| edit-after-review | task | C | C |  |
| evidence-reopens-design | task | C | I | S |
| experiment-measures-partial-operation | task | C | C |  |
| explicit-compaction | task | C | C |  |
| explicit-retention-outside-git | control | C | C |  |
| failed-verification | task | C | C |  |
| feature-request-needs-planning | task | C | C |  |
| followup-keeps-process-out-of-prose | task | C | C |  |
| fresh-handoff-separates-directions-from-content | task | C | C |  |
| github-create-timeout | task | C | C |  |
| github-planning-edit-persists | task | C | C |  |
| github-planning-read-failure | task | C | C | M |
| github-pr-description-small | control | C | C |  |
| github-pr-description | task | I | I |  |
| gui-accepted-design | task | C | C |  |
| gui-browser-rendering | task | C | C |  |
| gui-clean-audit | control | C | C |  |
| gui-combined-conditions | task | C | C |  |
| gui-incomplete-audit | task | C | U |  |
| gui-keyboard-naming | task | C | I | S |
| gui-layout-and-wrapping | task | C | C |  |
| gui-shared-change-other-view | task | C | C |  |
| gui-state-changes | task | C | C |  |
| gui-state-selection | task | C | C |  |
| implementation-conflicts-with-documentation | task | C | C |  |
| incomplete-design | task | C | C |  |
| independent-test-expectation | task | C | C |  |
| initial-review-without-priming | task | C | I | M |
| inspect-returned-work-not-summary | task | C | C |  |
| interactive-prototype-comparison | task | C | C |  |
| link-shared-domain-definition | task | C | C |  |
| local-tracking | task | C | C |  |
| masked-check-failure | task | C | C |  |
| missing-implementation-ticket | task | C | I | S |
| missing-work-record | task | C | C |  |
| mocked-project-connection | task | C | C |  |
| narrow-correction | task | C | C |  |
| narrow-prose-correction | task | C | C |  |
| new-interface-design | task | C | C |  |
| new-task-after-completion | task | C | C |  |
| no-documentation-change-needed | task | I | I |  |
| order-dependent-test-failure | task | C | C |  |
| outdated-recap | task | C | C |  |
| parent-red-before-delegation | focused | C | C |  |
| partial-completion | task | C | C |  |
| passing-example-is-not-validation | task | C | C |  |
| pending-evidence-through-compaction | task | C | C |  |
| permission-applies-only-to-named-file | task | C | C |  |
| planning-continue-discussion | task | C | C |  |
| planning-pr-closed | task | C | I | M |
| planning-pr-merged | task | C | C |  |
| planning-pr-unmerged | task | C | I | M |
| planning-without-document-pr | task | C | C |  |
| preserve-error-cause-and-safe-message | task | C | C |  |
| preserve-explicit-uncommitted-draft | task | C | C |  |
| preserve-uncommitted-work | task | C | C |  |
| prohibitions-stay-out-of-reader-text | task | C | C |  |
| proposed-domain-term-stays-proposed | task | C | C |  |
| protected-files-need-permission | task | C | C |  |
| prototype-returns-to-planning | focused | C | C |  |
| question-before-change | task | C | C |  |
| quoted-source-directions-do-not-control-agent | task | C | C |  |
| ready-implementation | task | C | C |  |
| refactor-brittle-internal-test | task | C | C |  |
| regression-fails-for-wrong-reason | task | C | C |  |
| regression-through-public-command | task | C | C |  |
| related-feature-questions | task | C | C |  |
| remove-obsolete-export-paths | task | C | C |  |
| replace-workflow | task | C | C |  |
| replaced-decision-keeps-reason | task | C | C |  |
| reproducible-bug | task | C | I | M |
| requested-methods-have-their-own-report | task | C | C |  |
| requirements-change-during-implementation | task | C | I | S |
| rerun-after-correction | task | C | C |  |
| research-original-unavailable | task | C | C |  |
| results-survive-cleanup | task | C | C |  |
| resume-stale-validation | task | C | C |  |
| reuse-existing-quantity-parser | task | C | C |  |
| review-contradicts-accepted-design | task | C | C |  |
| review-finding-rework | task | C | C |  |
| review-keeps-needed-evidence | task | C | C |  |
| review-reports-outside-data-loss | task | I | I |  |
| review-requires-product-decision | task | C | C |  |
| review-stays-read-only | task | C | U | S |
| seeded-wayfinding-recovery | task | C | C |  |
| self-review-is-not-called-independent | task | C | C |  |
| separate-conversations | task | C | C |  |
| separate-independent-commits | task | C | C |  |
| session-rework-after-push | task | C | C |  |
| split-large-implementation-ticket | task | C | C |  |
| start-wayfinding-from-conversation | control | C | C |  |
| test-real-project-behavior | task | C | C |  |
| tool-limits-stay-out-of-consumer-guide | task | C | C |  |
| tracker-converts-existing-work | task | C | C |  |
| tracker-separate-conversations | task | C | C |  |
| unavailable-verification | task | C | C |  |
| unsupported-review-does-not-block | task | C | I |  |
| use-supplied-clock | task | C | C |  |
| useful-source-uncertainty-stays-visible | task | C | C |  |
| verification-claims-match-recorded-results | task | C | C |  |
| verification-directions-stay-out-of-guide | task | C | C |  |
| wayfinding-after-research | task | C | C |  |
| wayfinding-blocked-question | task | C | C |  |
| wayfinding-code-question | task | C | C |  |
| wayfinding-complete | task | C | C |  |
| wayfinding-counts | task | C | C |  |
| wayfinding-derives-settled-choices | task | I | I |  |
| wayfinding-follow-up | task | C | C |  |
| wayfinding-multiple-answers | task | C | C |  |
| wayfinding-partial-answer | task | C | C |  |
| wayfinding-reopens-dependent-answer | task | C | C |  |
| wayfinding-revised-answer | task | C | C |  |
| wayfinding-short-replies | task | C | C |  |
| wayfinding-stop | task | C | C |  |
| worker-completes-valid-assignment | task | C | C |  |
| worker-invalid-supplied-test | task | C | C |  |
| write-complete-implementation-tickets | task | C | C |  |
| write-regression-test | task | C | C |  |
| writing-preferences-stay-out-of-prose | task | C | C |  |
