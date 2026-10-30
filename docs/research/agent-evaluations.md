# Agent evaluation tools

## Question

Which existing tools can support a growing corpus of workflow cases, short conversations,
saved-state recovery, and explicitly requested Codex compaction?

## Findings

Use the official Codex Python SDK for native conversation control. It reuses existing Codex
authentication, supports Python 3.10, and provides threads, turns, interruption, structured items,
and token usage. A compaction request is an acknowledgement; the runner must observe the
completed compaction item and matching completed turn before continuing. The SDK routes those
events into turn queues. A small adapter override observes them before routing.

Keep case setup, execution, checks, and results shared across the corpus. Use the repository's
existing unittest suite to verify those components without model calls. Isolate the SDK adapter
from case definitions and checks. Pin the SDK so its bundled runtime and protocol agree.

| Tool | Reusable parts | Gap for this work |
| --- | --- | --- |
| Codex Python SDK | Native threads, authentication, turns, events, compaction | Needs case setup, checks, limits, and results |
| Inspect AI and inspect-swe | Datasets, scorers, limits, reports, sandbox execution | Stock Codex bridge uses Inspect provider credentials and lacks an explicit Codex compaction step |
| skill-ci and skill-eval-harness | Skill comparisons, assertions, isolated homes, reports | Native Codex runner rejects scripted multi-turn cases; recovery uses a separate interruption protocol |

The larger frameworks would still need a Codex adapter for the required conversation control.
Their reporting and model-comparison facilities may justify integration later. The SDK avoids
replacing the existing Codex login or adding a custom protocol client now.

## Sources

- [Official SDK](https://learn.chatgpt.com/docs/codex-sdk).
- [Authentication and native turns](https://github.com/openai/codex/blob/main/sdk/python/README.md).
- [SDK lifecycle example](https://github.com/openai/codex/blob/main/sdk/python/examples/06_thread_lifecycle_and_controls/sync.py).
- [Inspect agent bridge](https://inspect.aisi.org.uk/agent-bridge.html).
- [skill-ci dependency and runtime](https://github.com/mdsmithaustin/skill-ci/blob/main/pyproject.toml).
- [Pinned harness](https://github.com/mdsmithaustin/skill-eval-harness/tree/76e0f2179a9d5bd64d16eec88996b8c4bedff2bb).
- [Pstack eval playbook](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/eval.md).

## Limits

Findings come from source inspection. No model runs or framework installations were used for
this comparison. Seeded recovery tests restoration from supplied state; it does not establish
what a real compactor preserves. Explicit compaction needs its own integration case.
