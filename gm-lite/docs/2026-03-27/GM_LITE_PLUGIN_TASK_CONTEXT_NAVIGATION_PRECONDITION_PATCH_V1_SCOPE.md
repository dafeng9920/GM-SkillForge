# GM_LITE_PLUGIN_TASK_CONTEXT_NAVIGATION_PRECONDITION_PATCH_V1_SCOPE

## Objective

Patch the missing preconditions that blocked `TC2_writeback_to_task_context_navigation`.

## In Scope

- minimal task-context type or data contract needed by navigation
- minimal navigation helper needed by plugin-side task jump flow
- minimal handling for missing / latest writeback discovery
- only the dependency slice required to unblock `TC2`

## Out of Scope

- full task board redesign
- full writeback browser UI
- broader plugin command redesign
- Marketplace / packaging work

