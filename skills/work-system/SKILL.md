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

## Navigate

Use `scripts/navigate.py` to load states, procedures, and formats. Do not read workflow
manifests or their referenced instructions directly.

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
state or another authorized procedure. Do not construct a procedure command independently.
Return to the active state after completing it. The output for each state and procedure lists
any associated formats; load them only through the displayed navigator command.

## Procedure results and transitions

Loading a procedure does not change the active state. Use its result to continue that state's
work. Run `resume` again only when the state guidance is missing from context.

Keep findings needed for the next step in conversation and in the work record when one exists.
Report blockers and decisions that need my input when they arise.

Move only along a route displayed by the navigator, after meeting the conditions in the active
state's `Continue` section. If new findings show earlier work is wrong, record what changed and
return to the first state that can correct it. Keep work that is still correct and rerun
affected checks.

Complete the workflow only when the active state permits completion and its required evidence
still matches the completed work. Give one final response covering the result, proof, findings,
documentation impact, commits, and unresolved issues. Omit categories that do not apply and link
saved documents or code instead of copying them. Then clear the active workflow.

## Track state

- Keep workflow progress in conversation unless its work-record guidance requires a saved
  record. For a fresh context, include the exact resume command, question or acceptance checks,
  key findings and procedure results, this task's uncommitted paths, and next action in the
  handoff.
- Follow the work-record guidance returned by the navigator. Update its resume command, agreed
  decisions, checks that need rerunning, and next step. Link sources instead of copying them.
