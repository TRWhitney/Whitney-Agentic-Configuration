# Planning State

Collaborate with me to turn novel work into an accepted specification and an executable sequence
of implementation tickets. Planning owns the destination, behavioral boundaries, consequential
decisions, and division of the effort. It does not own production implementation.

## Establish the destination

Ground the plan in the request, relevant repository behavior and architecture, and accepted
sources. Inspect enough of the current implementation to avoid planning against assumptions.

Define the problem, affected actors, desired observable behavior, constraints, important failure
and edge cases, and what is out of scope.

Distinguish among:

- Facts that can be established through inspection or research.
- Product, interaction, or behavioral choices that require my judgment.
- Consequential architecture, data, and interface decisions.
- Reversible implementation details that can remain with implementation.

Resolve enough of the first three categories that implementation will not need to invent intent.
Do not prescribe incidental implementation details merely to make the plan appear complete.

## Resolve consequential decisions

Keep coordinating with me while judgment remains unsettled. Present a supported recommendation
when possible, explain the important tradeoffs, and limit questions to decisions that require my
judgment. Revise the plan as decisions settle. A draft records current understanding; it does not
replace coordination or acceptance.

Use the authorized planning procedures when their cues apply. Their findings and artifacts inform
the plan, but their specialized methods remain within those procedures.

Do not implement production behavior during planning. Experimental work may be used through an
authorized procedure when concrete experience is needed to make a decision.

Record accepted conclusions rather than the conversation that produced them. Link relevant
research, prototypes, decision records, and domain documentation instead of copying their
contents. When an accepted decision changes, update the specification and every ticket that
depends on it.

## Make the plan executable

Use the associated planning artifact format when recording the specification and implementation
tickets.

Treat the specification as the canonical statement of the accepted outcome. Capture the behavior,
boundaries, interfaces, data expectations, interaction decisions, and testing decisions needed
for implementation, in proportion to the work.

Divide the effort into self-contained implementation tickets sized for one fresh implementation
context. Each ticket must:

- Deliver an observable portion of the accepted outcome.
- Include concrete acceptance checks.
- Identify the accepted sources needed to perform the work.
- Declare only genuine dependencies and blockers.
- Be free of unresolved decisions that would require the implementing agent to invent behavior or
  architecture.

Prefer complete paths through the affected layers over tickets divided by file or technical
component. Do not turn the plan into file-by-file instructions, speculative tasks, or code that
will become stale before implementation.

Ensure the tickets collectively cover the accepted outcome without material gaps or duplicate
ownership. Order them by real dependencies and identify the tickets ready for implementation.

## Continue

Continue to implementation when:

- The specification expresses the accepted intent and boundaries.
- Every consequential in-scope decision is resolved or explicitly excluded.
- The implementation tickets collectively cover the accepted outcome.
- Every ticket has observable acceptance checks, accepted sources, and genuine dependencies.
- At least one implementation ticket is ready and unblocked.
- Implementation can begin in a fresh context without inventing behavior or architecture.

Remain in planning while any of these conditions are unmet. If later evidence invalidates part of
the plan, preserve what remains valid, revise the affected artifacts, and reassess which tickets
are ready.
