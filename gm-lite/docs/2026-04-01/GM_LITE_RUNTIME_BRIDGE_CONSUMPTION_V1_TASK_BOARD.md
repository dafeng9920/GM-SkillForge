# GM_LITE_RUNTIME_BRIDGE_CONSUMPTION_V1_TASK_BOARD

## Scope
- See `GM_LITE_RUNTIME_BRIDGE_CONSUMPTION_V1_SCOPE.md`.

## Task order
- Single execution line: `RB2`.
- Run as triad: execution -> review -> compliance.

## RB2
- Title: AutoProgressionService consumes runtime bus adapter
- Purpose: Refactor the extension auto-progression path so it actually uses the runtime bridge (`IBusManager`) to drive discovery / claim / result submission.
- Expected owner split:
  - execution: Kior-B
  - review: vs--cc1
  - compliance: Kior-C

## Verification target
- `RB2 = PASS` only if `AutoProgressionService` is wired to the bridge and the bridge is consumed in the actual progression flow.
