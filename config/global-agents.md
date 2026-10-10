Glossary:
- "I," "Me," "My": Referring to me, the one communicating with you, Whitney.
- "You," "Your": Specifically you, the agent doing the work and reading this.
- "User": A consumer of the app, typically me, but may reach a wider audience.
- "Agent": An AI agent, usually you.

Communication:
- If I ask a question, then it is not a request for work. It represents genuine uncertainty that I believe needs resolution, before I am able to move forward. Answer the question if able, discuss with me if not, and until we come to a conclusion or I provide explicit instruction to do otherwise, do not move forward.
- Never tell me that you are the problem in the context of the instructions supplied to you via the agents.md or skills being sufficent. If I ask what is wrong with my instructions, or what is wrong with my skills, it means that they are there to prevent you from poor behaviors and the fact that you engaged in them nevertheless means they are insufficent.
- Challenge me when I say something that doesn't make sense, doesn't align with my earlier stated goals, doesn't align with our current work, or is not technically coherent. I have the final say, but I want to know, especially if I am trying to change the work or get confused on what's going on or how something works. I do not want any sycophancy, "You're right" are words that annoy me.

General:
- Do not add or modify a README, LICENSE, vendor specific infra (.github, etc.), or AGENTS.md unless you obtain permission from me or are directly asked to. Other top level content is generally fine, including .gitignore as appropriate to the repo content.

Evidence retention:
- Apply discard-by-default throughout research, experimentation, validation, documentation, review, and commits. Evidence preservation, reproducibility, and review requirements do not authorize retaining raw captures or exact historical replay.
- Retain conclusions and useful source: measured comparisons, failures, limitations, decisions, and reusable checks. Default to one report of at most 500 words plus a compact results table per study. Update an existing record when it fits; link findings from tickets and status records instead of repeating them. Expand this budget only when I explicitly request it.
- Do not commit agent session transcripts, per-run JSON, screenshots, logs, duplicate application or package snapshots, hash inventories, or evidence manifests unless I explicitly requested their retention. Requested deliverables and reusable source or tests may be retained; generating or inspecting an output does not make it a deliverable.
- Generate disposable outputs in temporary directories outside the checkout or vault. Keep them only for active inspection, required review, or a concrete diagnosis or retry. Delete them when that need ends and before delivery. Ignoring files does not satisfy cleanup. Preserve unrelated files and my work.
- Reviewers may inspect temporary evidence before disposal. Review must not require committing captures or preserving exact historical replay unless I explicitly requested it. Retain concise findings, not reviewer transcripts or elaborate review records.
- Do not replace a removed archive with deletion inventories, provenance maps, cleanup evidence, or another archive. Record useful findings in their existing canonical location.
- Before every commit, inspect generated file counts and sizes, untracked and ignored outputs, and staged additions, including large or binary files. Remove task-generated disposable material before committing or delivering. Carry these retention rules and any explicit exceptions into every delegated assignment.

Harness Usage:
- Use 'request_user_input' liberally when you have access to it, but never add a timeout for it, I will get to answering and would always prefer to answer
