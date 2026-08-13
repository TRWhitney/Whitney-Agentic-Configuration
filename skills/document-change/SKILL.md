---
name: document-change
description: Use when production behavior, interfaces, architecture, terminology, or accepted intent may require durable documentation changes; do not use for active prototype iteration.
---

# Document Change

Perform a documentation-impact pass and update only knowledge that future work must rely on.

Do not invoke this skill during active prototype iteration. `$prototype-decision` owns settlement and preservation until the prototype is accepted or abandoned.

## Assess impact

Inspect the change, accepted decisions, repository documentation conventions, and applicable instructions. Classify each impact using [durable-knowledge.md](references/durable-knowledge.md):

- changed user or operator behavior;
- changed public interface or workflow;
- an architecture decision that constrains future changes;
- a new or sharpened domain term;
- an accepted prototype or specification that must remain traceable;
- non-obvious code reasoning that belongs close to the constraint.

Record "no documentation impact" when none applies so the pass is explicit.

## Update the source of truth

- Update existing documentation at its established location.
- Create an ADR automatically when a consequential architecture decision and its tradeoff must constrain later work.
- Create or update the domain glossary automatically when shared terminology changes.
- Preserve specifications, accepted prototype contracts, and verification evidence in the active durable work record.
- Add code comments only for reasoning or constraints the code cannot express clearly.
- Ask permission before adding or changing a README, LICENSE, vendor-specific infrastructure, or `AGENTS.md` unless the user directly requested it.

Avoid a progress diary, duplicated explanations, generated file catalogs, speculative future documentation, and descriptions recoverable cheaply from code or configuration.

## Validate

Check relative links, terminology consistency, factual alignment with the implemented behavior, and repository formatting. Ensure each meaning has one canonical home and other artifacts point to it.

## Completion

Complete when every qualifying durable impact is updated or explicitly ruled out, protected files remain untouched without permission, references resolve, and documentation describes accepted behavior rather than implementation progress.
