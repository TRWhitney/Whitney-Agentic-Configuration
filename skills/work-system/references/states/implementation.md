# Implementation State

Build the agreed behavior, its tests, and any refactoring needed to leave the affected code easy
to maintain. Use earlier states for changes to requirements and validation for completion
checks.

## Understand the change

Start with the agreed requirements, acceptance checks, and supporting documents or prototypes.
Inspect the affected code and interfaces to determine what must change.

If a check, source, or architecture constraint is missing, contradictory, or impossible to
follow, identify the problem and return to the first state that can settle it. Do not guess my
intent or expand the task.

Refactor across files, layers, and interfaces when it improves the code involved in this change.
Include code you inspect or change and directly connected code that prevents a clear
implementation. Do not keep awkward structure merely to reduce the diff. Do not search unrelated
code for cleanup opportunities or start a separate refactoring effort without my direction.

Keep behavior outside the agreed change unchanged and keep affected tests passing.

## Build the change

When changing behavior, use the testing procedure. Choose the test before changing production
code, then keep the focused test and affected tests passing as you build.

- Remove duplication, misleading abstractions, obsolete interfaces, and unnecessary complexity
  in the involved code. Improve how it divides responsibilities and manages dependencies.
- Keep domain and application logic separate from GUI rendering and interaction as far as
  practical. Connect them through explicit interfaces and data.
- Inject services, storage, time, and other dependencies that may vary. Do not hide them in
  globals, service locators, or constructors inside domain logic.
- Use precise types and explicit states. Do not weaken types merely to make the change compile.
- Handle errors where you can add useful context. Keep the underlying cause available for
  diagnosis without exposing implementation details to users.
- Reuse suitable dependencies. Add a library when it removes substantial custom code and fits
  the project's stack. Do not rebuild an existing library or add a broad framework for a narrow
  need.
- Add abstractions for required behavior or variation already needed by the project. Do not
  design extension points for hypothetical uses.
- When removing something, remove its deprecated paths, aliases, compatibility code, and
  duplicate implementations unless the agreed requirements explicitly need them.

Connect all layers needed for the user-visible result. An internal helper alone does not satisfy
an acceptance check that requires the complete feature.

Use available specialist procedures when their cues apply and include their results in this
change. Passing implementation tests supports development; validation still needs to check the
final result.

## Continue

Continue when the agreed behavior works across the affected layers, focused and affected tests
pass, and no known defect or unresolved product or architecture decision remains.

Move to validation when the finished change is ready to check directly. If implementation
reveals a misunderstood requirement or missing decision, return to the first state that can
settle it. Keep parts of the implementation that are still correct.
