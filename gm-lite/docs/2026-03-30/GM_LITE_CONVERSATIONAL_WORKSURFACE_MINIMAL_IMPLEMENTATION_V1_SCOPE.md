# GM-LITE Conversational Worksurface Minimal Implementation V1 Scope

## Module

- `gm_lite_conversational_worksurface_minimal_implementation_v1`

## Intent

Make `GM-LITE` feel like a Codex-style usable plugin surface: openable, conversational, output-visible, and click-usable from one place.

## Primary Goal

Reduce operator friction by making the main plugin route:

- open plugin
- enter prompt / instruction
- see current task and recent output
- click high-frequency actions
- stay inside one worksurface instead of bouncing across commands and raw output

## In Scope

- explorer-first `GM-Lite Console` view shell
- prompt/input surface inside plugin
- transcript / snapshot / output visibility in one surface
- quick actions for high-frequency paths
- validation of whether the surface is truly conversational and click-usable

## Out of Scope

- full Claude-Code-class chat replacement
- marketplace / publish work
- broad scheduler redesign
- upstream vault / keep implementation
- final governance relocation into plugin

## Success Test

This cut succeeds only if opening `GM-LITE` gives the operator one obvious surface where they can talk, see outputs, and trigger the next useful action without falling back to scattered command-palette usage.
