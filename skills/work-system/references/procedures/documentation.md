# Documentation Procedure

Bring repository documentation up to date with the completed work. This required procedure may
conclude that no documentation change is needed.

## Decide the impact

Compare the accepted intent and completed behavior with existing documentation and any active work
record. Update documentation when the work changes information that a future developer,
operator, or consumer must know, such as an interface, command, configuration, workflow, domain
term, or accepted architectural reason.

Do not document temporary process, narrate the diff, restate code, or create an artifact merely
because files changed. If the completed behavior conflicts with an accepted specification,
domain term, or architecture decision, report the conflict. Do not rewrite accepted documentation to
justify the implementation.

## Update canonical knowledge

- Edit the existing canonical source when one exists. If information needs to be kept and no
  existing document fits, create the smallest document that serves that purpose.
- Keep each meaning in one place and link related records instead of copying their content.
- Keep domain glossaries free of implementation detail and preserve the reasoning of superseded
  architecture decisions.
- When a work record exists, update its ticket status, completion evidence, progress, and frontier.
  Keep it an index by linking specifications, decisions, research, and prototypes rather than
  duplicating them.
- Match the artifact's audience. Do not leak implementation considerations into consumer-facing
  prose.

Check changed links, names, commands, and examples against the completed behavior. This check
covers the documentation changes; it does not repeat implementation validation.

## Result

State whether documentation needed changes, which canonical records changed, and any work-record
updates. If nothing changed, explain why the existing documentation is sufficient. Include any
decision or behavior gap that prevents an accurate update.
