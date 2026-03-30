# GM_LITE_TASK_REALITY_AND_CONTROL_MODEL_PREPARATION_V1_ACCEPTANCE

## Acceptance

This line passes only if it produces all of the following:

1. A minimum `TaskArtifact` model that is sufficient to reduce chat dependence.
2. A minimum defect / repair / re-entry model.
3. A minimum `RunState` and `NextAction` model.
4. A minimum `HumanControlPoint` model with explicit intervention semantics.
5. A written adjudication rule for layer conflicts involving:
   - `GM-LITE`
   - `superpowers`
   - `SkillForge`
6. Clear anti-drift language upgraded from naming to reviewable criteria.
7. Explicit treatment of the "user-perceived weak shell" failure mode as a rejected target state.

If any of these remain free-form only, the line is `REQUIRES_CHANGES`.
