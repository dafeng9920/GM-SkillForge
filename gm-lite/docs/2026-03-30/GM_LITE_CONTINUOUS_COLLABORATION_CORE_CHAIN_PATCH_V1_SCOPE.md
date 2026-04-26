# GM-LITE Continuous Collaboration Core Chain Patch V1 Scope

## Module

- `gm_lite_continuous_collaboration_core_chain_patch_v1`

## Intent

Patch the core breaks that prevent `GM-LITE` from becoming a true continuous collaboration chain between dialogue, Codex output, `.gm_bus`, AI legion execution, writeback, and resumed dialogue.

## Primary Goal

Repair the four core gaps surfaced by `OR1`:

- Codex output is not protocolized
- AI legion discovery / claim is not evidenced as automatic
- context continuity is not preserved across turns
- status transitions still break into manual boundaries

## In Scope

- `CodexOutput` protocol object definition and write path
- AI legion auto-discovery / claim evidence path
- context binding and restoration path
- controlled automatic state transition path

## Out of Scope

- broad UI redesign
- replacing `.gm_bus`
- SkillForge governance relocation
- generic agent-platform expansion

## Success Test

This cut succeeds only if the collaboration chain no longer depends on repeated manual re-creation of intent, handoff, and context at every boundary.
