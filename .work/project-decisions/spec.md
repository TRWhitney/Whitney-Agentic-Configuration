# Project agreements throughout work-system

## Problem Statement

Work-system restores an effort and its tickets but has no separate reference for decisions that
apply across a project. Planning records can introduce platform commitments, release requirements
or versioning choices without distinguishing them from implementation work. Feature-only planning
records also lack a clear place for project-wide questions.

## Solution

Give repository work a shared project record at `docs/project.md`. Link existing detailed
documentation instead of duplicating its requirements. Keep release plans optional and
link them only when relevant. Existing effort records continue to hold effort specifications,
feature planning and implementation tickets.

Establish and revise project agreements within the existing planning workflow. Discovery,
resumption, delegated work, implementation, validation, review and delivery use the same accepted
sources. Decisions may remain open until needed, and agreed decisions may change through
discussion. Only affected work waits for an unresolved decision.

## User Stories

1. As the person directing a project, I want to decide its support commitments and release
   requirements before agents make them implementation work or dependencies.
2. As someone developing an unfinished application, I want useful work to proceed before a
   release plan, date, version number or versioning policy exists.
3. As someone changing a project decision, I want affected plans, tickets and checks updated
   together while completed work and valid evidence remain useful.
4. As an agent starting or resuming work, I want the current project agreements and effort
   record identified without reconstructing them from unrelated tickets.

## Implementation Decisions

### Shared records

The project record contains current agreed purpose, intended users, support commitments,
cross-feature constraints, versioning policy when chosen, and unresolved project questions.
Keep feature detail and architecture rationale in their existing records and link them. Mark
recommendations and questions distinctly from accepted decisions; available tools and test
machines establish technical facts, not product commitments.

Default release documents live under `docs/releases/`. A descriptive name can precede a chosen
version. A release document records its audience, selected work, supported environments, required
checks, chosen version and timing when agreed, and remaining questions. A project may have no
release documents. Versioning policy lives once in the project record; release documents link it.
Existing version metadata does not itself select a future release or compatibility policy.

### Lookup

Add a read-only `project` navigator command that identifies `docs/project.md`. Use that fixed
location across repositories, without a document-path setting or registration command.

Git tracker settings remain in the Git common directory. For non-Git work, preserve the existing
tracker settings in `.work/project.json`. Looking up the project document creates no files and
changes neither the selected tracker nor the conversation workflow.

Resolve the document against the current checkout root, including nested working directories
and worktrees. Report a missing record without treating the missing text as agreement. A missing
record does not by itself block a factual answer or otherwise specified routine fix.

Start and resume return shared project guidance and identify the project record beside the
current effort record, including a resume with no active workflow. The `project` command also
returns this guidance. Project contents remain in their source files rather than conversation
state. Existing hook recovery therefore restores current references. Relevant release links
remain in accepted sources in the effort record; the navigator does not choose a release.

### Planning and changes

Add a project-planning procedure and a shared project/release document format to novel-work
planning, also available during wayfinding. Use the procedure when establishing a project,
changing project commitments or planning a release. Reuse existing agreements and discuss only
material unresolved choices. Routine implementation judgment remains delegated as before.

Project and release questions live in their shared documents, linked from any decision map.
Feature questions remain grouped by feature. Implementation tickets follow agreed decisions;
they do not establish new support, release or versioning commitments by being created.

After an agreed change, update its source and affected effort specifications, tickets,
dependencies and acceptance checks before proceeding with dependent work. Preserve completed
work and evidence that remain valid. An unavailable environment cannot itself cancel an agreed
support requirement or count as passing validation.

### Workflow integration

Keep shared decision authority and record use in `references/project-agreements.md`, returned
by the navigator. The main skill documents the project lookup command and project
references returned during resume. Project planning is exposed through the navigator's existing
procedure list, with its cue and displayed invocation. Keep establishment/change steps and
document formats separate and discoverable
through navigator commands. Reconcile overlapping planning and wayfinding instructions rather
than adding a second feature-record convention.

Delegated assignments and independent reviews include applicable project and release sources.
Validation checks the agreed commitments. Delivery distinguishes the completed effort from
readiness of an agreed release and from permission to publish. No personal acceptance step or
release gate exists unless agreed for that work.

Local and GitHub effort tracking keep their existing ownership and publication rules. Shared
project/release documents are repository documentation, linked from tracking records rather than
copied into effort specifications or feature issues. Existing repository adoption reuses factual
and accepted sources, discusses conflicts, and removes duplicate current statements by linking
their shared source.

## Testing Decisions

Exercise the navigator through its CLI in temporary Git repositories, worktrees and non-Git
projects. Cover fixed-path lookup, nested paths, fresh checkouts, state preservation,
missing records, selected tracker preservation, start/resume, delegated
contexts and hook recovery. Assert observed references and unchanged state, not incidental prose.

Add ordinary task cases for project establishment, existing-project adoption, undecided platform
work, approved platform work, development before release planning, later versioning decisions,
and changed agreements. Include relevant existing planning, implementation, validation and native
recovery controls. Keep private criteria and checks out of candidate projects.

Establish a fresh baseline before guidance changes. Compare the complete integrated change
against the original source; do not attribute its effect solely to wording. During wording
iterations, keep code, tasks, criteria and model settings fixed. Use the existing gpt-6.1-sol
candidate and separate blinded judge setup, with three final attempts per case/control. Inspect
complete outputs and actions, report behavior separately from assessment completion, and retain
earlier failures and disputed judgments in a concise study.

Framework and quality checks cover the completed change; independent intent and engineering
review inspect the full work and available raw evidence before its cleanup.
