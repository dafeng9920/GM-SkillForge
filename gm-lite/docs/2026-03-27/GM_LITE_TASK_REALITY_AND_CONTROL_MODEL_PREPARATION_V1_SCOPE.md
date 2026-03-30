# GM_LITE_TASK_REALITY_AND_CONTROL_MODEL_PREPARATION_V1_SCOPE

## Goal

Convert the current high-maturity role definition of `GM-LITE` into a harder product/governance foundation by freezing the minimum object model and control model required for:

- shared task reality
- defect-driven repair / re-entry
- visible next-action flow
- explicit human control points

## In Scope

- `TaskArtifact` minimum object model
- `BoundarySpec` / `AcceptanceSpec` minimum shape
- `DefectRecord` / `RepairInstruction` / `ReEntryCondition`
- `RunState` / `NextAction` / `HumanControlPoint`
- bridge-visible return object relationship
- boundary adjudication rules for `GM-LITE / superpowers / SkillForge`
- anti-drift upgrade from named wrong-shapes to reviewable rejection criteria
- framing of the "user-perceived weak shell" failure mode for later plugin work

## Out of Scope

- full UI implementation
- heavy scheduler
- autonomous lifecycle engine
- final governance implementation
- superpowers-lite implementation
- SkillForge solidification implementation

## Why Now

Current risk is no longer pure direction drift. The risk is:

> document maturity is now ahead of mechanism maturity.

This line exists to close that gap before `GM-LITE` drifts into:

- status shell
- chat-dependent pseudo task reality
- blind repair loop
- fake human control
- architecturally strong but user-perceived weak shell
