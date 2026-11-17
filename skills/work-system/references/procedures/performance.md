# Performance procedure

Investigate performance, evaluate possible improvements, and check measured claims or requirements.

## Define the measurement

State the operation or comparison to investigate and any agreed performance requirement.
Identify the input sizes, concurrency, environment, and metric needed to answer it. Use
representative workloads and existing project tools where suitable.

Read the measurement code. Establish where timing starts and ends, what it counts, and what
it excludes. Include the complete operation relevant to the claim. Measure individual parts
when useful, but establish their contribution to the complete operation.

## Establish reliable evidence

- Confirm the intended work happens inside the measurement: requests finish, data is read or
  written, asynchronous work completes, and results are consumed.
- Check output correctness and count completed work, failures, retries, and timeouts alongside
  speed. Faster rejection or incomplete work does not establish an improvement.
- Record versions, build options, configuration, cache conditions, and competing machine load.
  Compare equivalent work under comparable conditions. Use settings appropriate to the
  intended deployment; resolve consequential configuration differences before recommending
  one option over another.
- For comparisons, run each of the two alternatives at least five times, alternating between
  Alternative A and Alternative B (A, B, A, B, ...), so warmup, cache effects, and changing
  machine load do not consistently favor one alternative. Report the median and range, or the established benchmark's
  appropriate statistics. When results are close, use the benchmark tool's statistical comparison
  or an appropriate statistical test to assess whether the repeated measurements support a
  difference despite their variation. If they do not establish a winner, report that uncertainty.
- Check claimed savings against the measured time the affected work takes. Removing a step
  that takes 100 ms cannot by itself save 500 ms. Compare reported throughput with available
  CPU, storage, or network capacity. Investigate results that exceed those limits before
  using them.

For an explicitly requested rough estimate, one run is sufficient if work completion and
correctness are checked. Label it as a single-run estimate and identify any simulated work
or delays it includes. Use repeated comparisons when choosing between options or claiming
an improvement or regression.

Reuse existing evidence only when its code, workload, configuration, and recorded observations
support the current question. Rerun affected measurements when those conditions change.

## Explain and evaluate changes

Use measurements to identify what limits performance. When the cause is unclear, profile CPU,
waiting, allocation, or I/O as relevant and trace the expensive work to its source. Profile
separately from reported timing runs so instrumentation does not distort the comparison.
Check whether the measurement tool or load generator is limiting the result.

When evaluating an improvement, establish a baseline before changing the relevant code.
First consider removing unnecessary or repeated work. Then consider doing it less frequently,
deferring it, or performing it outside the interaction someone is waiting on, where accepted
behavior permits. Consider concurrency or a cheaper implementation after those options.
Measure each attempt against the baseline while preserving required behavior. Stop when the
agreed goal is met.

When checking a completed change, reproduce the claimed comparison and check the agreed
requirement under its stated conditions. A faster internal helper does not establish that the
complete operation improved. Distinguish a measured difference from an explanation of its cause,
and a tested workload from broader production claims.

Keep repository code and test changes in implementation. Return defects, inadequate checks,
or unresolved requirements through the active state's existing routes.

## Result

For comparisons, state whether an alternative is faster, slower, shows no measurable difference,
or the result is inconclusive.
Call a comparison inconclusive when the factor limiting performance is unknown, an alternative
remains improperly configured for its intended use, or correctness or completed work could not
be checked. Identify the missing evidence.

Report supporting measurements with units, run counts and variation, completed work and errors,
and relevant conditions. For a change, include the baseline, result after the change, and
difference. Distinguish confirmed causes from hypotheses and state whether any agreed target
was demonstrated.

Preserve reusable measurement commands or scripts and concise findings in the existing record.
Keep raw captures outside the checkout through inspection and required review, then delete them
under the existing evidence retention rules.
