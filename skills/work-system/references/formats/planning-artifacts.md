# Planning artifacts

A specification records the accepted problem, outcome, user stories, design decisions, testing,
and scope. Use the project glossary and link the decisions that constrain the work. Keep evidence
and reasoning in their owning records.

Each implementation ticket describes one observable result, its acceptance checks, prerequisites,
accepted sources, and completion evidence. Size it for one fresh implementation context and an
independently verifiable result. Order work by dependencies.

Prefer vertical slices. For a mechanical change that cannot stay green in one slice, use expand,
migrate, and contract tickets with explicit dependencies. Include file paths or code snippets only
when an accepted prototype needs them to state a decision precisely.
