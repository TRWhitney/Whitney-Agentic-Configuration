# Planning documents

A specification records the accepted problem, outcome, user stories, design decisions, testing,
and scope. Link applicable project agreements and release decisions. Use the project glossary
and link the decisions that constrain the work. Keep check results and reasons in the records
that already cover them.

Each implementation ticket describes one observable result, its acceptance checks,
prerequisites, accepted sources, and completion evidence. Size it for one fresh implementation
context and an independently verifiable result. Order work by dependencies.

Prefer tickets that each deliver a working result across all needed layers. For a mechanical
change too large to keep tests passing in one ticket, split it into adding the new structure,
moving callers, and removing the old structure. Make their dependencies explicit. Include file
paths or code snippets only when needed to state an accepted prototype requirement, type
definition, or function interface precisely. Link shared usage examples and declarations rather
than copying them into each ticket.
