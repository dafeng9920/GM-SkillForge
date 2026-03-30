# GM_LITE_PLUGIN_TASK_CONTEXT_AND_QUICK_ACTIONS_THIRD_CUT_V1_SCOPE

## Objective

Land the third usability cut for the installed `GM-Lite` VS Code plugin so the sidebar and command flow become faster, safer, and more task-context aware.

## In Scope

- packet JSON summary / content preview
- writeback-to-task-board navigation improvement
- quick paths for latest outbox / latest writeback / quick send / quick read
- preserve existing confirmation-before-send behavior
- preserve task-context-first interaction model

## Out of Scope

- new heavy dashboard UI
- automatic dispatch orchestration
- Marketplace work
- non-plugin Python shell refactor
- database or persistence layer changes

## Success Signal

The plugin should let the operator inspect packet intent faster, jump back to the related task faster, and execute the most common send/read actions with fewer manual steps.

