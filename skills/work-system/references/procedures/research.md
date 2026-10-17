# Research procedure

Investigate factual questions for the current feature or agreed work. Related questions,
comparisons, and experiments belong together. Return findings to the current state and work
record without making product decisions, changing requirements, or expanding the task.

## Define the question

Find the feature ticket or work record and its existing research report. Keep one combined
research-and-planning ticket per feature, including follow-up questions and architecture
concerns. A new source, method, experiment, agent, or context does not justify another planning
ticket. Implementation is divided separately into tasks that deliver parts of the agreed
feature.

State the questions, why they matter, scope, exclusions, needed sources or checks, and when to
stop. Stop when the findings support the current planning or delivery decision. Research facts
and return preference or product decisions to me in the same work item.

Read relevant code, configuration, history, and project documents yourself when they can answer
the question. Do not delegate ordinary repository reading.

## Investigate

- Use a fresh-context subagent when available for research across external sources, technology
  or standards comparisons, unfamiliar topics, conflicting claims, or experiments that benefit
  from an independent investigator. If this work was delegated to you, do it yourself; do not
  delegate again. Do not delegate basic orientation or reading a few files. For larger
  investigations, read the sources that affect the decision yourself before delegating
  additional research.
- Give the subagent the question, scope, relevant sources, source restrictions, expected result,
  cleanup rules, and any exceptions I requested. Do not suggest an answer, supply an untested
  hypothesis, or include unrelated history. Keep a subject's related questions in one delegated
  assignment.
- Keep the subagent's Git access read-only. It must not stage, commit, alter history, discard
  changes, or edit files outside its assigned scope. Require findings and citations in its
  reply.
- Try multiple search terms and sources before concluding that information is unavailable.
  Prefer original, authoritative, current sources. Use secondary sources for context or
  disagreements.
- Check important claims against their original sources. Repeated copies of one claim are not
  independent confirmation. Cite source paths and locations or direct external links.
- Investigate disagreements. Compare dates, versions, assumptions, and the conditions each
  source addresses instead of choosing the convenient answer.
- Keep searches and experiments within the question and stop when they support the decision at
  hand. Generate raw outputs in temporary directories outside the checkout. Record enough setup,
  measured comparisons, failures, and limitations to rerun useful checks. Do not keep full run
  captures for later replay unless I explicitly request them.

## Check and record findings

Inspect the sources behind important findings and confirm that citations support their claims.
Separate facts, inferences, recommendations, and uncertainty. State when information is missing
rather than filling the gap with an assumption.

Create a research report only when future work needs its findings, reasons, or citations and no
existing report covers the subject. Use the repository's research layout or
`docs/research/<research-slug>.md`. Update that report for later questions and experiments. Keep
it under 500 words plus a compact results table unless I explicitly request more. Include the
question, scope, conclusion, supporting sources, disagreements, limitations, and effects on the
work. Link sources rather than copying them. Otherwise record findings in the answer, decision,
specification, or ticket that needs them.

After inspection and required review, delete temporary captures. Keep reusable code or checks
and concise findings. Do not commit raw outputs or replace them with manifests, deletion
inventories, or archives.

## Result

Return the answer, sources, disagreements, uncertainty, and what the findings mean for the work.
Identify decisions or questions that still need my judgment.
