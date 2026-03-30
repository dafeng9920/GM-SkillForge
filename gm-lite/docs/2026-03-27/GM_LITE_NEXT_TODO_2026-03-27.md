# GM-LITE Next TODO - 2026-03-27

## Today Closed

- `GM-LITE` VS Code plugin private local-use path is now effectively landed.
- `.vsix` packaging and local installation path are usable.
- Activity bar icon and minimal sidebar entry are visible and working.
- Local long-term self-use release line has passed.
- Marketplace code-side readiness has passed.
- Marketplace public release is still blocked only by platform-side actions:
  - publisher registration
  - PAT configuration

## Current True State

- `private_local_use = completed`
- `marketplace_public_release = not_required_for_now`
- `platform_publish_path = optional / deferred`

## Tomorrow Mainline

Do **not** continue Marketplace publish work first.

Priority should switch back to reducing manual control load inside `GM-LITE`.

Recommended next line:

- `gm_lite_operator_load_reduction_preparation_v1`

Focus:

1. Clarify which operator actions are still manual high-frequency work.
2. Identify which of those can move into plugin-visible controls first.
3. Define the first low-risk automation slice that reduces human forwarding / status checking work.
4. Keep core assets protected while increasing process visibility.

## Tomorrow Candidate Modules

Preferred order:

1. `gm_lite_operator_load_reduction_preparation_v1`
2. `gm_lite_reverse_semantic_echo_preparation_v1` (only if needed for visibility design)
3. `gm_lite_document_status_normalization_v1` (after next mainline, not before)

## Explicit Non-Priority

Do not prioritize tomorrow:

- Marketplace public publish
- publisher registration
- PAT setup
- document-wide cleanup sweep before next feature line

## Practical Goal

Tomorrow's target is not "more packaging".

Tomorrow's target is:

> reduce operator manual burden and move `GM-LITE` one step closer to real workflow relief.

