# GM-LITE Console Interactive Workflow Hardening V1 Scope

## Module

- `gm_lite_console_interactive_workflow_hardening_v1`

## Intent

Harden `GM-Lite Console` from a low-friction action surface into a more natural interactive workflow surface.

## Primary Goal

Make the console better at:

- understanding prompt intent
- showing outputs and file destinations
- surfacing the next useful action
- reducing operator hesitation after each action

## In Scope

- prompt-to-action intent hardening
- clearer output / file visibility inside console
- next-action guidance after action completion
- validation of whether console now feels meaningfully more interactive

## Out of Scope

- full general-purpose chat assistant behavior
- replacing `.gm_bus` or task reality objects
- marketplace / publish work
- broad runtime orchestration redesign

## Success Test

This cut succeeds only if the operator can type or click inside the console and more reliably understand:

- what just happened
- what file or output was produced
- what the next useful action is
