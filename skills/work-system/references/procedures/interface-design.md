# Interface Design Procedure

Approach interface work as a design lead responsible for a recognizable visual identity, not as a
component assembler decorating a functional layout. Establish or apply a distinctive point of view
without overriding accepted intent, established visual language, or product boundaries.

## Ground the direction

Inspect the consumer's primary task, the interface's single job, real content, established design
system and components, prior designs, and any accepted prototype. Identify the subject, audience,
technical constraints, and the qualities the product should express. Build from the subject's own
materials, instruments, artifacts, language, and relationships rather than generic model defaults.
Use real subject matter throughout; placeholder content hides whether the design actually fits.

Treat an established visual language and accepted prototype as primary sources unless the accepted
work changes them. New work should belong to the product rather than look distinctive only in
isolation. Preserve accepted choices even when they resemble a common pattern.

If product meaning, the consumer's task, or another consequential visual choice is unsettled, do
not invent it. Identify the missing decision and its effect. When accepted intent leaves an
inconsequential axis free, exercise judgment confidently. Take one real aesthetic risk that can be
justified from the subject, then keep the surrounding design disciplined.

## Plan a specific design

Choose a clear visual premise, not a collection of fashionable effects. For a page or other
prominent view, the primary surface is a thesis: lead with the content, interaction, image, or
demonstration most characteristic of the subject. Do not default to a centered headline, large
metric, supporting statistics, and gradient accent unless that structure expresses something true.

Develop each design axis deliberately:

- **Typography:** Typography carries personality. Choose two or more type roles with a deliberate
  relationship, clear scale, and intentional weight, width, spacing, and hierarchy. A display role
  should add character with restraint; body and utility roles must remain highly legible. Follow an
  established type system when one exists rather than changing it merely to appear novel.
- **Color and atmosphere:** Use a dominant visual world with purposeful accents. Draw backgrounds,
  texture, depth, imagery, and contrast from the subject. Avoid timid distribution of many unrelated
  colors and decorative effects that have no semantic or atmospheric role.
- **Composition:** Structure must communicate content relationships. Structural devices such as
  numbering, dividers, labels, and containers must encode real meaning. Numbering implies sequence
  and belongs only when content actually has that order. Cards must represent genuine grouping
  rather than serve as the default container. Use asymmetry, overlap, density, or negative space
  when the premise supports them, not as automatic signs of creativity.
- **Motion:** Motion must serve the subject, hierarchy, or interaction. Prefer one orchestrated
  moment over scattered animation. Sometimes restraint is stronger; extra motion can make a design
  feel as generic as having none. Preserve reduced motion and never make animation the only carrier
  of meaning.
- **Complexity:** Match complexity to the direction. Expressive work may justify layered composition
  and rich motion. Minimal work demands precision in spacing, typography, alignment, and detail.
  Intentionality matters more than intensity.

Calibrate against current convergence, not only yesterday's clichés. Common model outputs include a
warm cream field with a high-contrast serif and terracotta accent, a near-black field with one acid
accent, and a broadsheet layout with hairline rules and dense columns. Default sans faces, purple
gradients, uniformly rounded cards, and centered compositions are other familiar attractors. These
directions are legitimate when the subject calls for them; they are failures when selected because
the model reaches them for unrelated products. Do not replace one overused default with another or
repeat a signature from previous work without subject-specific cause.

Work in two passes. First, make a compact design plan containing:

- four to six named colors with concrete values or accepted token references;
- two or more type roles with their scale and relationship;
- a layout concept expressed in concise prose and, when useful, small ASCII wireframes;
- a motion approach and the states it affects;
- one signature element the interface should be remembered by.

Then critique the plan against the accepted sources. Replace any choice that could belong unchanged
to an unrelated product. Resolve contradictions between the premise and the individual choices
before changing production code. Present coherent candidates rather than undigested brainstorming.
When a concrete reaction is needed, use the related prototype procedure if the navigator exposes it;
otherwise report the unresolved design decision.

## Build and critique

Follow the accepted plan precisely enough that its point of view survives implementation. Derive
local choices from its tokens and relationships instead of improvising each component separately.
Reuse appropriate components and tokens, but refactor or extend them when forcing the design through
an unsuitable abstraction would erase the accepted direction.

Keep dark and light themes coherent. Use adaptive units and account for display sizes, real content
variation, wrapping, overflow, loading, empty, error, disabled, and intermediate states. Keep the
interface reactive as data changes. Use current, legible controls with clear affordances. Preserve
keyboard operation, visible focus, reduced motion, and applicable accessibility needs.

Treat words as design material. Write from the consumer's side of the interface using specific plain
language and active voice. Name an action the same way through the interaction. Errors explain what
happened and how to recover; empty states direct the next useful action. Match tone to the product,
use sentence case, and remove filler. Each element does one job. Avoid em dashes, sales pitch
language, implementation terminology, design rationale, and feature inventories in consumer-facing
prose.

Render and inspect the interface throughout the build across relevant interactions, themes, sizes,
and states. Inspect both its appearance and an available structural representation for hierarchy,
semantics, alignment, clipping, contrast, focus, and reflow. Watch for style precedence that causes
rules to cancel or override one another. Critique the result against the premise, remove one
unnecessary accessory, and refine the details that carry the design.

This inspection guides iteration but does not establish completion evidence. Do not let refinement
change accepted behavior, expand scope, or conceal a missing product decision.

## Result

Include the accepted or applied direction, its existing constraints and sources, the compact design
plan, the visual and writing choices that constrain later work, affected surfaces, and any unresolved
design decision. Identify the rendered states that later work must verify.
