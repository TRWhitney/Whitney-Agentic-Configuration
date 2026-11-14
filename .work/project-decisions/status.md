# Project-wide planning decisions

## Destination

Shared platform, release and versioning commitments must reflect agreed project decisions before
agents turn them into implementation tickets. Release plans may wait until needed. Changes to
agreements update affected work while preserving completed work and useful evidence.

## Current state

Complete. The [specification](spec.md) and three tickets are implemented, validated and
independently reviewed. The [approved guidance](../../docs/research/project-decisions-proposal.diff)
is applied exactly as tested. Global installation and real GitHub publication were not performed.

## Progress

- [01 Navigator context](tickets/01-project-context.md): fixed `docs/project.md`, with no document-path
  setting or registration command. Start, resume, hooks and delegated workflows identify the same
  project source. Existing tracker settings remain intact.
- [02 Integrated guidance](tickets/02-project-planning.md): project planning is a navigator procedure
  with a shared record format. Main-skill additions concern navigation only. Existing detailed
  sources remain linked; shared commitments stay separate from feature requirements.
- [03 Behavioral evidence](tickets/03-behavioral-evidence.md): the
  [study](../../docs/research/project-decisions-trials.md) retains every condition's outcomes,
  earlier failures, four excluded attempts and the mechanical code-check correction.

## Accepted sources

- [Specification](spec.md) and [tested guidance](../../docs/research/project-decisions-proposal.diff).
- [Eval authoring](../../docs/eval-authoring.md) and [runner](../../docs/agent-evaluations.md).
- Pstack's existing [plan](https://github.com/backnotprop/pstack/blob/18e0e908a13553b0e58d065ab26dbc9a972ec8ba/skills/poteto-mode/references/plan.md),
  [orchestration](https://github.com/backnotprop/pstack/blob/18e0e908a13553b0e58d065ab26dbc9a972ec8ba/skills/poteto-mode/playbooks/orchestrate.md) and
  [autonomy principle](https://github.com/backnotprop/pstack/blob/18e0e908a13553b0e58d065ab26dbc9a972ec8ba/skills/principle-never-block-on-the-human/SKILL.md)
  informed this adaptation; it is not an existing pstack project-setup procedure.

## Verification

All 36 final attempts meet the selected criteria, three per case/control. All 120 comparable
candidate assessments and 120 final joint judgments complete and agree. Complete outputs,
relevant actions and available child findings were inspected. All final attempts have verified
instruction sources, definitions, model and isolation. Seven shared-record calibration examples
and three existing readiness examples agree. All 167 cases validate.

The exact final source passes 563 framework tests, lint and focused type checks. After application,
21 focused/structural checks, lint, type checks and direct project lookup pass. Independent intent
and engineering reviews pass with no blocking findings. The full behavioral corpus was not rerun.
An earlier ungraded GitHub ticket-claim omission is preserved in the study for separate follow-up.

Raw captures were kept outside Git through inspection and review, then deleted. Fresh comparisons
require fresh runs. The verifier-check repair is committed as `99387c3`; project-planning code,
guidance, tests and records are delivered together in the commit containing this record.
