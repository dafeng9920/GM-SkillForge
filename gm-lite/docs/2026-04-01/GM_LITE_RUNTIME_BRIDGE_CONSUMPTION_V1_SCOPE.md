# GM_LITE_RUNTIME_BRIDGE_CONSUMPTION_V1_SCOPE

## Goal
- Make `AutoProgressionService` consume the runtime bridge (`busAdapter` / `IBusManager`) so auto-progression can drive the real claim → execution → submitResult path instead of staying on direct file operations.

## Why this exists
- RB1 connected the runtime bridge to extension activation.
- The remaining gap is that the bridge is initialized but not consumed by `AutoProgressionService`.
- Without this, the plugin still stops at discovery / claim refresh and does not fully reach runtime writeback from the bridge path.

## In scope
- Dependency injection or service exposure for `busAdapter`.
- `AutoProgressionService` read/claim/writeback path consumption.
- Bounded handoff from auto-progression to runtime bridge.
- Fail-closed behavior if the bridge is unavailable.

## Out of scope
- Algorithm / math backlog.
- New UI redesign.
- Reworking unrelated task formats.
- Replacing the bus protocol layer.

## Success criteria
- `AutoProgressionService` calls the runtime bridge instead of only direct file operations.
- The active/current participant and session are preserved through the bridge path.
- The bridge path remains bounded and does not silently fake success.
- The change is verifiable with real code evidence in `D:\gm-lite`.
