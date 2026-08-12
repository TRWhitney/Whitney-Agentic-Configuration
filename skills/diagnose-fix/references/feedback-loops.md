# Defect feedback loops

Choose the highest-fidelity loop that can remain fast enough to run repeatedly:

1. Focused automated test at a public seam.
2. CLI or HTTP invocation with fixed input and asserted output.
3. Headless browser flow with DOM, console, and network assertions.
4. Replay of a redacted production-shaped payload or trace.
5. Minimal harness around the responsible subsystem.
6. Differential run against a known-good revision or configuration.
7. Automated bisection command.

For intermittent defects, pin controllable inputs such as time and random seeds, loop the trigger, add scheduling pressure when relevant, and measure failures per run. Preserve the user's symptom as the verdict rather than a generic crash check.

Keep credentials in environment variables. Redact tokens, cookies, authorization headers, personal data, and private payload fields from stored evidence and conversation output.
