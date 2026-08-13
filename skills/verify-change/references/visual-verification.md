# Visual verification checklist

Use this reference for GUI changes and accepted prototypes.

- Trigger the behavior exactly as requested rather than navigating to a convenient resulting state.
- Identify the interacted target using a stable accessible role, label, or test identifier.
- Assert the exact resulting state before taking a screenshot.
- For a focused change, capture only viewports and themes that can materially affect the requested result. Use the broader representative matrix for full-production verification.
- Exercise empty, populated, long-content, loading, error, disabled, and expanded states only when they can alter the changed behavior or layout.
- Inspect alignment, hierarchy, density, contrast, wrapping, overflow, clipping, and fixed or sticky elements.
- Compare accepted prototype references and the binding contract side by side.
- Save evidence in the active effort rather than a temporary directory when it forms part of acceptance.
