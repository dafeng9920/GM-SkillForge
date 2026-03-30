# GM-LITE Conversational Worksurface Minimal Implementation V1 Acceptance

## Acceptance Targets

1. plugin can be opened through one obvious worksurface entry
2. user can type / submit a prompt or instruction inside the plugin surface
3. recent outputs / writebacks / task snapshot are visible inside the same surface
4. high-frequency actions are clickable without command-palette dependency
5. the surface is judged meaningfully closer to "open-and-use" than the prior explorer/output split

## Fail Conditions

- console view exists but is not reachable from the main plugin route
- prompt box exists but cannot trigger meaningful actions
- outputs remain visible only in raw diagnostic channels
- the user still has to bounce across multiple scattered surfaces for basic operation
- implementation looks conversational but weakens task reality / evidence clarity
