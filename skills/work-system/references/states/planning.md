# Planning State

Work with me to agree on a specification and an ordered set of implementation tickets. Settle
requirements, important decisions, and how to divide the work. Do not implement production code.

## Define the goal

Read the request, relevant code and architecture, and agreed sources. Inspect the current
implementation before planning changes to it.

Describe the problem, who is affected, expected behavior, constraints, failure and edge cases,
and what is out of scope.

Keep one combined research-and-planning ticket per distinct feature. Its questions, detailed
requirements, architecture concerns, experiments, and agreed answers belong together. A change
of question, method, evidence, agent, or context does not justify another planning ticket. For
example, named text-style syntax, defaults, inheritance, and validation belong to one feature.

For broad work, agree on the first useful deliverable and its acceptance checks before listing
more decisions. Identify choices that block specifying, building, or checking that deliverable.
Defer later choices with the work they affect. Keep the full requested goal in scope for the
effort; do not call it complete after delivering only part. If I request a complete design up
front, plan that full design.

For open-ended inputs or public composition and extension interfaces, state which uses are
supported and what callers must handle when that affects acceptance.

Separate facts you can check, product and interaction choices that need my judgment, important
architecture and data decisions, and reversible implementation details. Settle the first three
enough that implementation will not need to guess my intent. Use project conventions and
judgment I have delegated for reversible details. Record decisions in the existing feature
ticket without creating approval tickets for incidental details.

## Settle decisions

Keep discussing choices that need my judgment. Recommend an answer when the facts support one,
explain tradeoffs, and ask only about decisions I need to make. Update the plan as we decide. A
draft does not replace discussion or agreement.

Use available planning procedures when their cues apply. Use experiments through those
procedures when trying something is needed to decide. Do not implement production behavior
during planning.

Record agreed conclusions and their reasons, not a transcript. Link research, prototypes,
decisions, and domain documentation instead of copying them. If a decision changes, update the
specification and every ticket that depends on it.

Before creating a ticket, check the current design issue or work record and the tracker's
creation rules. Put related refinements into the existing design. Before leaving planning, move
useful decisions and reasons from redundant records into that design, update links, and close or
remove the redundant records under the tracker's rules.

## Write the specification and tickets

Use the displayed planning format. The specification states the agreed behavior, supported uses,
interfaces, data, interactions, and testing decisions needed to implement the work.

Divide implementation into tickets that each fit one fresh agent context. Each must:

- deliver a result you can observe and check independently;
- give acceptance checks and link the sources needed to implement it;
- list only real dependencies and blockers;
- leave no product or architecture decision for the implementing agent to invent.

Prefer tickets that connect all layers needed for a result over tickets divided by file or
technical component. Avoid file-by-file instructions, speculative tasks, and code likely to
become outdated.

Check that tickets cover the agreed deliverable without gaps or duplicate work. When delivering
in parts, keep later work explicit and create its tickets when requirements are clear enough.
Order by dependencies and identify tickets ready to build. One fresh context limits ticket size;
it does not justify a ticket for every question, file, or refinement. Planning stays grouped by
feature, while one feature's implementation may need several tickets.

## Continue

Continue to implementation when the specification describes the agreed behavior and scope, all
decisions blocking this deliverable are settled, and deferred choices cannot change its behavior
or acceptance checks. Tickets must cover the deliverable, link their sources, and list real
dependencies. At least one must be ready for a fresh context to implement without guessing.

Stay in planning otherwise. If new findings overturn part of the plan, keep the valid parts,
update affected documents and tickets, and reassess which work is ready.
