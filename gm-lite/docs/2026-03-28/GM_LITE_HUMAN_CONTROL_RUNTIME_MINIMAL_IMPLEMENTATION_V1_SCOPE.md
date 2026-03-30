# GM-LITE Human Control Runtime Minimal Implementation V1 Scope

## Module

- `gm_lite_human_control_runtime_minimal_implementation_v1`

## Intent

Fill the missing runtime layer between typed human control definitions and real usability validation.

## Primary Goal

Implement the minimum runtime path for:

- `inspect`
- `pause`
- `redirect`
- `resume`

so that `WS3` can verify actual usability instead of only type presence.

## In Scope

- minimal runtime action wiring for human control points
- plugin-surface binding for usable control actions
- visible state effect after control action
- narrow validation of control-path runtime behavior

## Out of Scope

- broad scheduler behavior
- autonomous orchestration expansion
- final governance decisions
- full conversational console
- broad UX redesign

## Success Test

This patch succeeds only if human control is no longer just typed but minimally runnable in the plugin.
