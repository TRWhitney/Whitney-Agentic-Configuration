# 06 Workflow model and approval loop

**Status:** resolved
**Blocked by:** none
**Type:** architecture

## Question

How should the draft's archive, curation, approval, and completion responsibilities become a
stateful process without forcing every vault request through source ingestion?

## Answer

Expose three workflows through one discoverable `note-system` skill:

- `question` for read-only questions about vault knowledge;
- `curate` for knowledge-note integration, curation, and structural maintenance without a new
  source;
- `ingest` for source acquisition, vault discovery, source preservation, and knowledge integration,
  beginning with YouTube.

Use shared `discovery`, `integration`, `review`, and `answer` states, plus an `acquisition` state
owned only by source ingestion. Acquisition runs first for ingestion and prepares source evidence
without writing to the vault. Discovery remains source-agnostic and establishes the vault, current
conventions, relevant capabilities, and conceptual neighborhood for every workflow. During
ingestion, integration creates the faithful source record before performing safe concept-centered
changes and collecting material judgments. Review validates the work, removes temporary artifacts
after success, and presents the terse change log and decision queue.

Review may return to integration after I resolve a queued decision or when the source record has a
defect. Missing or unsuitable source evidence returns ingestion to acquisition. Safe work should
complete before either transition is needed.

Keep workflow state conversational. Media preparation uses an explicit temporary workspace whose
path is reported when work fails and which is removed after successful review; do not add workflow
status to vault notes or maintain a permanent vault-local process database.

## Evidence

The original expanded draft distinguished source archiving from knowledge curation, permitted
low-risk additive work without interruption, reserved material changes for approval, and required
a concise completion report. It was removed from the repository root after decomposition. I asked
for a process similar to `work-system`; the separate instruction about plugin development governed
the repository task rather than the resulting skill's runtime behavior.
