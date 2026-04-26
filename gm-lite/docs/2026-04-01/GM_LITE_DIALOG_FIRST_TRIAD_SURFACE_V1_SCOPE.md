# GM_LITE_DIALOG_FIRST_TRIAD_SURFACE_V1_SCOPE

## Goal
- Reshape GM-Lite into a dialogue-first operational surface: one main dialog for commands/results/errors, plus three small triad status panes for execution / review / compliance.

## Why this exists
- The current UI is spread across too many entry points and feels like a click-only single-player page.
- The user-facing flow should match the actual operating model:
  - instruction input
  - dispatch
  - legion collaboration
  - triad verification
  - automatic flow continuity

## In scope
- Main dialog as the only primary interaction surface.
- Three small status panes for:
  - execution
  - review
  - compliance
- Explicit error-recovery states in the dialog.
- Clear next-step guidance in the dialog after each operation.

## Out of scope
- Algorithm / math backlog.
- New task semantics or protocol rewrites.
- Adding more surface area or more navigation layers.
- Reworking runtime bridge internals beyond what the UI needs to reflect state accurately.

## Success criteria
- Users can issue instructions and receive outcomes from one dialog.
- The three triad panes show only their own status, evidence, and next hop.
- On failure, the dialog states where the chain is blocked and what action to take next.
- The UI stops feeling like a scattered single-player click page.
