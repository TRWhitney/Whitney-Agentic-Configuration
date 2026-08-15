# Implementation State

Turn the accepted outcome into a coherent, maintainable repository change. Implementation owns
production changes, supporting tests, and refactoring that improves the code while the outcome is
built. It does not own new product intent or completion evidence.

## Establish the change

Begin from the accepted outcome, concrete acceptance checks, and source artifacts that constrain
the work. Inspect the existing seams and determine what must change to produce the observable result
cleanly.

When an acceptance check, source, or architectural constraint is missing, contradictory, or no
longer feasible, identify the exact gap and use the earliest available route that can resolve it.
Do not silently reinterpret accepted intent or enlarge the outcome.

Do not measure implementation quality by diff size. Refactor freely within the code and
relationships involved in the accepted outcome. This includes code inspected or changed to
implement the behavior and directly coupled code whose structure prevents a clean implementation.

Follow a refactoring across files, layers, and interfaces when necessary to leave that working set
coherent and maintainable. Do not search unrelated parts of the repository for cleanup opportunities
or begin a separate refactoring effort without my direction.

Keep behavior outside the accepted change stable while refactoring, and keep the focused and
affected tests green.

## Build the outcome

For behavior-changing work, implementation and the required testing procedure form one loop.
Establish the focused test boundary before changing production behavior, then evolve the
implementation while its focused and affected tests remain green.

Apply these engineering preferences while building:

- Refactor the involved code when doing so improves maintainability, clarity, cohesion, boundaries,
  dependency structure, or extensibility. Remove duplication, misleading abstractions, obsolete
  boundaries, and accidental complexity revealed by the work. Do not preserve awkward structure
  merely to keep the diff small.
- Keep domain and application behavior independent of GUI rendering and interaction to the fullest
  practical extent. Connect them through explicit interfaces and data rather than embedding
  business behavior in presentation code.
- Use dependency injection for services, infrastructure, time, storage, environment, and other
  collaborators whose behavior may vary. Do not hide those dependencies in global state, service
  locators, or construction buried inside domain behavior.
- Preserve precise types and model meaningful states explicitly. Do not weaken types merely to make
  the change compile.
- Handle failures at the boundary that can add useful context. Preserve actionable causes rather
  than swallowing errors or exposing implementation details to consumers.
- Reuse established dependencies when they fit. Add a focused dependency when it removes meaningful
  owned complexity and belongs in the repository's stack. Do not recreate a capable dependency or
  introduce a broad framework for a narrow need.
- Add abstractions for accepted behavior or demonstrated variation, not hypothetical flexibility.
  Keep extension seams clear without generalizing beyond evidence.
- Treat removal as removal. Do not retain deprecated paths, compatibility behavior, aliases, or
  shadow implementations unless the accepted outcome explicitly requires them.

Integrate every layer needed for the observable outcome. Do not stop at an internal mechanism when
the acceptance checks require consumer-visible behavior.

Use authorized specialized procedures when their cues apply. Incorporate their results into the
same coherent implementation rather than treating them as separate outcomes.

Focused test results support the implementation loop but do not establish completion evidence.

## Continue

Continue when every accepted behavior is implemented, focused and affected tests are green, the
change is integrated across its relevant boundaries, and no known implementation defect or
unresolved consequential decision remains.

Use the available route to the next state only when the completed implementation is ready for
direct completion evidence. If implementation exposes an earlier misunderstanding or decision gap,
use the route to the earliest state that can resolve it and preserve work that remains valid.
