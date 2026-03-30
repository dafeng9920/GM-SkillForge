# GM-LITE Console Low Friction Action Patch V1 Scope

## Module

- `gm_lite_console_low_friction_action_patch_v1`

## Intent

Turn the visible `GM-Lite Console` from "buttons that call legacy command paths" into a lower-friction usable action surface.

## Primary Goal

Make the highest-frequency console buttons execute with context from the console snapshot instead of falling back to empty-selection or extra-step flows.

## In Scope

- direct `Read Writeback` with latest writeback context
- direct `Send Packet` with latest / only usable outbox packet
- explicit action feedback inside console transcript
- minimal hardening for `Open Task Board` / `Open GM Bus Folder`

## Out of Scope

- broad chat intelligence redesign
- new task orchestration logic
- marketplace / publish work
- replacing the underlying writeback / send operators

## Success Test

This cut succeeds only if the console buttons feel meaningfully more direct than the legacy command flow and no longer fail on obvious available context.
