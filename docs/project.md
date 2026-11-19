# Whitney Agentic Configuration

This repository maintains Whitney's agent instructions, skills, and the tools used to install and
evaluate them. See the [deployment instructions](deployment.md) and the
[guide to writing agent evals](eval-authoring.md).

## Work-system rules

| Rule | What prevents or detects a violation |
| --- | --- |
| A procedure can load only in a workflow state that declares it. | The [navigator rejects procedures absent from the state's list](../skills/work-system/scripts/navigation.py#L132). The [state boundary test](../tests/test_work_system.py#L854) checks both an available procedure and a rejected one. Run `uv run --group dev python -m unittest tests.test_work_system.NavigatorTests.test_procedure_command_enforces_the_active_state_boundary`. |
