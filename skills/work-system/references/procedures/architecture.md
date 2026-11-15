# Architecture Procedure

Decide what calling code uses, which component performs each operation, and which component
can change shared data. Keep these decisions in the existing feature design.

## Define the calls and results

Read the affected functions and the code that calls them. Trace their inputs, results, and
changes to stored data. Check why the existing code is divided this way before changing it.

Write example calling code before choosing types and function declarations. Include the normal
operation and relevant failure or cancellation behavior. Show the arguments, returned values,
and steps the calling code must perform. Keep examples consistent with accepted requirements.

Write calling examples and matching function declarations before requesting agreement on a
new or changed function interface. Discuss examples with me when they help resolve a
decision requiring my judgment or when I request review. Creating an example does not itself
require approval or ending the turn.

## Define responsibilities and compare designs

Use the examples to define the needed types and function declarations. Identify which component
performs each operation, passes each value, and can change each shared record. Include enough
to explain the operation from input to result. Leave internal helper functions to implementation.
Keep example code separate from production code until its behavior is implemented and tested.

Check for calling code that must repeat internal steps, multiple writers of the same data,
storage or network formats exposed unnecessarily, lists or rules maintained in multiple places,
and functions that only forward arguments without adding behavior or translating between APIs.
Resolve these problems where they occur. Keep required steps inside the component responsible
for completing the operation, so its calling code does not have to reproduce them.

Compare different ways to divide responsibilities when there is a genuine tradeoff. Explain
what each requires of calling code, how it handles shared data, and its implementation costs.
If a proposed design cannot meet an accepted requirement, check alternatives against that
requirement. Ask to change it only after explaining why those alternatives cannot meet it.
Do not reject a design that meets the requirements solely because it also provides a
guarantee the request did not specify.
For each failure guarantee, check what happens if cleanup also fails and which files or
records can then remain changed.
Use the prototype procedure when running an experiment is needed to decide. Do not require
alternative designs or multiple agents when existing requirements already determine the answer.

## Record the decision

Keep the usage examples, needed type definitions and function declarations, chosen division of
responsibilities, reasons, and useful rejected alternatives with the existing feature design.
Identify unresolved decisions. Follow the planning state's rules for agreement.

Link the accepted design from implementation tickets. Use domain modeling to record lasting
architecture decisions when its existing criteria apply. Review the implementation against
the agreed calls, results, and responsibilities.
