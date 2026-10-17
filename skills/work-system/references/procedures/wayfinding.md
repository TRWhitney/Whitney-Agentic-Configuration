# Wayfinding procedure

Turn a broad or unclear request into agreed requirements using a decision map. Plan decisions
here, not production code. Use the displayed format for the map and feature tickets.

## Define the goal

Describe the finished result in one or two sentences. For broad work, agree on the first useful
deliverable and its acceptance checks before listing decisions. Put later work under `Out of
scope` for this deliverable. Put unclear topics under `Not yet specified` only if they may
affect it.

Group questions by feature. Keep each feature's questions, research, detailed requirements,
refinements, and agreed answers in one combined research-and-planning ticket. Create another
planning ticket only for a distinct feature under the tracker's rules. Identify how to answer
its open questions and what blocks them. Do not add speculative questions just to fill the map.

## Work through the next decisions

Choose precise, unanswered, unblocked questions that prevent specifying or building the first
deliverable. They may be sections of one design issue. Claim a ticket before working on it. Use
a compact progress line during discussion:

`Planning: <n> decided, <n> ready, unspecified: <topics or none>`

Name the current decision and what it blocks. Give the facts and tradeoffs needed to decide,
recommend an answer with its reason, and ask one main question. Group questions that use the
same facts and are clearer to answer together. Do not split questions I can reliably answer
together. Separate questions do not need separate records.

Do not paste the map into conversation or recap everything after each answer. Give a larger
update when the goal or remaining work changes significantly. Do not estimate a percentage or
fixed question count, since an answer can reveal or remove work.

Use research for factual questions and prototypes when trying something will help us decide. A
`task` is an action needed to answer a question, never production implementation. Use project
conventions and delegated judgment for reversible details within the agreed behavior. Record the
choice in its feature ticket without a separate approval ticket. Leave decisions that need my
judgment to me. While research runs, work on another unblocked decision if one is available.

## Update the map and tickets

After each answer, update the requirements and supporting sources in the feature ticket. Keep
its planning open while a blocking question remains. Once settled, mark it resolved, update its
issue state under the tracker's rules, and link the conclusion from the map.

Reassess the next decisions and unspecified topics. Add a question to its feature ticket when it
is precise and blocks the deliverable. Create a new planning ticket only for a distinct feature.

When requirements settle and before a planning handoff, move useful decisions, reasons, and
source links from redundant records into the existing feature ticket. Close or remove redundant
records under the tracker's rules and update map links and blockers. Merely renesting or closing
issues does not combine their useful content.

Link research and agreed prototypes instead of copying them. Use domain modeling to document
project terms or architecture decisions that future work needs, then link those documents from
the feature ticket.

Keep the map an index. Feature planning records requirements; implementation tickets describe
work to build them. Finish when the deliverable is clear, its blocking decisions are settled,
and a fresh context can write its specification and implementation tickets without guessing my
intent. Deferred choices must not affect its acceptance checks or be reported as resolved.

## Result

Report the goal, first deliverable, links to agreed requirements, exclusions, deferred work, and
remaining unspecified topics and ready decisions. When finished, report that no blocking
decision or unspecified topic remains for the deliverable.
