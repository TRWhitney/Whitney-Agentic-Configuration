# Recurrence prevention trials

The four cases start in the affected workflow states. They exercise whether an agent loads the
right procedure, respects when it can edit, prevents the original mistake, and links the rule
to what enforces it during delivery. The control changes a valid requirement.

Runs used three attempts per evaluated case, with GPT-6.1 Sol as candidate and a separate
blinded judge. The repository checks supplement recorded commands, replies, and changed files.

| Case | Initial | After first clarifications | Accepted result |
| --- | --- | --- | --- |
| Read-only shipping discovery | 0/3 | 2/3 | 3/3. Reproduced the bug, identified the earlier incident, and kept the repository read-only. |
| Weight limit implementation and delivery | 2/3 | 3/3 | 3/3. Both paths share one rule, with regression checks and a link in the rule table. |
| CSV validation rework | 0/3 | 2/3 | 3/3. Reproduced the original bug in validation, loaded prevention in implementation before editing, then confirmed the fix. |
| Changed requirement | 3/3 | Reused | 3/3. Updated the requirement without invoking recurrence prevention. |

The first clarifications specify where discovery findings belong, which procedure to load
after returning to implementation, and how to link enforcement. The validation case needed
an additional instruction to exercise the original failing input before deciding to return.
The discovery rubric initially penalized replies that omitted an unrelated incident, then
penalized a reply that omitted a duplicate report. The final rubric checks which incidents
the agent counts. Implementation and control results were reused from their passing rounds.

All 188 eval definitions validate. The initial 152 repository tests and the final 54 focused
tests passed, along with lint, formatting, typing, whitespace, and skill structure checks.

```sh
uv run --group eval python -m evals run \
  --model gpt-6.1-sol --judge-model gpt-6.1-sol \
  --tag recurrence-prevention --repeat 3 --timeout 900 --judge-timeout 700
```
