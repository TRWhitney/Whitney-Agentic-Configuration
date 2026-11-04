---
name: work-system
description: Handle repository questions and work through workflows that load instructions
  for each step. Use whenever I ask a question or request work in a code repository.
---

# Work System

Use one workflow per repository request. Load only the instructions available in its current
state.

## Glossary

I, me, my, you, your, user, and agent have their meanings from my global instructions.

## Evidence retention

Keep conclusions and reusable code or checks. Generate raw outputs in temporary directories
outside the checkout. Keep them for required inspection and review, then delete them before
delivery. Do not save captures or full run histories for later replay unless I explicitly
request it. Include these rules in delegated assignments.

Before replying, update the existing report or work record with conclusions and remove each raw
capture whose diagnosis, inspection, and required review are finished. Supplied trial captures
are raw outputs. Preserve original source data and reusable checks. Keep retained captures
outside the checkout and out of Git.

## Route spawned implementation subagents

Apply this section only when system or developer instructions identify you as a spawned subagent
whose current assignment authorizes repository changes. It does not apply to the primary agent,
including when I ask the primary agent to delegate work.

- Use the exact navigator command supplied with the assignment.
- If the command or permitted scope is missing, report what you need.

## Route the prompt

1. Keep the active workflow until it completes or I replace or cancel it. Treat my feedback and
   related questions as part of that workflow.
2. When no workflow is active, classify my prompt by intent, uncertainty, and scope:
   - **Question**: I ask for information or discussion.
   - **Tweak**: I request limited repository work with a clear result and no open product or
     architecture decision.
   - **Fix**: I report that existing intended behavior is broken. Diagnose the reported behavior
     before implementation.
   - **Novel work**: I request substantial capability or work with unresolved product, UX, data,
     or architecture decisions.
3. Ask one clarifying question when it would show whether the work fits a tweak or fix. Otherwise
   choose novel work rather than guessing at decisions that affect the requirements or scope.
4. Switch a tweak or fix to novel work when later evidence shows that its scope or uncertainty
   no longer fits the bounded workflow.

## Restore

The saved workflow state records which workflow and state this conversation is in.
It also stores the substate and work-record link when present.

After context compaction, run:

```text
python3 <skill-directory>/scripts/navigate.py resume
```

The navigator restores this conversation's saved workflow state. Read its linked work record before
continuing when one is saved. If there is no active workflow, route the prompt. Named-location
resume loads guidance without changing the saved workflow state.

If the saved workflow state is damaged, leave its file unchanged, report the error, and stop that
conversation's workflow.

## Navigate

Use `scripts/navigate.py` to load states, procedures, and formats. Do not read workflow
manifests or their referenced instructions directly, except to answer a question about another
tracker. For that question, read its guidance under `references/providers/<tracker>/` and
explain its record locations and delivery requirements. Keep the selected tracker unchanged.

Run the script with Python and the path relative to this `SKILL.md`:

```text
python3 <skill-directory>/scripts/navigate.py start <workflow>
python3 <skill-directory>/scripts/navigate.py resume <workflow> <state>
python3 <skill-directory>/scripts/navigate.py move <workflow> <state> <destination>
```

Use `question`, `tweak`, `fix`, or `novel-work` as standard workflows. Use
`subagent-implementation` only under the spawned-implementation-subagent rule.

Enter a workflow with `start`. Use `--record <path-or-url>` to link its work record. Workflow state is
saved separately for each conversation. Use `cancel` when the workflow is cancelled.
The navigator uses `CODEX_THREAD_ID` to identify the conversation. If it is unavailable, supply
`--conversation <id>`; displayed continuation commands keep that argument. The navigator returns
the active state and the procedures related to it:

- **Allowed**: Load when it would help perform the state's work.
- **Triggered**: Load when its displayed cue applies.
- **Required**: The navigator loads it with the state. Complete it before leaving the state.

Load an allowed or triggered procedure only through an exact command displayed by the active
state or another authorized procedure. Do not construct a procedure command independently.
Return with the displayed resume command after completing a procedure. The output for each
state and procedure lists any associated formats; load them only through the displayed
navigator command.

## Procedure results and transitions

Loading a procedure does not change the active state or substate. Use its result to continue
that state's work.

A state may offer optional substates. Enter one with its displayed command when it would help.
It remains active across discussion and temporary procedures until its result is complete or I
cancel it. Resume restores its guidance and formats. Leave it with the displayed command before
moving to another state.

Keep findings needed for the next step in conversation and in the work record when one exists.
Report blockers and decisions that need my input when they arise.

Move only along a route displayed by the navigator, after meeting the conditions in the active
state's `Continue` section. If new findings show earlier work is wrong, record what changed and
return to the first state that can correct it. Keep work that is still correct and rerun
affected checks.

Complete the workflow only when the active state permits completion and its required evidence
still matches the completed work. Give one final response covering the result, proof, findings,
documentation impact, commits, and unresolved issues. Omit categories that do not apply and link
saved documents or code instead of copying them. Then use the displayed completion route to
remove its saved workflow state.

## Track state

The navigator stores the saved workflow state under
`<Codex home>/work-system/state/`, using `CODEX_HOME` or `.codex` under the home directory. Keep the
current question, accepted sources, findings, this task's uncommitted paths, and next action in
the work record when one is required, or in conversation otherwise. Follow the work-record
guidance returned by the navigator. Update its resume command, agreed decisions, checks that
need rerunning, and next step. Link sources instead of copying them.
