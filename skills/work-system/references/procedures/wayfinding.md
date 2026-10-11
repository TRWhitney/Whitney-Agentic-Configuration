# Wayfinding procedure

Turn a large or foggy outcome into settled intent through a visible decision map. Plan decisions,
not production work. Use the associated wayfinding format for the map and decision records.

## Establish the destination

State the destination in one or two observable sentences that make clear where the effort ends.
For a broad outcome, establish the first useful deliverable and its acceptance boundary before
decomposing decisions. Keep later work visible as deferred scope without making it a planning gate.
Record explicit exclusions under `Out of scope`. Keep uncertain terrain under `Not yet specified`
only while it may affect this deliverable.

Group questions by distinct feature. Keep each feature's questions, research, subcontracts,
refinements, and accepted answers in one combined research-and-planning ticket. Create another
planning ticket only for another distinct feature under the provider's ownership rules. Questions,
technical concerns, and different evidence within a feature cannot receive their own planning
tickets. Identify how each feature's open questions will be settled and their genuine blockers.
Do not enumerate speculative questions merely to make the fog look complete.

## Work the frontier

The frontier consists of precise, unresolved, unblocked decisions that prevent specifying or
building the first deliverable. They may be sections of one design issue. Claim a separate ticket
before working it. During coordination, use a compact status line:

`Wayfinding · <n> resolved · <n> visible · fog: <themes or none>`

Name the current decision and why it gates progress. Present only the evidence and tradeoffs
needed to decide it, recommend an answer with the decisive reason, and ask one primary question.
Group tightly coupled questions when they rely on the same evidence and answering them together
is clearer. Do not serialize questions that I can answer reliably together. Asking them separately
does not require separate records.

Do not paste the decision map into conversation or repeat a full recap after every answer. Give a
larger recap when the destination or remaining route materially changes. Do not estimate a
completion percentage or fixed question count because one answer can expose or remove terrain.

Use research to resolve factual uncertainty and prototypes for questions that benefit from concrete
reactions. A `task` is a prerequisite action needed to answer a decision, never production
implementation. Use established conventions and judgment I have delegated for reversible details
within accepted behavior. Record the resulting contract in its owner without a separate approval
ticket. Do not resolve a choice that requires my judgment. When research is in progress, advance
an unrelated frontier decision when one is available.

## Update the record

After each answer, update the current contract and supporting evidence in its owning record.
Keep the feature's planning unresolved while any blocking question remains. When its planning is
settled, mark it resolved, synchronize native issue state under the provider's rules, and link the
conclusion from the map. Recompute the frontier and remaining fog. Promote fog to a question within its feature ticket
only when it is precise and blocks the deliverable. A new question gets a new planning ticket
only if it establishes another distinct feature.

When a contract settles and before a planning handoff, consolidate related refinements and
superseded records into their current owner. Preserve material accepted decisions, rationale, and
source links. Retire redundant records and update map links and blockers. Renesting issues or
closing settled questions without consolidating their content does not complete this pass.

Link research, accepted prototypes, and other evidence instead of copying them. When a resolution
establishes durable domain terminology or an architecture decision, use domain modeling to record
the canonical knowledge and link it from the owning record.

Keep the map an index rather than a transcript or specification. Decision records resolve intent
and must not become production implementation tickets. Wayfinding is complete when the deliverable
is specific, its consequential decisions are resolved, no blocking fog remains, and a fresh context
could produce its specification and implementation tickets without inventing intent. Deferred
decisions must not affect its acceptance boundary or be reported as resolved.

## Result

Include the destination, first deliverable, current contract links, explicit exclusions, deferred
concerns, remaining fog, and visible frontier. When wayfinding is complete, report zero blocking
decisions and no remaining fog for the deliverable.
