---
name: note-system
description: Route questions and knowledge work on content in an Obsidian vault through stateful
  workflows. Use work-system for code-repository work, including changes to this skill.
---

# Note System

Use one workflow per Obsidian vault request. Load only the instructions available in its current
state.

## Glossary

I, me, my, you, your, user, and agent have their meanings from my global instructions.

## Evidence retention

Keep conclusions and reusable checks. Generate research and preparation outputs in temporary
directories outside the vault or checkout. Keep them for required inspection and review, then
delete them before delivery unless I explicitly request them. Requested source notes, source
transcripts, and selected attachments belong in the vault. Agent session transcripts and bulk
preparation outputs do not. Include these rules in delegated assignments.

## Route the prompt

1. Keep the active workflow until it completes or I replace or cancel it. Treat my feedback and
   related questions as part of that workflow.
2. When no workflow is active, classify my prompt by intent, uncertainty, and scope:
   - **Question**: I ask for information or discussion.
   - **Curate**: I request knowledge integration, organization, connection, or maintenance
     without introducing a new source that needs its own source note.
   - **Ingest**: I provide or identify a new source to save as a source note and use in the
     vault.
3. Treat creating, correcting, consolidating, and relinking definition notes as Curate work
   unless the request introduces an external source that first needs its own source note.
4. Ask one clarifying question when its answer would establish whether the work introduces a new
   source that needs its own source note. Otherwise use `ingest` and save the source note before
   changing knowledge notes rather than guessing.
5. Switch to `ingest` when later evidence shows that the work introduces a source that must be
   saved in a source note.

## Navigate

Use `scripts/navigate.py` to load states, procedures, and formats. Do not read workflow
manifests or their referenced instructions directly.

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
state or another authorized procedure. Do not construct a procedure command independently.
Return to the active state after completing it. The output for each state and procedure lists
any associated formats; load them only through the displayed navigator command.

## Procedure results and transitions

Loading a procedure does not change the active state. Use its result to continue that state's
work. Run `resume` again only when the state guidance is missing from context.

Keep findings needed for continuation in conversation. Report blockers and decisions that need
my input when they arise.

Move only along a route displayed by the navigator, after meeting the conditions in the active
state's `Continue` section. If new findings show earlier work is wrong, record what changed and
return to the first state that can correct it. Keep work that is still correct and rerun
affected checks.

Complete the workflow only when the active state permits completion and its required evidence
still matches the completed work. Give one final response covering the result, direct proof,
findings, and unresolved decisions. Link saved notes or attachments instead of copying them.
Omit internal details that do not affect the result. Then clear the active workflow.

## Track state

- Keep question, curate, and ingest state in conversation. Do not create a vault record for
  these workflows. For a fresh context, include the exact resume command, vault root, question
  or requested result, key findings and procedure results, this task's temporary paths, and next
  action in the handoff.
- Do not add workflow status to the prose of vault notes.
