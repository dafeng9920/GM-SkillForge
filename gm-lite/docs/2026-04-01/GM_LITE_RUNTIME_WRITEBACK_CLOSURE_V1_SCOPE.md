# GM_LITE_RUNTIME_WRITEBACK_CLOSURE_V1_SCOPE

## Goal
- Close the remaining runtime gap so the current chain can produce a real execution result and writeback after claim, instead of stopping at discovery / claim / bridge initialization.

## Why this exists
- RB1 connected the runtime bridge.
- RB2 made `AutoProgressionService` consume the bridge.
- The remaining blocker is the actual execution-result closure: a claimed task still needs to reach `submitResult()` and generate a writeback that the current chain can read.

## In scope
- Runtime execution handoff after claim.
- Result submission into `.gm_bus/writeback`.
- Current chain scoping for writeback / followback.
- Fail-closed handling when execution cannot be completed.

## Out of scope
- Algorithm / math backlog.
- UI redesign.
- New task formats or new protocol layers.
- Reworking the already-passed claim refresh/session binding work.

## Success criteria
- A claimed task can reach execution-result submission.
- A real writeback artifact is produced for the current chain.
- Read Writeback / Followback can surface the new result without being trapped by history.
- The path remains bounded and fail-closed.
