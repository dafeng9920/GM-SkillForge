# GM-LITE Human Control Flow Integration Patch V1 Scope

## Module

- `gm_lite_human_control_flow_integration_patch_v1`

## Intent

Integrate existing human control runtime primitives into the real operator execution flow.

## Primary Goal

Make control points affect live flow rather than remain passive infrastructure.

## In Scope

- blocking control point checks in operator loop flow
- visible paused / blocked state transition
- redirect affecting next hop or next action path
- resume affecting paused flow continuation

## Out of Scope

- broad scheduler expansion
- autonomous policy engine
- governance relocation
- full workflow redesign

## Success Test

The patch succeeds only if `WS3` can verify live flow impact, not just primitive existence.
