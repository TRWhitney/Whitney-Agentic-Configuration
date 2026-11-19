# Prevent recurrence

Prevent regressions by addressing the cause of the mistake. Prefer changes that make the
mistake impossible or detect it automatically.

## Implementation

Use the first option that addresses the cause at a cost proportionate to the risk and likely
frequency of the mistake.

1. Remove the way the mistake happens. Give shared data one writer, derive duplicated definitions
   from one source, or remove an obsolete interface that callers still copy.
2. Use types or validate values where they enter the system so invalid combinations are rejected
   before use.
3. Add or repair an automated check. Use lint when the incorrect code can be recognized reliably,
   and make its error explain what to use instead. For incorrect behavior, use a regression test
   through a stable interface. Use behavioral evals for agent decisions that depend on judgment.
4. Document the decision when it still depends on judgment and no practical check can assess it.

Explain the tradeoff that determined your choice. Add new checks to the project's normal suite.
Correct affected occurrences and obsolete examples that would cause the same mistake. If prevention
requires changing an agreed design, return to planning. Limit cleanup to directly connected work.
