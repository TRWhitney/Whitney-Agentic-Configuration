# Research Procedure

Answer one bounded factual question needed by the current work. Return findings to the owning
state without making a knowledge-organization judgment, changing accepted intent, or expanding the
prompt.

## Frame the question

State the question, why its answer matters, its scope and exclusions, the needed evidence, and the
stopping condition. If the outcome depends on preference or knowledge-organization intent, research
the factual parts and return the remaining judgment to me.

Inspect evidence already authorized by the owning state directly when the question can be answered
from current artifacts, relevant notes, configuration, history, or a small set of supporting
documents. Reading those sources is ordinary context gathering and must not be replaced by
delegation.

## Investigate

- Use a fresh-context subagent when available for external multi-source investigation, comparison
  of technologies or standards, an unfamiliar domain, conflicting claims, or a bounded experiment
  whose independence improves the answer. If another agent delegated the current work to you,
  perform the research yourself; do not delegate it again. Do not delegate vault orientation or
  reading a handful of relevant notes. A subagent may supplement a larger vault investigation only
  after you have inspected its decision-bearing sources directly.
- Give the subagent the exact question, scope, relevant artifacts, source constraints, and expected
  form of the result, including retention rules and any explicitly requested exceptions. Do not
  supply a preferred conclusion, an unverified hypothesis, or unrelated vault history.
- Keep the subagent's vault and Git access read-only. It must not edit notes, configuration, or
  attachments; stage, commit, alter repository history, or discard changes; or expand its file
  scope. Have it return findings and citations.
- Use multiple search approaches and sources when available. Try alternate terminology and search
  paths before concluding that evidence does not exist. Prefer original, authoritative, and current
  sources; use secondary sources to add context or identify disagreements.
- Follow material claims to their supporting source. Do not treat repeated copies of one claim as
  independent confirmation. Cite vault paths and locations or direct external sources.
- Investigate conflicts instead of selecting the convenient source. Check publication dates,
  applicable versions, assumptions, and whether the sources address the same conditions.
- Keep searches and experiments bounded to the question. Generate raw outputs in temporary
  directories outside the vault or checkout. Record a concise setup, measured comparisons,
  failures, and limitations so useful checks can be rerun. Do not retain per-run captures for exact
  historical replay unless I explicitly request it.

## Assess and preserve

Inspect the original evidence behind consequential findings and confirm that each citation supports
the claim attributed to it. Distinguish established facts, supported inferences, recommendations,
and unresolved uncertainty. State when the available evidence is insufficient rather than filling
the gap with an assumption.

Research remains read-only. When later work will need to revisit the evidence, reasoning, or
citations, return a report-ready record for the owning state instead of creating a note. Default
to one report of at most 500 words plus a compact results table per study; expand only at my
explicit request. Update existing findings when they fit. Include the
question, scope, conclusion, evidence, source links, conflicts, limitations, and implications. Link
external and vault sources rather than copying material. Otherwise keep the finding in its owning
work.

After inspection and required review, delete disposable captures. Keep reusable checks and concise
findings. Do not commit raw outputs or create evidence manifests, deletion inventories, or
substitute archives. Requested canonical source notes remain governed by source preservation.

## Result

Include the direct answer, supporting evidence and citations, conflicting evidence, uncertainty,
and implications for the work that requested the research. Identify any judgment or next question
that remains mine to resolve.
