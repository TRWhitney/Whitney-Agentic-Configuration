Hey, I'm Whitney. I'm a software developer with an interest in building bespoke apps and growing a dependency stack that allows me to create the things no one else is willing to make. Usually this involves simulators and tools. I prefer when code is well thought out, maintainable, extensible, and eloquently refined to what is essential all without sacrificing behavior or style. Below are a series of points to help you understand my intent. These are mostly not hard strict rules, but when they stand between you and the task, ask rather than abandoning these principles.

Glossary:
- "I," "Me," "My": Referring to me, the one communicating with you, Whitney.
- "You," "Your": Specifically you, the agent doing the work and reading this.
- "User": A consumer of the app, typically me, but may reach a wider audience.
- "Agent": An AI agent, usually you.

Communication:
- If I ask a question, then it is not a request for work. It represents genuine uncertainty that I believe needs resolution, before I am able to move forward. Answer the question if able, discuss with me if not, and until we come to a conclusion or I provide explicit instruction to do otherwise, do not move forward.
- Never tell me that you are the problem in the context of the instructions supplied to you via the agents.md or skills being sufficent. If I ask what is wrong with my instructions, or what is wrong with my skills, it means that they are there to prevent you from poor behaviors and the fact that you engaged in them nevertheless means they are insufficent.
- Challenge me when I say something that doesn't make sense, doesn't align with my earlier stated goals, doesn't align with our current work, or is not technically coherent. I have the final say, but I want to know, especially if I am trying to change the work or get confused on what's going on or how something works.

Code Style:
- Do not be afraid to refactor as it makes sense and requirements change and expand.
- Utilize dependency injection.
- Separate backend code from GUI code to the fullest extent possible.
- Do not add or modify a README, LICENSE, vendor specific infra (.github, etc.), or AGENTS.md unless you obtain permission from me or are directly asked to. Other top level content is generally fine, including .gitignore as appropriate to the repo content.
- Never attempt to support features which I ask you to remove. Assume there are no current users of the product and do not attempt to support backward compatibility unless otherwise asked.

Visual Style:
- Avoid em-dashes in user facing prose.

Harness Usage:
- Use 'request_user_input' liberally when you have access to it, but never add a timeout for it, I will get to answering and would always prefer to answer
