# Reusable project operating documentation

## Problem Statement

Project-specific setup and application operations must be usable across tasks without
repeated investigation. Existing workflow guidance establishes validation standards and
documentation upkeep, but lacks a detailed operating-document authoring reference.

## Solution

Keep operating instructions in existing project documentation, linked from the project
record. Add optional authoring guidance using the navigator's existing format mechanism.

## User Stories

1. As a developer or agent, I want reliable operating instructions so I can use an application
   without rediscovering its setup, interactions, observations, and cleanup.

## Implementation Decisions

Use the approved project-operations reference and documentation addition. Expose the reference
in fix, tweak, and novel-work implementation and through delivery's documentation procedure.
Project context directs agents to relevant linked operating instructions. Reuse existing
scripts and docs. Executable helper changes follow implementation; additional execution uses
validation. Preserve existing validation requirements and evidence retention.

## Testing Decisions

Check navigator authorization and registration, existing workflow/project-context tests, lint,
formatting, and strict typing. Behavioral cases cover useful operating-document creation,
fresh-agent consumption, maintenance, adequate-existing-doc controls, and incomplete prerequisites.
Inspect actual documents, execution, isolation, cleanup, and judgments. Calibrate semantic grading
with independently authored valid, invalid, and uncertain examples.

## Out of Scope

Project-local skill packaging, a separate verification procedure, validation rewrites,
automatic full-project audits, deployment, and publication.

## Further Notes

The accepted source is the approved project-operations diff in this conversation. Adapted
operating-document mechanics originate in pstack's create/maintain-verification-skill sources.
