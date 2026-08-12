Hey, I'm Whitney. I'm a software developer with an interest in building bespoke apps and growing a dependency stack that allows me to create the things no one else is willing to make. Usually this involves simulators and tools. I prefer when code is well thought out, maintainable, extensible, and eloquently refined to what is essential all without sacrificing behavior or style. Below are a series of points to help you understand my intent. These are mostly not hard strict rules, but when they stand between you and the task, ask rather than abandoning these principles.

Glossary:
* "I," "Me," "My": Referring to me, the one communicating with you, Whitney.
* "You," "Your": Specifically you, the agent doing the work and reading this.
* "User": A consumer of the app, typically me, but may reach a wider audience.
* "Agent": An AI agent, usually you.

Code Style:
* Do not be afraid to refactor as it makes sense and requirements change and expand.
* Utilize dependency injection.
* Separate backend code from GUI code to the fullest extent possible.
* Do not add or modify a README, LICENSE, vendor specific infra (.github, etc.), or AGENTS.md unless you obtain permission from me or are directly asked to. Other top level content is generally fine, including .gitignore as appropriate to the repo content.
* Never attempt to support features which I ask you to remove. Assume there are no current users of the product and do not attempt to support backward compatibility unless otherwise asked.

Testing and Verification:
* Linting is mandatory, no outstanding is acceptable. Run linters to ensure style.
* Type checking is mandatory, do not use 'Any' unless there is no reasonable alternative. Run type checkers when possible (for languages where it is possible) to ensure correctness.
* Formating is necessary, run a formatter to ensure consistency.
* We use Test Driven Development, all features and fixes require tests. Tests must be run and go green before finishing a task. If you see a flakey test, it is always in scope to correct, if a test is red it is your problem.
* But do not write endless smoke tests or tests to ensure a feature has been removed, focused tests which prevent regressions in capability are what we want. Partition tests into verification tiers as necessary and evaluate what suites must be run based on your changes.
* Visual verification is a must. Use playwright, or any other means at your disposal if playwright is insufficent, to take screenshots and visually verify the state of any GUIs or output yourself.
* Use the DOM tree to ask yourself some questions. Are elements all aligned? Are there any elements which can be rendered in the layout which may shift the elements around? If so, will they misalign elements? Are there elements in arkward places? Do *not* rely on the DOM tree alone though, does the GUI look right when you verify visually?
* Always verify reported symptoms directly, do not allow implementatin proxies to stand in for direct proof a bug is fixed.
* Before editing code, write down the concrete acceptance checks that will be used to ensure the task is done or bug is fixed.
* Do not mark GUI bugs fixed if the verified Playwright flow (or other flow when playwright is not available) did not include the exact triggering action, exact target element, and exact post-action state described by me.

Visual Style:
* Avoid em-dashes in user facing prose.
* Strive for consistency. Reuse components and check that the
* Dark and Light mode must both be considered in any work, does this contrast well in both? Are any elements leaking in from another style?
* Use adaptive units, users will have different display resolutions and the app should look and size consistently on them.
* Reactivity is paramount. GUI elements should update as data changes and should virtually never require an explicit action or user refresh.
* Modern and sleek are the keywords, avoid design language which speaks to outdates controls.
* UX is important, are elements in need of progressive disclosure? Is it intuitive (where to click, what each action will do, what is an interactable or inactive element) to someone who has no idea what the project is?
* Minimize use of cards, sometimes they make sense, but often they are out of place.
* Never make user facing prose read like a sales pitch, a technical description, a description of design intent, or list of capabilities. Do not let things I tell you to consider for implementation leak into user facing text, unless I make it obvious this is what I want it to say or describe, it's probably just information to aid your work.

Commit and squash liberally, but be smart about it. Ask yourself the following questions:
* Does it seem like I want to provide input on the work or confirm things work before commit?
* Is the upstream (if any) updated? If not, then we have more freedom to squash.
* Did you make significant design or behavior assumptions or take liberties that I may have to provide input on before committing?
* Is the work done, or issues fixed, tweaks made, something that should or could have been part of the previous commit?
* Did I make changes which can logically be included in your changes?
* Are the changes in the working tree two distinct logical units of work? Does it make sense to be multiple commits or one?

Commit messages should be descriptive but terse (sub 50 characters), tailored for human readability:
* All commits should include a slug first, one of: [Feature] (for significant features), [Fix] (for bugs), [Tweak] (for minor changes), [Refactor] (for refactoring tasks), [Optimization] (for performance changes), [Documentation] (for primarily documentation related changes), [Design] (for documentation work pre-implementation for features), [Cleanup] (for tidying unused files), and [Chore] (for bumping versions, scaffolding, and other non-development work not covered by other categories).
* Use the imperative style messages, active verbs to describe a command to the repo (Ex: "Add login page" instead of 'Added login page')
* Focus on clarity, is there ambiguity with the phrasing? Would someone with no technical knowledge of the codebase know what changed?

Harness Usage:
* Use 'request_user_input' liberally when you have access to it, but never add a timeout for it, I will get to answering and would always prefer to answer
* If a subagent is ever used (should only be at my request or for research tasks), ensure file scope and git boundaries are clearly communicated so no conflicts between agents occurs.
* Use the search tool liberally, especially with research, I rather you be thorough and well informed (look at multiple sources to develop a well-rounded approach).
