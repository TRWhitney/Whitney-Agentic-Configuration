---
name: note-system
description: Route Obsidian knowledge-vault questions and work requests through stateful workflows
  with state-authorized guidance. Use whenever I ask a question or request knowledge work in an
  Obsidian vault.
---

# Note System

Route each Obsidian knowledge-vault prompt through one workflow while loading only the guidance
authorized for its current state.

## Glossary

I, me, my, you, your, user, and agent retain their established meanings.

## Route the prompt

1. Keep the active workflow until it completes or I replace or cancel it. Treat my feedback
   and related questions as part of that workflow.
2. When no workflow is active, classify my prompt by intent, uncertainty, and scope:
   - **Question**: I ask for information or discussion.
   - **Curate**: I request knowledge integration, organization, connection, or maintenance without
     introducing a new source that must be preserved.
   - **Ingest**: I provide or identify a new source to preserve and integrate into the vault.
3. Ask one clarifying question when its answer would establish whether the work introduces a new
   source that must be preserved. Otherwise preserve the source before changing vault knowledge
   rather than inventing consequential decisions.
4. Switch to `ingest` when later evidence shows that the work introduces a source that must be
   preserved.

## Navigate

Use `scripts/navigate.py` for all state, procedure, and format navigation. Do not open workflow
manifests or resolve resource files directly.

Run the script with Python and the path relative to this `SKILL.md`:

```text
python3 <skill-directory>/scripts/navigate.py start <workflow>
python3 <skill-directory>/scripts/navigate.py resume <workflow> <state>
python3 <skill-directory>/scripts/navigate.py move <workflow> <state> <destination>
```

Use `question`, `curate`, or `ingest` as the workflow.

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

Keep findings needed for continuation in conversation. Report blockers and decisions that need
my input when they arise.

Move only along a route displayed by the navigator, after meeting the conditions in the active
state's `Continue` section. If new evidence invalidates earlier work, record what changed and
return to the earliest state responsible for resolving it. Preserve valid work and repeat checks
whose evidence may have changed.

Complete the workflow only when the active state permits completion and its required evidence
remains valid. Give one final response covering the outcome, direct proof, material findings, and
unresolved decisions. Link durable artifacts instead of copying them and omit internal detail
that does not affect the outcome. Then clear the active workflow.

## Track state

- Keep question, curate, and ingest state in conversation. Do not create a vault record for these
  workflows. When one must continue in a fresh context, preserve its exact resume command, vault
  root, current question or requested outcome, decisive evidence and procedure results, owned
  temporary paths, and next action in the continuation context.
- Do not add workflow status to the prose of vault notes.
