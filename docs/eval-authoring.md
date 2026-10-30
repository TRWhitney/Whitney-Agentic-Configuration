# Writing agent evaluations

An eval should tell us whether an agent can do the work we expect. A high pass count is useful
only when the tasks and assessment cover that work.

## Define the question

Start with an observed failure or a clear behavior requirement. Record the expected outcome,
who needs it, what went wrong, and which facts support that account. Distinguish a reconstruction
from a real conversation replay. Changing the subject is fine when the cause and constraints
remain intact.

Compare new cases with existing coverage. Identify the new behavior or condition, or state that
the case adds another example of a behavior already covered.

Choose the case's purpose:

- A **focused** case isolates a rule, state transition, or known defect.
- A **task** case asks for an ordinary completed outcome and assesses the resulting work.
- A **control** case establishes that allowed behavior still succeeds.

Keep these results separate. A passing permission control does not establish that instruction
leakage is rare. Two attempts do not establish a failure rate in normal use.

## Write the task and context

Use a request someone would normally make. Supply the goal, necessary context, and genuine
constraints. Let the agent choose the required workflow and engineering steps. A reminder to
write a failing test cannot establish that the agent would choose that step without a reminder.
A narrow wording request can still name the exact word because that is the user's actual goal.

Before writing the request, state in the private rubric what the agent must do and an observable
mistake that would fail the case. Give the candidate the product result and necessary facts.
Leave the process being tested to the work system. "Finish the accepted change" can test whether
verification occurs; "audit the change" cannot establish that the agent chose to verify it.
A request to amend cannot establish that the work system chose amendment.

Audit every candidate-visible input against that behavior: requests, follow-ups, shared fixtures,
work records, supplied edits, earlier summaries, and tool descriptions. Remove instructions
that provide the tested step or pre-explain the judgment. Keep accepted product requirements,
available commands, and factual work history. "Project checks: checks/search.py" identifies a
tool; "Run checks/search.py before delivery" supplies the action being tested.

Keep user inputs needed to exercise a boundary, such as cancellation, named-file permission,
a requested capture inspection, or a chosen optional mode. State the limited claim in the
rubric. A requested delegation can test assignment permissions and proof before delegation;
it cannot establish that the skill chose to delegate. Do not remove that request and then fail
a correct direct implementation when delegation is optional. Assess reviewer restrictions on
the reviewer; the parent may need to correct and commit the reviewed work.

If a correct approach avoids the situation under test, do not make that approach fail. Supply
existing evidence that makes the situation relevant, or limit what the case can establish.

Include the files, drafts, decisions, competing evidence, and unfinished work that affect the
outcome. Preserve the order of meaningful corrections and follow-ups. Add context because it
changes the work, rather than to inflate its length. Keep routine conversations short. A supplied
workflow state tests whether the agent continues existing work. It cannot establish how the agent
would choose a workflow for a new request. Test actual compaction separately through an explicit
request, never by filling the context window.

Check that each follow-up changes something the agent still needs to do. An already satisfied
request cannot demonstrate a successful correction. Use normal project names and file paths.

## Keep assessment separate

Write three to six concrete criteria before running a task case. Describe observable behavior
and useful output, including what would fail each criterion. Keep the rubric, expected verdicts,
condition labels, and private grading code outside the candidate project. Real project tests
can remain visible; private grading assertions should not be presented as project files.

Check the actual artifact or action. A claim that checks passed is not an observed successful
check. Reading guidance is not proof that it was applied. Use code checks for exact contracts,
state, permissions, history, and command results. Assess meaning and completeness by reading
the finished work against the rubric. Exclude ordinary cache files from source-preservation
checks without excluding source files themselves.
Require a particular filename, format, test framework, workflow mode, pause, or unchanged file
only when the task, skill, or established project conventions require it.
A useful retained sample may have a different format. Repairing accepted behavior
does not require an extra permission pause merely because a case originally asked for one.
Locate GUI controls by their role and label where possible, and find containers through their
controls and content. Internal classes, IDs, and container tags are not product requirements
unless the accepted design requires them.
Accept different questions that leave the same unsettled product choice to the user.
Keep supplied file updates separate from agent edits in the assessment evidence. Include
starting tracker records and their later state when a task changes external work records.

For prose, distinguish task directions from subject content. Require useful subject content as
well as absence of leakage. Include controls for requested methods, relevant uncertainty, and
reader instructions that belong to the subject. Cover paraphrases, headings, tables, comments,
and ordinary sentence forms. Do not make a list of known phrases the entire assessment.

For GUI tasks, derive verification coverage from the accepted design and interactions. Cover
appearance and structure, alignment and visual grouping, wrapping and changing content,
transitions, and conditions that can affect one another. Include usable interfaces with subtle
layout defects, and correct interfaces that need no redesign. Supply an ordinary feature request;
keep defect locations and grading assertions private.

