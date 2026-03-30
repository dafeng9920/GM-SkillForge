# GM_LITE_PLUGIN_WRITEBACK_NAVIGATION_TYPED_STATUS_PATCH_V1_BOUNDARY_RULES

## Boundary

- Fix only the typed-status design gap exposed by `TP2`.
- Do not keep `string | null` as the main failure discriminator.
- Prefer explicit enum/union-like states over free-text control flow.
- Preserve visible operator semantics.

