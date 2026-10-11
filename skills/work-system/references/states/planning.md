# Planning State

Collaborate with me to turn novel work into an accepted specification and an executable sequence
of implementation tickets. Planning owns the destination, behavioral boundaries, consequential
decisions, and division of the effort. It does not own production implementation.

## Establish the destination

Ground the plan in the request, relevant repository behavior and architecture, and accepted
sources. Inspect enough of the current implementation to avoid planning against assumptions.

Define the problem, affected actors, desired observable behavior, constraints, important failure
and edge cases, and what is out of scope.

Use one combined research-and-planning ticket per distinct feature. Only a distinct feature can
receive its own research-and-planning ticket. Its questions, subcontracts, architecture concerns,
experiments, and accepted answers stay in that ticket through discussion, research, and planning.
A change of question, method, evidence, agent, or context does not create another planning ticket.
For example, named text-style syntax, defaults, inheritance, and validation belong to the same
named-text-style feature ticket.

For a broad request, agree on a first useful deliverable and its acceptance boundary before
expanding the decision list. Identify which unresolved choices actually prevent specifying,
building, or validating it. Defer later choices and optional refinements with the later scope they
affect. Preserve the requested overall outcome; do not silently drop requirements or report the
whole effort complete after delivering only this part. If I request a complete design up front,
retain that planning boundary.

When the outcome accepts an open input domain or exposes a public composition or extension seam,
state its supported boundary and the responsibilities that remain with consumers when those facts
materially bound acceptance.

Distinguish among:

- Facts that can be established through inspection or research.
- Product, interaction, or behavioral choices that require my judgment.
- Consequential architecture, data, and interface decisions.
- Reversible implementation details that can remain with implementation.

Resolve enough of the first three categories that implementation will not need to invent intent.
Use established conventions and judgment I have delegated for reversible details within accepted
behavior. Record the resulting contract in its owner. Do not turn incidental details into approval
tickets or prescribe them merely to make the plan appear complete.

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

Keep design questions and accepted answers in the existing design issue or work record. Before
creating a separate ticket, check existing ownership and apply the provider's creation rules.
Consolidate related refinements into their current contract when it settles and before leaving
planning. Retire superseded records after preserving material decisions and updating their links.

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
ownership. When proceeding by deliverable, cover the accepted first deliverable and keep later
scope explicit; create later tickets when their outcomes are sufficiently defined. Order tickets
by real dependencies and identify those ready for implementation. One fresh context bounds ticket
size; it does not justify a ticket for every question, file, or minor refinement. Planning and
research use the feature boundary. Decompose actual implementation into logical units of work
with useful deliverables, acceptance checks, and genuine dependencies. One feature's implementation
may require several tickets; do not force it into one ticket because its research and planning
share one owner.

## Continue

Continue to implementation when:

- The specification expresses the accepted intent and boundaries.
- Every consequential decision blocking the deliverable is resolved; deferred choices cannot
  change its accepted behavior or acceptance checks.
- The implementation tickets collectively cover the accepted deliverable, with later scope explicit.
- Every ticket has observable acceptance checks, accepted sources, and genuine dependencies.
- At least one implementation ticket is ready and unblocked.
- Implementation can begin in a fresh context without inventing behavior or architecture.

Remain in planning while any of these conditions are unmet. If later evidence invalidates part of
the plan, preserve what remains valid, revise the affected artifacts, and reassess which tickets
are ready.
