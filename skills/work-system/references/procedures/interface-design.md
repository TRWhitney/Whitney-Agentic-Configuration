# Interface Design Procedure

Create or apply a recognizable visual identity. Preserve accepted intent, established visual
language, and product boundaries.

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
not invent it. Identify the missing decision and its effect. When accepted intent leaves a minor
visual choice open, use your judgment. Make one bold visual choice justified by the subject and
keep the rest of the design restrained.

## Plan a specific design

Choose a clear design direction. Lead the main view with the content, interaction, image, or
demonstration most characteristic of the subject. Use a centered headline, large metric,
supporting statistics, and gradient accent only when that structure fits the subject.

Develop each design axis deliberately:

- **Typography:** Choose two or more type roles that express the design direction. Define their
  relationship, scale, weight, width, spacing, and hierarchy. Give display text character without
  excess; keep body and utility text easy to read. Follow an established type system when one
  exists rather than changing it merely to appear novel.
- **Color and atmosphere:** Use a dominant palette with accents. Draw backgrounds, texture,
  depth, imagery, and contrast from the subject. Avoid spreading emphasis across many unrelated
  colors or adding effects that convey neither meaning nor atmosphere.
- **Composition:** Structure must communicate content relationships. Structural devices such as
  numbering, dividers, labels, and containers must encode real meaning. Numbering implies sequence
  and belongs only when content actually has that order. Each card must represent a genuine group
  rather than serve as the default container. Use asymmetry, overlap, density, or negative space
  when the design direction supports them, not as automatic signs of creativity.
- **Motion:** Motion must serve the subject, hierarchy, or interaction. Prefer one coordinated
  sequence over scattered animations. Use restraint when extra motion would distract from the
  subject or interaction. Preserve reduced motion and never make animation the only carrier
  of meaning.
- **Complexity:** Match complexity to the direction. Expressive work may justify layered composition
  and rich motion. Minimal work demands precision in spacing, typography, alignment, and detail.

Watch for overused model defaults, including recent ones. Common outputs include a
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
- one distinctive visual element.

Then critique the plan against the accepted sources. Replace any choice that could belong unchanged
to an unrelated product. Resolve contradictions between the design direction and individual
choices before changing production code. Present coherent candidates with enough detail to evaluate.
When a concrete reaction is needed, use the related prototype procedure if the navigator exposes it;
otherwise report the unresolved design decision.

## Build and critique

Preserve the accepted design direction during implementation. Use the plan's tokens and
relationships to guide component choices.
Reuse appropriate components and tokens, but refactor or extend them when forcing the design through
an unsuitable abstraction would erase the accepted direction.

Keep dark and light themes coherent. Use adaptive units and account for display sizes, real content
variation, wrapping, overflow, loading, empty, error, disabled, and intermediate states. Keep the
interface reactive as data changes. Use current, legible controls with clear affordances. Preserve
keyboard operation, visible focus, reduced motion, and applicable accessibility needs.

Write interface text from the consumer's perspective, using specific plain language and active
voice. Name an action the same way through the interaction. Errors explain what happened and how
to recover; empty states direct the next useful action. Match tone to the product,
use sentence case, and remove filler. Each element does one job. Avoid em dashes, sales pitch
language, implementation terminology, design rationale, and feature inventories in consumer-facing
prose.

Render and inspect the interface throughout the build across relevant interactions, themes, sizes,
and states. Inspect both its appearance and an available structural representation for hierarchy,
semantics, alignment, clipping, contrast, focus, and reflow. Watch for style precedence that causes
rules to cancel or override one another. Compare the result with the accepted design direction,
remove one unnecessary element, and refine the details that define the design.

This inspection guides iteration but does not establish completion evidence. Do not let refinement
change accepted behavior, expand scope, or conceal a missing product decision.

## Result

Include the accepted or applied direction, its existing constraints and sources, the compact design
plan, the visual and writing choices that constrain later work, affected views and components, and
any unresolved design decision. Identify the rendered states that later work must verify.
