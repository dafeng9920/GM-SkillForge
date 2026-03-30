# GM-LITE Self Running Closure Patch V1 Scope

## Module

- `gm_lite_self_running_closure_patch_v1`

## Intent

Close the two remaining blockers discovered by `SR1-SR2`:

- automatic bounded task progression
- automatic writeback / followback return to the work surface

## Primary Goal

Move `GM-LITE` from partially self-running to a minimally closed self-running loop.

## In Scope

- bounded automatic progression wiring
- automatic return-to-surface path for writeback / followback
- visible loop closure without hidden autonomy
- re-entry path for `SR1` and `SR2`

## Out of Scope

- heavy scheduling engine
- broad orchestration rewrite
- cloud / website integration
- generic chat console work

## Success Test

This patch succeeds only if `SR1` and `SR2` can re-enter with their core acceptance blockers removed.
