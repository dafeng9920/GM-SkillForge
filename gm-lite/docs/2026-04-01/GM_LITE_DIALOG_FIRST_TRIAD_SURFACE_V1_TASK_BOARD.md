# GM_LITE_DIALOG_FIRST_TRIAD_SURFACE_V1_TASK_BOARD

## Scope
- See `GM_LITE_DIALOG_FIRST_TRIAD_SURFACE_V1_SCOPE.md`.

## Task order
- First wave: `UI1 + UI2`
- Second wave: `UI3`

## UI1
- Title: Main dialog as the single operational entry point
- Purpose: Collapse scattered interactive surfaces into one command/result/error dialog.
- Expected owner split:
  - execution: Kior-B
  - review: vs--cc1
  - compliance: Kior-C

## UI2
- Title: Three triad status panes
- Purpose: Show execution / review / compliance as small state panes, not as competing primary surfaces.
- Expected owner split:
  - execution: Kior-B
  - review: vs--cc1
  - compliance: Kior-C

## UI3
- Title: Dialog-driven error recovery and next-step guidance
- Purpose: Make the main dialog tell the user exactly where the chain is blocked and what to do next.
- Expected owner split:
  - execution: Kior-B
  - review: vs--cc1
  - compliance: Kior-C

## Verification target
- `UI1-UI3 = PASS` only if the UI clearly reflects the dialogue-first model and provides explicit recovery actions instead of only passive error text.
