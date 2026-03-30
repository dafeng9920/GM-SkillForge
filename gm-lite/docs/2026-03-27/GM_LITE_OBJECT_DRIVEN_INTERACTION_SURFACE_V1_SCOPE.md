# GM_LITE_OBJECT_DRIVEN_INTERACTION_SURFACE_V1_SCOPE

## Goal

Turn the newly frozen object/control model into a real plugin interaction surface.

This line exists to move from:

- defined objects
- defined control points
- defined anti-drift rules

to:

- visible task objects
- visible run state
- visible next actions
- visible defect / repair path
- operator-usable control points inside the plugin

## In Scope

- render `TaskArtifact` as plugin-visible task surface
- render `RunState` / `NextAction` as operator-facing interaction units
- expose minimum `HumanControlPoint` actions in plugin UI
- expose defect / repair / re-entry path in minimal usable form
- keep interaction tied to `.gm_bus` / bridge / writeback reality

## Out of Scope

- heavy dashboarding
- scheduler / lifecycle engine
- final governance UI
- full conversational console
- superpowers-lite implementation

