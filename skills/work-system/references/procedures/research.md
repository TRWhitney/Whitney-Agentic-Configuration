# Research procedure

Investigate factual uncertainty for the owning feature or accepted work.
Related questions, comparisons, and experiments belong to the same investigation. Research and
planning are methods within that work, not separate work items. Return findings to its owning
state and record without making a product judgment, changing accepted intent, or expanding the task.

## Frame the investigation

Identify the owning feature or work record and its existing research report. Each distinct feature
has one combined research-and-planning ticket. Only a distinct feature can receive another such
ticket. Its questions, subcontracts, and architecture concerns remain inside that owner, including
follow-up findings. Different sources, methods, experiments, agents, or contexts do not create
another planning or research ticket. Actual implementation is decomposed separately into logical
units of work under the accepted feature design.

State the related questions, why their answers matter, scope and exclusions, needed evidence, and
the stopping condition for the subject. Stop when the findings support the current planning or
delivery decision. If the outcome depends on preference or product intent, research the factual
parts and return the remaining judgment to me within the same work item.

Inspect the current repository directly when the question can be answered from its relevant code,
configuration, history, or a small set of project documents. Reading those sources is ordinary
context gathering and must not be replaced by delegation.

## Investigate

- Use a fresh-context subagent when available for external multi-source investigation, comparison
  of technologies or standards, an unfamiliar domain, conflicting claims, or a bounded experiment
  whose independence improves the answer. If another agent delegated the current work to you,
  perform the research yourself; do not delegate it again. Do not delegate repository orientation
  or reading a handful of relevant files. A subagent may supplement a larger repository
  investigation only after you have inspected its decision-bearing sources directly.
- Give the subagent the subject, related questions, owning record, existing findings, scope,
  relevant artifacts, source constraints, and expected form of the result, including the
  retention rules and any explicitly requested exceptions. Do not supply a preferred conclusion,
  an unverified hypothesis, or unrelated project
  history. Delegate the subject's related research together rather than creating an assignment
  for each question.
- Keep the subagent's Git access read-only. It must not stage, commit, alter repository history,
  discard changes, or expand its file scope. Have it return findings and citations.
- Use multiple search approaches and sources when available. Try alternate terminology and
  search paths before concluding that evidence does not exist. Prefer original, authoritative,
  and current sources; use secondary sources to add context or identify disagreements.
- Follow material claims to their supporting source. Do not treat repeated copies of one claim as
  independent confirmation. Cite repository paths and locations or direct external sources.
- Investigate conflicts instead of selecting the convenient source. Check publication
  dates, applicable versions, assumptions, and whether the sources are addressing the same
  conditions.
- Keep commands and experiments bounded to the subject and its stopping condition. Generate raw
  outputs in temporary directories outside the checkout. Record a concise setup, measured
  comparisons, failures, and limitations so useful checks can be rerun. Do not retain per-run captures for exact historical
  replay unless I explicitly request it.

## Assess and preserve

Inspect the original evidence behind consequential findings and confirm that each citation
supports the claim attributed to it. Distinguish established facts, supported inferences,
recommendations, and unresolved uncertainty. State when the available evidence is insufficient
rather than filling the gap with an assumption.

Create a dedicated report only when future work will need to revisit the evidence, reasoning, or
citations and no existing report owns the subject. Store it in the repository's research
documentation, following its existing layout or using `docs/research/<research-slug>.md`. Keep one
current report for that subject, including later related questions and experiments.
Default to at most 500 words plus a compact results table; expand only at my explicit request.
Update its conclusions as research progresses rather than creating a report for each question or
pass. Include the subject, related questions, scope, conclusion, evidence,
source links, conflicts, limitations, and implications. Link external and repository sources rather
than copying material. Otherwise keep the finding in its owning answer, decision, specification, or
ticket.

After inspection and required review, delete disposable captures. Keep reusable source or checks
and concise findings. Do not commit raw outputs or create evidence manifests, deletion inventories,
or substitute archives.

## Result

Include the direct answer, supporting evidence and citations, conflicting evidence, uncertainty,
and implications for the work that requested the research. Identify any judgment or next question
that remains mine to resolve.