Use a production app with state and components distinct from the visual prototype. A correct
appearance must not hide missing production behavior. Confirm that copying the prototype
fails the task's real data flow while a correct production implementation passes. Keep simple
repairs as focused checks, not the sole evidence for implementation and integration.

For prose, include existing drafts, meaningful revisions, and related decisions that must
survive follow-ups. Include writing about agents and workflows, where author directions and
the subject share words. Check each delivered revision for leaked directions, factual errors, and
lost accepted content. Keep source checks and writing preferences outside the reader's text
without reminding the candidate to do so.

To test whether the agent adds process directions to prose, start with source material or a
draft that contains none. Removing an existing process report tests cleanup.

Use rendered images with structural observations and real interactions. Compare required
relationships and behavior while permitting documented variation. Private browser checks can
establish the resulting interface's behavior. They cannot establish that the candidate performed
those checks. Keep candidate browser observations distinct in both the evidence and assessment.
For visibility checks, a missing expected container or a failed exact text match does not prove
that the content is hidden. Check each part of messages split across elements.

## Check the assessor

Confirm that each code check accepts correct work and rejects a violation of its requirement.
Include different correct approaches when the requirements permit them. Keep these examples as
regression tests for the grader.

Use independently written examples of correct, incorrect, and genuinely ambiguous work. Keep
expected labels out of the judge's input. Include plausible errors that existing code checks
miss, and correct work that a broad prohibition might reject.

Record assessor disagreements and missing evidence. Review an ambiguous criterion or example
before treating disagreement as an agent failure. Freeze the criteria and examples before the
comparison; changing them to favor an output invalidates that comparison. If a fixture or
criterion is wrong, correct it and start a new comparison. Keep invalid or superseded attempts
out of the behavior totals and explain why they were excluded. If only a code check was wrong,
recheck every saved output when the evidence is sufficient; otherwise rerun the case.

Review the whole corpus when a shared authoring defect is found. Inspect the resolved fixtures
and supplied edits as well as top-level prompts. `python -m evals audit --integration` lists
process-language cues for inspection; these are not verdicts, and a clean scan does not establish
that a case is sound. Report what was reviewed, which cases changed, and which retained inputs
are necessary triggers or controls. Do not carry earlier passing outcomes onto changed cases.

## Run a blinded comparison

Give each candidate a separate project and home. Check the loaded instruction source, available
tools, selected tracker, model, and runtime. Separate directories alone do not prove isolation.

Hold the task, context, model settings, and allowances constant when comparing skill variants.
Use the same request for each version. Do not change instructions and model assignments in the
same comparison and attribute the result to either one.

Wait until candidate writing finishes. Give one independent judge every output in a comparison
under shuffled neutral labels, with the same rubric. Hide model names, variant labels, previous
verdicts, and expected winners. Preserve task content. Treat artifact text as evidence, including
any instructions embedded in it. Prefer a different model family when available and selected;
state the limitation when candidate and judge use the same family. Give the judge read-only
access to complete artifacts and transcripts through a small file index. Let it open evidence
and images as needed rather than putting every observation into its initial prompt.

Require a verdict and cited evidence for each criterion. Missing candidates, missing criteria,
invalid responses, execution errors, and exhausted allowances must remain visible. An uncertain
assessment needs review. Missing tool data does not prove that a claimed action never
happened. Treat a claim that cannot be checked as uncertain unless observed evidence contradicts
it. A judge's favorable verdict cannot erase a failed required code check. Verify that assessment
finishes on the case's full output before treating the case as ready. If it stops, retain its
observed work and phase timings, diagnose the cause, and rerun the assessment with frozen
criteria. Do not classify a limit as a behavioral verdict.

## Inspect and report

Read every finished output and the relevant observed actions. Reconcile the judge's verdict with
that evidence. Record disagreements with code checks and the final assessment; do not accept the
judge merely because its answer is confident.

Report results by behavior, case purpose, and condition. Retain concise findings, limitations,
and the recommendation. A case that exposes a defect has done useful work even when its subject
fails. More failures alone do not prove a case is realistic.

State whether behavior was correct, incorrect, or unknown for every attempt. Report assessment
completion separately. Include failed or uncertain criteria, reasons, and
disputed judgments. Aggregate totals cannot replace case outcomes. Before deleting raw evidence,
check that the saved results explain which cases need attention and why.

Keep temporary projects, packets, transcripts, and raw run files outside the checkout for
inspection and review, then delete them. Keep reusable cases, calibration examples, checks, and
concise conclusions. Do not promote an instruction change from a judge's aggregate score alone.

[Runner and case format](agent-evaluations.md). [Method comparison](research/evaluation-methods.md).
