# GM-LITE Surface Return Identity Patch V1 Scope

## Module

- `gm_lite_surface_return_identity_patch_v1`

## Intent

Repair the identity-chain break discovered by `SR2` so writeback and followback can return to the correct work surface.

## Primary Goal

Make work-surface return identity survive task completion and remain readable by return-loop logic.

## In Scope

- `intent_trace_id` propagation in writeback path
- surface-return identity in summary objects
- return matching logic not dependent on active-task state
- followback visibility rule correction

## Out of Scope

- broad writeback redesign
- broad state model redesign
- scheduler or orchestration work
- unrelated UI expansion

## Success Test

The patch succeeds only if `SR2` can re-enter with surface return identity preserved end-to-end.
