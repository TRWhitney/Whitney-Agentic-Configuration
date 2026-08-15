# Research Procedure

Answer one bounded factual question needed by the current work. Return findings to the owning
state without making a product judgment, changing accepted intent, or expanding the task.

## Frame the question

State the question, why its answer matters, its scope and exclusions, the needed evidence, and the
stopping condition. If the outcome depends on preference or product intent, research the factual
parts and return the remaining judgment to me.

Inspect the current repository directly when the question can be answered from its relevant code,
configuration, history, or a small set of project documents. Reading those sources is ordinary
context gathering and must not be replaced by delegation.

## Investigate

- Use a fresh-context subagent when available for external multi-source investigation, comparison
  of technologies or standards, an unfamiliar domain, conflicting claims, or a bounded experiment
  whose independence improves the answer. Do not delegate repository orientation or reading a
  handful of relevant files. A subagent may supplement a larger repository investigation only
  after you have inspected its decision-bearing sources directly.
- Give the subagent the exact question, scope, relevant artifacts, source constraints, and
  expected form of the result. Do not supply a preferred conclusion, an unverified hypothesis, or
  unrelated project history.
- Keep the subagent's Git access read-only. It must not stage, commit, alter repository history,
  discard changes, or expand its file scope. Have it return findings and citations.
- Search through more than one approach and source when available. Try alternate terminology and
  search paths before concluding that evidence does not exist. Prefer original, authoritative,
  and current sources; use secondary sources to add context or identify disagreements.
- Follow material claims to their supporting source. Do not treat repeated copies of one claim as
  independent confirmation. Cite repository paths and locations or direct external sources.
- Investigate conflicts instead of selecting the convenient source. Check publication
  dates, applicable versions, assumptions, and whether the sources are addressing the same
  conditions.
- Keep commands and experiments bounded to the question. Record the setup, decisive observations,
  and limitations needed to interpret or reproduce their result.

## Assess and preserve

Inspect the original evidence behind consequential findings and confirm that each citation
supports the claim attributed to it. Distinguish established facts, supported inferences,
recommendations, and unresolved uncertainty. State when the available evidence is insufficient
rather than filling the gap with an assumption.

Create a dedicated report only when future work will need to revisit the evidence, reasoning, or
citations. When a durable effort exists, store that report under
`.work/<effort-slug>/research/<research-slug>.md` uncommitted; commit it with the completed outcome
during delivery in normal repository history. Include the question, scope, conclusion, evidence,
source links, conflicts, limitations, and implications. Link external and repository sources rather
than copying material. Otherwise keep the finding in its owning answer, decision, specification, or
ticket.

## Result

Include the direct answer, supporting evidence and citations, conflicting evidence, uncertainty,
and implications for the work that requested the research. Identify any judgment or next question
that remains mine to resolve.
