# GM_LITE_PLUGIN_TASK_CONTEXT_AND_QUICK_ACTIONS_THIRD_CUT_V1_BOUNDARY_RULES

## Boundary

- Work only inside the current `GM-Lite` VS Code plugin surface.
- Keep the current minimal plugin shape; do not expand into a large UI rewrite.
- Do not remove existing confirmation-before-send protection.
- Do not break existing `gmLite.status`, `gmLite.state`, `gmLite.action.*`, sidebar, or task-context flows.

## Protected Constraints

- No fabricated task linkage.
- No silent auto-send.
- No hidden mutation of `.gm_bus` state.
- No scope drift into public Marketplace release work.

