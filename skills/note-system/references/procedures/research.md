# Research Procedure

Answer a limited factual question needed by the current work. Return findings to the current
state. Do not decide how to organize knowledge, change requirements, or expand the request.

## Define the question

State the question, why it matters, scope, exclusions, needed sources or checks, and when to
stop. Research facts and return preferences or knowledge-organization decisions to me.

Read sources already available to the current state, including relevant notes, configuration,
history, and supporting documents, when they can answer the question. Do not delegate ordinary
vault reading.

## Investigate

- Use a fresh-context subagent when available for research across external sources, technology
  or standards comparisons, unfamiliar topics, conflicting claims, or experiments that benefit
  from an independent investigator. If this work was delegated to you, do it yourself; do not
  delegate again. Do not delegate basic orientation or reading a few files. For larger
  investigations, read the sources that affect the decision yourself before delegating
  additional research.
- Give the subagent the question, scope, relevant sources, source restrictions, expected result,
  cleanup rules, and any exceptions I requested. Do not suggest an answer, supply an untested
  hypothesis, or include unrelated history.
- Keep the subagent's vault and Git access read-only. It must not edit notes, configuration, or
  attachments; stage, commit, alter history, or discard changes; or read outside its assigned
  scope. Require findings and citations in its reply.
- Try multiple search terms and sources before concluding that information is unavailable.
  Prefer original, authoritative, current sources. Use secondary sources for context or
  disagreements.
- Check important claims against their original sources. Repeated copies of one claim are not
  independent confirmation. Cite source paths and locations or direct external links.
- Investigate disagreements. Compare dates, versions, assumptions, and the conditions each
  source addresses instead of choosing the convenient answer.
- Keep searches and experiments within the question and stop when they support the decision at
  hand. Generate raw outputs in temporary directories outside the vault or checkout. Record
  enough setup, measured comparisons, failures, and limitations to rerun useful checks. Do not
  keep full run captures for later replay unless I explicitly request them.

## Check and record findings

Inspect the sources behind important findings and confirm that citations support their claims.
Separate facts, inferences, recommendations, and uncertainty. State when information is missing
rather than filling the gap with an assumption.

Research is read-only. If later work needs a report, return findings ready for the current state
to use instead of creating a note. Keep one report per study under 500 words plus a compact
results table unless I explicitly request more. Update existing findings when they fit. Include
the question, scope, conclusion, supporting sources, disagreements, limitations, and effects on
the work. Link sources rather than copying them. Otherwise return findings with the current
work.

After inspection and required review, delete temporary captures. Keep reusable checks and
concise findings. Do not commit raw outputs or replace them with manifests, deletion
inventories, or archives. Requested source notes follow the source-preservation procedure.

## Result

Return the answer, sources, disagreements, uncertainty, and what the findings mean for the work.
Identify decisions or questions that still need my judgment.
