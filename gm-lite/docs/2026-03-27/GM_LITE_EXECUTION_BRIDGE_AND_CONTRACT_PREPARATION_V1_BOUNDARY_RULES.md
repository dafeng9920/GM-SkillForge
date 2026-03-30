# GM_LITE_EXECUTION_BRIDGE_AND_CONTRACT_PREPARATION_V1_BOUNDARY_RULES

## Boundary

- `gm-lite` remains the shared task reality layer.
- `superpowers`-class systems remain execution methodology only.
- `SkillForge` remains audit/permit only.
- The bridge must stay thin:
  - translate
  - create workspace
  - absorb standard callback objects

## Protected Constraints

- no executor direct mutation of `.gm_bus` global state
- no Bridge expansion into a second orchestration kernel
- no SkillForge dependency on free-form executor output
- no heavy runtime work in this preparation module

