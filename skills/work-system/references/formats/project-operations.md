# Project operating documentation

Preserve the project-specific steps another developer or agent needs to operate the application.

## Find the existing documentation

Read the project record and relevant developer docs, scripts, and tests. Update the document
that covers the task. Create a document in the project's existing documentation structure only
when the needed instructions have no suitable home. Link it from the project record when one
exists.

Keep common setup in one place. Link feature-specific instructions where they become useful.
Reference existing scripts, tests, and accepted requirements rather than duplicating them.

## Establish usable instructions

Inspect application entry points, configuration, startup scripts, and existing interaction tools.
Record the details needed for the documented operations:

- Build and startup commands, configuration, authentication prerequisites, migrations, and test
  data. Explain how to recognize that the needed feature is usable, beyond a running process.
- Isolated data, ports, or profiles, and how to identify resources the run owns. State any
  prerequisites for using an existing instance when a separate instance is unavailable.
- Actual commands, UI controls, or public API requests for reaching and operating the feature.
  Explain how to inspect its output and stored effects, linking expected behavior to its source.
- Checks for an unhealthy instance after a failed interaction, recovery to a usable state, and
  cleanup of owned processes and temporary data, including after failed attempts.

Use existing tools before adding helpers. When repeated setup or interaction needs automation,
implement and test it through the existing implementation workflow and document its invocation.

## Check and maintain the instructions

Exercise new or changed operating steps from their documented starting state through cleanup.
Reuse current implementation or validation evidence when it demonstrates those exact steps.
Identify unexercised steps, unavailable prerequisites, and differences from the supported target
so they are not presented as proven. Apply the existing evidence retention rules to captures.

When the application changes, update affected commands, prerequisites, feature instructions,
and helper references. Distinguish outdated instructions, inadequate helpers, and product bugs;
correct each through its existing owning state. Preserve accepted expected behavior when the
application is wrong. A requested documentation audit covers its stated scope; ordinary feature
work updates the affected instructions.
