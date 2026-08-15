---
name: work-system
description: Use when working in a code repository and I ask a question or request work.
---

# Work System

Route each repository prompt through one workflow while loading only the guidance authorized
for its current state.

## Glossary

I, me, my, you, your, user, and agent retain their established meanings.

- **Prompt**: Anything I communicate, including a question, work request, feedback, or
  clarification.
- **Workflow**: The sequence selected to handle my prompt.
- **State**: The active stage of a workflow.
- **Procedure**: Reusable guidance that may be loaded only when the active state authorizes it.
- **Procedure result**: The evidence, artifacts, decisions, or blockers a procedure gives back to
  the active state.
- **Transition**: Movement the agent requests after meeting continuation criteria.
- **Continuation criteria**: The conditions that must be satisfied before leaving a state.
- **Null state**: The condition in which no workflow is active.

## Route the prompt

1. Keep the active workflow until it completes or I replace or cancel it. Treat my feedback
   and related questions as part of that workflow.
2. In the null state, classify my prompt by intent, uncertainty, and scope:
   - **Question**: I ask for information or discussion.
   - **Tweak**: I request bounded repository work with a clear outcome and no unresolved
     consequential decision.
   - **Fix**: I report that existing intended behavior is broken. Diagnose the reported
     behavior before implementation.
   - **Novel work**: I request substantial capability or work with unresolved product, UX,
     data, or architecture decisions.
3. Ask one clarifying question when its answer would establish that bounded work is a tweak or fix.
   Otherwise choose novel work rather than inventing consequential decisions.
4. Switch a tweak or fix to novel work when later evidence shows that its scope or uncertainty no
   longer fits the bounded workflow.

## Navigate

Use `scripts/navigate.py` for all state, procedure, and format navigation. Do not open workflow
manifests or resolve resource files directly.

Run the script with Python and the path relative to this `SKILL.md`:

```text
python3 <skill-directory>/scripts/navigate.py start <workflow>
python3 <skill-directory>/scripts/navigate.py resume <workflow> <state>
python3 <skill-directory>/scripts/navigate.py move <workflow> <state> <destination>
```

Use `question`, `tweak`, `fix`, or `novel-work` as the workflow.

Enter a workflow with `start`. Every active state displays its exact resume command. In a fresh
context, use that command before loading a procedure. The navigator returns the active state and
the procedures related to it:

- **Allowed**: Load when it would help perform the state's work.
- **Triggered**: Load when its displayed cue applies.
- **Required**: The navigator loads it with the state. Complete it before leaving the state.

Load an allowed or triggered procedure only through an exact command displayed by the active
state or another authorized procedure. Do not construct a procedure command independently. Return
to the active state after completing it. State and procedure output lists any associated formats;
load them only through the displayed navigator command.

## Handle procedure results

A procedure result belongs to the active state. Use it to continue the state's work; the result
does not select another state or require a standalone completion response.

- Keep conversational results available until the workflow completes. Record results needed for
  continuation in the durable work record when one exists.
- Tell me immediately when a result requires my decision or prevents meaningful progress. Do not
  defer a blocker until workflow completion.
- When the workflow completes, give me one final response summarizing the overall outcome, direct
  proof, material procedure results, documentation impact, commits, and unresolved issues. Link
  durable artifacts instead of copying them, and omit internal detail that does not affect the
  outcome.

## Track state

- Keep question, tweak, and fix state in conversation. Do not create a repository record for these
  workflows. When one must continue in a fresh context, preserve its exact resume command, current
  question or acceptance checks, decisive evidence and procedure results, owned uncommitted paths,
  and next action in the continuation context.
- Follow any workflow-record guidance returned by the navigator. When a durable record exists,
  keep the exact resume command, accepted decisions, invalidated evidence, and next transition
  current. Link source artifacts instead of copying them.

## Transition

Leave a state only when its continuation criteria are satisfied. Choose the appropriate
destination from the routes returned by the navigator, then use its `move` command. When a state
reveals an earlier problem:

1. Record the problem and the evidence or assumption it invalidates.
2. Use the navigator to return to the earliest state responsible for resolving it.
3. Preserve accepted work that remains valid.
4. Repeat every later check whose evidence may have changed.

## Completion

Complete the workflow when the active state permits movement to `complete` and all required
evidence remains valid. Report it according to the procedure-result convention, then return to
the null state.
