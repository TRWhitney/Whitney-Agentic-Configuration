---
name: work-system
description: Route repository questions and work requests through stateful workflows with
  state-authorized guidance. Use whenever I ask a question or request work in a code repository.
---

# Work System

Route each repository prompt through one workflow while loading only the guidance authorized
for its current state.

## Glossary

I, me, my, you, your, user, and agent retain their established meanings.

## Route spawned implementation subagents

Apply this section only when system or developer instructions identify you as a spawned subagent
whose current assignment authorizes repository changes. It does not apply to the primary agent,
including when I ask the primary agent to delegate work.

- Use the exact navigator command supplied with the assignment.
- When that command or the assignment boundary is missing, report the missing context.

## Route the prompt

1. Keep the active workflow until it completes or I replace or cancel it. Treat my feedback
   and related questions as part of that workflow.
2. When no workflow is active, classify my prompt by intent, uncertainty, and scope:
   - **Question**: I ask for information or discussion.
   - **Tweak**: I request bounded repository work with a clear outcome and no unresolved
     consequential decision.
   - **Fix**: I report that existing intended behavior is broken. Diagnose the reported
     behavior before implementation.
   - **Novel work**: I request substantial capability or work with unresolved product, UX,
     data, or architecture decisions.
3. Ask one clarifying question when its answer would establish whether bounded work qualifies as a
   tweak or fix. Otherwise choose novel work rather than inventing consequential decisions.
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

Use `question`, `tweak`, `fix`, or `novel-work` as standard workflows. Use
`subagent-implementation` only under the spawned-implementation-subagent rule.

Enter a workflow with `start`. Every active state displays its exact resume command. In a fresh
context, use that command before loading a procedure. The navigator returns the active state and
the procedures related to it:

- **Allowed**: Load when it would help perform the state's work.
- **Triggered**: Load when its displayed cue applies.
- **Required**: The navigator loads it with the state. Complete it before leaving the state.

Load an allowed or triggered procedure only through an exact command displayed by the active
state or another authorized procedure. Do not construct a procedure command independently. Return
to the active state after completing it. The output for each state and procedure lists any
associated formats; load them only through the displayed navigator command.

## Procedure results and transitions

Loading a procedure does not change the active state. Use its result to continue that state's
work. Run `resume` again only when the state guidance is missing from context.

Keep findings needed for continuation in conversation and, when one exists, the durable work
record. Report blockers and decisions that need my input when they arise.

Move only along a route displayed by the navigator, after meeting the conditions in the active
state's `Continue` section. If new evidence invalidates earlier work, record what changed and
return to the earliest state responsible for resolving it. Preserve valid work and repeat checks
whose evidence may have changed.

Complete the workflow only when the active state permits completion and its required evidence
remains valid. Give one final response covering the outcome, proof, material findings,
documentation impact, commits, and unresolved issues. Omit categories that do not apply and link
durable artifacts instead of copying them. Then clear the active workflow.

## Track state

- Keep question, tweak, and fix state in conversation. Do not create a repository record for these
  workflows. When one must continue in a fresh context, preserve its exact resume command, current
  question or acceptance checks, decisive evidence and procedure results, owned uncommitted paths,
  and next action in the continuation context.
- Follow any workflow-record guidance returned by the navigator. When a durable record exists,
  keep the exact resume command, accepted decisions, invalidated evidence, and next transition
  current. Link source artifacts instead of copying them.
