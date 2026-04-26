# GM_LITE_RUNTIME_EXECUTION_BRIDGE_V1_SCOPE

## Goal
- Wire the existing `LegionRuntimeDriver` into the VS Code extension activation / auto-progression path so the runtime can actually execute claims and emit writebacks.

## Why this exists
- Claim refresh and session binding are already fixed.
- The remaining blocker is that `LegionRuntimeDriver` exists in `src/gm_bus/runtime/LegionRuntimeDriver.ts` but is not connected to the extension startup chain.
- Without this bridge, `claim -> execute -> submitResult -> writeback` stays theoretical.

## In scope
- Extension startup / activation wiring.
- Auto-progression to runtime-driver handoff.
- Current participant / session context passed into the runtime path.
- Verifiable writeback emission for the current task chain.

## Out of scope
- Algorithm / math backlog.
- New task formats.
- UI redesign beyond status visibility needed for verification.
- Rewriting the existing bus protocol layer.

## Success criteria
- Extension activation can start the runtime bridge without manual intervention.
- A claimed task reaches execution and submits a writeback.
- Console / worksurface can surface the current chain rather than only claim/session artifacts.
- The change is bounded and does not bypass fail-closed behavior.
