# Domain Documentation Formats

Add domain documentation when the project agrees on a term or decision worth recording.

## Single context

Use a root `CONTEXT.md` as a glossary:

```markdown
# <Context name>

<One or two sentences describing the context.>

## Language

**<Standard term>**:
<One- or two-sentence definition.>
_Avoid_: <misleading alternatives>
```

Include only project-specific domain concepts. Define what a term is without implementation
details. Prefer one standard term and group related terms only when useful.

## Multiple contexts

Use a root `CONTEXT-MAP.md` that links each context-local `CONTEXT.md` and briefly records the
relationships between contexts. Store system-wide architecture decisions in `docs/adr/` and
context-specific decisions beside that context under `docs/adr/`.

## Architecture decision

Name ADRs `docs/adr/<NNNN>-<slug>.md`, numbered after the highest existing entry:

```markdown
# <Short decision title>

<One to three sentences stating the context, accepted decision, and reason.>
```

Create an ADR only when the decision is costly to reverse, surprising without context, and the
result of a genuine tradeoff. Add `Status`, `Considered Options`, or `Consequences` only when
they explain something a future change needs. Mark an obsolete ADR as replaced and link the new
one without deleting its original reason.
