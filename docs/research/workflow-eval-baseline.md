# Workflow evaluation baseline

## Question and sources

What keeps wayfinding progress in later replies?

Pocock's [grilling](https://github.com/mattpocock/skills/blob/a496f5513d4a4cf889bc48e189e579f4b0bdf6aa/skills/productivity/grilling/SKILL.md)
uses a repeating discussion process. His [writing guidance](https://github.com/mattpocock/skills/blob/a496f5513d4a4cf889bc48e189e579f4b0bdf6aa/skills/productivity/writing-for-agents/SKILL.md)
separates selecting instructions from following them.
[Official OpenAI documentation](https://learn.chatgpt.com/docs/customization/overview)
distinguishes durable global guidance from skills selected for a task.
[Anthropic](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#workflows-and-feedback-loops)
recommends workflow checks. [MultiTurnInstruct](https://arxiv.org/html/2503.13222v1)
shows that recalling instructions and following them are different capabilities.
These sources informed experiments; they do not prove a fix for this workflow.

## Method

Use gpt-6.1-sol and Codex SDK/runtime 0.163.0 in isolated projects. Compare the original
instructions with changes to selection, discussion steps, reply checks, and global entry.
The final run allows 350,000 reported tokens and 240 seconds per attempt. Token totals include
repeated input across tool calls. Routine cases never request compaction; integration cases
request it in short conversations. Reply checks inspect final answers, excluding commentary.

## Findings

The original agent restored the right question and saved state but lost the progress line.
Moving the guidance, using a complete template, naming the skill explicitly, changing its
description, adding a discussion loop, and adding a completion reminder did not preserve the
line through follow-ups. A skill-level instruction to resume before each reply also failed.

Two changes worked together: global guidance reads the work-system skill and resumes the
workflow before repository replies; wayfinding says to start each reply with its existing line.
Neither change alone survived short questions. The pair kept the line and updated its counts
when an answer settled a decision. Ending wayfinding removed the line while planning continued.

The global entry adds reading and navigation. One three-reply comparison used about 185,000
reported tokens with the pair, versus 134,000 with the original instructions. This is measured
usage for one case, not a spending forecast.

A grader initially rejected “CSV containing only the header.” Its corrected check accepts that
and “header-only CSV,” still requires the refusal alternative, and rejects missing choices.

## Results

The original four passing cases remain regression checks. Earlier baseline runs included one
runtime error followed by a completed retry. Results below describe behavior, not that error.
The stopping case originally failed its initial active-wayfinding reply; cancellation succeeded.

| Case | Original instructions | Retained pair |
| --- | --- | --- |
| Incomplete design | Pass | Pass |
| Planning PR unmerged | Pass | Pass |
| Local tracking | Pass | Pass |
| Narrow correction | Pass | Pass |
| Recovery from supplied state | Missing line | Pass |
| Separate conversations | Missing line on return | Pass |
| Follow-up question | Missing line | Pass |
| Short follow-ups | Missing line | Pass |
| Counts after an answer | Missing line on recap | Pass |
| Stop wayfinding | Missing initial line | Pass |
| Explicit compaction | Missing line afterward | Pass |

Each initial wayfinding case passed at least two attempts with the retained instructions. The switch
case passed two fresh runs after its choice check was corrected. No routine run compacted its
context; each integration attempt confirmed one compaction.

## Added routine cases

Eight added cases use the same instructions. Revision was inconsistent: one acknowledgement
omitted progress despite updating the design and map; its recap recovered. The repeat passed.
Amendment exhausted 350,000 reported tokens, then passed with 500,000 available, using 418,202.
The repeat batch allowed 240 seconds per case. No compaction was observed in the added runs.

| Case | First attempt | Repeat |
| --- | --- | --- |
| Revised accepted answer | Missing progress on acknowledgement | Pass |
| Blocked question becomes ready | Pass | Pass |
| Code question during wayfinding | Pass | Pass |
| Question before a change | Pass | Not repeated |
| Amendment preserves earlier edit | Allowance limit | Pass |
| Missing implementation ticket | Pass | Not repeated |
| Continue planning discussion | Pass | Not repeated |
| Tracker across conversations | Pass | Not repeated |

## Planning records and completion

Each case ran twice; final checks accept grouped shell commands.

| Case | First attempt | Repeat |
| --- | --- | --- |
| Finish wayfinding | Saved wayfinding remained active | Pass |
| Update dependent tickets | Pass | Pass |
| Recover from an outdated recap | Pass | Pass |
| Return from a prototype | Pass | Pass |
| Keep related questions together | Pass | Pass |
| Report partial completion | Pass | Pass |
| Start ready implementation | Pass | Pass |
| Preserve uncommitted work | Pass | Pass |
| Replace one conversation's workflow | Pass | Pass |
| Failed verification | Pass after corrected grading | Pass after corrected grading |
| Unavailable verification | Pass after corrected grading | Pass |
| Reproducible bug | Pass | Pass |

## Limits

These are small samples with one model and short conversations, not failure-rate estimates.
Reply patterns remain mechanical checks, and GitHub responses remain local fixtures.
Deployment is separate from this study.

[Run instructions](../agent-evaluations.md). [Verification cases](workflow-verification-evals.md).
