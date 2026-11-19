# Validate recurrence prevention

Use the implementation evidence to confirm that a new or repaired check rejects a real example
of the mistake for the expected reason. Run the affected checks on the completed change and
confirm that valid behavior passes. If the design removes the cause, show how the change
prevents the old mistake and exercise the supported behavior.

If the existing check may miss the mistake, exercise the original failing case in validation
before deciding whether to return to implementation.

If prevention requires a further change to code, tests, or checks, return to implementation
and load `prevent-recurrence` before editing. Use the existing workflow routes for unresolved
requirements or design decisions.

Record what changed and the evidence in the work record when one exists. Identify the affected
rule and what now enforces it for the rule-table update in delivery. Use the documentation
procedure to make that update.
