# GM_LITE_TASK_REALITY_AND_CONTROL_MODEL_PREPARATION_V1_BOUNDARY_RULES

## Boundary

This line is a **preparation and freezing line**, not a full implementation line.

It must:

- define minimum objects
- define minimum state/control semantics
- define cross-layer adjudication rules

It must not:

- build heavy runtime behavior
- add speculative UI surface area
- move governance into `GM-LITE`
- move task-reality ownership out of `GM-LITE`

## Hard Rules

1. No object may be left as free-form narrative if it is required by automation loop continuity.
2. No "human control" claim is valid unless it maps to an explicit control point or action type.
3. No "repair loop" claim is valid unless it maps to a defect object and re-entry condition.
4. No "next action" claim is valid unless it maps to a structured action object.
5. `GM-LITE` may define and expose these objects, but not become the final governance authority over them.

