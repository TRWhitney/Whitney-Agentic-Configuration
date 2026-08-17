# 01 Core note-system process

**What to build:** A discoverable, stateful skill that answers vault questions read-only and safely
curates an Obsidian concept network through live convention discovery, integration, review, and a
batched approval loop.

**Blocked by:** none

**Status:** complete

- [x] `note-system` is implicitly discoverable beside `work-system`, while its internal references
  are not independently discoverable.
- [x] The public navigator routes `question`, `curate`, and the non-source-specific portions of
  `ingest` through valid state transitions and is the sole source of exact
  resume/procedure/format commands.
- [x] Active guidance preserves the draft's source/archive distinction, concept-centered
  integration, provenance, disagreement, uncertainty, note structure, approval boundaries, and
  terse completion contract without loading every procedure at once.
- [x] Discovery accounts for Agent Client's actual boundary and finds only relevant live vault
  conventions/capabilities without persistent inventory or add-on mutation.
- [x] Discovery, Acquisition, and Integration allow a bounded research procedure when ordinary
  inspection leaves a factual question whose answer would materially improve the active work,
  without chained research delegation or unauthorized vault writes.
- [x] Asking a question does not authorize vault writes, and repository-only implementation
  constraints are not encoded as runtime guidance.
- [x] Focused structure, metadata, link, manifest, navigation, formatting, lint, and typing checks
  pass.

## Accepted sources

- [Specification](../spec.md)
- [Process boundary](../decisions/01-process-boundary.md)
- [Source record](../decisions/02-source-record.md)
- [Vault discovery](../decisions/05-vault-capabilities.md)
- [Workflow model](../decisions/06-workflow-model.md)
- [Agent Client research](../research/agent-client-capabilities.md)
- [`work-system`](../../../skills/work-system/SKILL.md)

## Completion evidence

- Focused note-system structure, manifest, metadata, link, and navigator tests pass.
- Skill-creator validation reports `Skill is valid!`.
- Direct navigator runs load the expected ingestion discovery and acquisition boundaries.
- Fresh intent and engineering delivery reviews passed with no findings after corrections.
