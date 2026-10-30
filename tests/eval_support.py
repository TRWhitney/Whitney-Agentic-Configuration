from __future__ import annotations

import json

from evals.fixtures import Workspace
from evals.models import CaseSpec
from evals.runner import CaseResult, CommandResult, Observation, run_case
from tests.test_eval_runner import SOURCE, FakeDriver


def observe_case(
    case: CaseSpec,
    changes: dict[str, str],
    reply: str | tuple[str, ...],
    *,
    progress: tuple[str, str | None] | None = None,
    commands: tuple[str, ...] = (),
    command_results: tuple[CommandResult, ...] = (),
) -> CaseResult:
    def factory(
        workspace: Workspace, model: str, timeout: float, max_tokens: int
    ) -> FakeDriver:
        replies = iter([reply] * len(case.steps) if isinstance(reply, str) else reply)

        class ScriptedDriver(FakeDriver):
            def message(self, thread: str, prompt: str) -> Observation:
                for path, text in changes.items():
                    target = workspace.file(path)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(text)
                if progress is not None:
                    progress_file = workspace.progress_path(thread)
                    saved = json.loads(progress_file.read_text())
                    saved["state"] = progress[0]
                    if progress[1] is None:
                        saved.pop("substate", None)
                    else:
                        saved["substate"] = progress[1]
                    progress_file.write_text(json.dumps(saved))
                return Observation(
                    next(replies), 10, commands, command_results=command_results
                )

        return ScriptedDriver()

    return run_case(case, SOURCE, "example-model", driver_factory=factory)
