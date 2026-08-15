# Wayfinding Procedure

Turn a large or foggy outcome into settled intent through a visible decision map. Plan decisions,
not production work. Use the associated wayfinding format for the map and decision tickets.

## Establish the destination

State the destination in one or two observable sentences that make clear where the effort ends.
Record explicit exclusions under `Out of scope`. Keep uncertain but potentially relevant terrain
under `Not yet specified` until it can be expressed as a precise question.

Create decision tickets only for questions that can be stated precisely. Give each ticket its
settlement type and genuine blockers. Do not enumerate speculative questions merely to make the
fog look complete.

## Work the frontier

The frontier consists of precise, open, unblocked, and unclaimed decision tickets. Claim one
before working it. During coordination, use a compact status line:

`Wayfinding · <n> resolved · <n> visible · fog: <themes or none>`

Name the current decision and why it gates progress. Present only the evidence and tradeoffs
needed to decide it, recommend an answer with the decisive reason, and ask one primary question.
Group two or three tightly coupled questions when they rely on the same evidence and answering
them together is clearer. Do not serialize questions that I can answer reliably together.

Do not paste the decision map into conversation or repeat a full recap after every answer. Give a
larger recap when the destination or remaining route materially changes. Do not estimate a
completion percentage or fixed question count because one answer can expose or remove terrain.

Resolve factual uncertainty through research and questions that benefit from concrete reaction
through a prototype. A `task` is a prerequisite action needed to answer a decision, never
production implementation. Do not resolve a choice that requires my judgment. When research is
in progress, advance an unrelated frontier decision when one is available.

## Update the record

After each answer, record the resolution and supporting evidence once in its decision ticket,
mark it resolved, and add only a linked one-line conclusion to the map. Recompute the frontier and
remaining fog. Promote fog to a ticket only when its question becomes precise, and update or remove
tickets invalidated by the resolution.

Link research, accepted prototypes, and other evidence instead of copying them. When a resolution
establishes durable domain terminology or an architecture decision, use domain modeling to record
the canonical knowledge and link it from the decision ticket.

Keep the map an index rather than a transcript or specification. Decision tickets resolve intent
and must not become production implementation tickets. Wayfinding is complete when the destination
is specific, every consequential decision is resolved, no in-scope fog remains, and a fresh
context could produce the specification and implementation tickets without inventing intent.

## Result

Include the destination, resolved-decision links, explicit exclusions, remaining fog, and visible
frontier. When wayfinding is complete, report zero visible decisions and no remaining in-scope
fog.
