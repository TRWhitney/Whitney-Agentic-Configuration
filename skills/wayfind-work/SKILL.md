---
name: wayfind-work
description: Use when an outcome needs multiple contexts or has unresolved product, UX, data, or architecture decisions that prevent reliable planning.
---

# Wayfind Work

Turn a large or foggy outcome into settled intent through a visible, conversational decision map. Plan decisions, not production tasks.

## Ownership

Own the destination, decision frontier, remaining fog, and conversational alignment. Do not implement the destination. Delegate factual investigation to research and concrete design questions to `$prototype-decision`.

## Establish the destination

1. Load an existing effort through the active work adapter or ask `$manage-work` to create one.
2. State the destination in one or two observable sentences. The destination defines where this effort stops.
3. Record explicit exclusions as out of scope. Keep uncertain but potentially in-scope terrain as fog.
4. Identify only decisions that can be stated precisely now. These form the visible frontier. Read [decision-map.md](references/decision-map.md) for adapter-neutral fields and local serialization.

If the destination is already clear, no consequential decisions remain, and the work fits one context, return control to `$manage-work` for the tweak route.

## Converse through the frontier

Handle one primary question per user exchange. Keep each exchange small:

1. Show one status line using this shape:

   `Wayfinding · <n> decisions settled · <n> visible · fog: <themes or none>`

2. Name the current decision and why it gates progress.
3. Present only the evidence and tradeoffs needed to answer it.
4. Give a recommended answer and explain the decisive reason.
5. Ask the one primary question, then wait.

Do not paste the decision map into chat. Give a fuller recap only when the destination or remaining route materially changes. Never estimate a percentage or a fixed question count because resolving a decision can reveal or remove terrain.

Find environmental and documentary facts independently. If research is still running, advance any unrelated frontier decision. Never answer the user's side of a judgment question.

## Advance the map

After each answer:

1. Record the answer and rationale in one decision file.
2. Recompute the visible frontier and remaining fog.
3. Promote fog to a decision only when its question can be stated precisely.
4. Remove or close decisions that the answer places outside the destination.
5. Use `$prototype-decision` when reacting to a concrete artifact will resolve the decision more reliably than prose. An accepted prototype blocks planning until its acceptance contract is explicitly confirmed.

## Hand off automatically

When the destination is specific, all consequential decisions are settled, no in-scope fog remains, accepted prototypes are settled, and constraints and exclusions are recorded, return control to `$manage-work`. It advances automatically to `$plan-work`; do not require the user to request specification or work-item creation.

## Completion

Complete when another fresh agent could produce the plan without inventing a product, UX, data, or architecture decision. The final wayfinding status must report zero visible decisions and no remaining in-scope fog.
