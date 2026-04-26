# GM_LITE_RUNTIME_EXECUTION_BRIDGE_V1_TASK_BOARD

## Scope
- See `GM_LITE_RUNTIME_EXECUTION_BRIDGE_V1_SCOPE.md`.

## Task order
- Single execution line: `RB1`.
- Run as triad: execution -> review -> compliance.

## RB1
- Title: Legion runtime driver activation bridge
- Purpose: Connect `LegionRuntimeDriver` to extension startup / auto-progression so claims can actually execute and write back.
- Expected owner split:
  - execution: Kior-B
  - review: vs--cc1
  - compliance: Kior-C

## Verification target
- `RB1 = PASS` only if the runtime driver is actually started / wired and produces a writeback for the current chain.
