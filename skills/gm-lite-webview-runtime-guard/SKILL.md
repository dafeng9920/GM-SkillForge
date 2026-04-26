---
name: gm-lite-webview-runtime-guard
description: Diagnose, repair, and harden the GM-Lite main workbench webview runtime. Use when GM-Lite pages partially render, buttons stop responding, triad panes show `--`, state summary stays stale, `Only GM-Lite` filtering behaves inconsistently, or DevTools / Extension Host evidence must be collected for WV0/WV2 boot markers, snapshot delivery, CSP drift, resource path drift, and render-layer failures.
---

# GM-Lite Webview Runtime Guard

## Overview

Stabilize the GM-Lite main workbench webview by treating runtime failures as a three-hop chain:

1. boot
2. snapshot delivery
3. render layer

Do not jump to triad or backend conclusions until the earlier hop passes.

## Workflow

### 1. Classify the failure hop

Use these markers in order:

- `WV0`: external bootstrap loaded
- `WV2`: webview script booted
- `WV2 snapshot message received`
- `SNAPSHOT` / `TRIAD`: render-layer faults

Interpretation:

- no `WV0`: bootstrap did not load
- `WV0` but no `WV2`: main app script did not boot
- `WV2` but no `snapshot message received`: backend-to-frontend delivery failed
- snapshot received but page still broken: render layer failed

### 2. Verify both sides of the bridge

Check both:

- GM-Lite webview frame console
- Extension Host logs

Required evidence pairs:

- frontend: `[WV2] ...`
- host: `[WV2-FROM-WEBVIEW] ...`

Do not accept only one side when diagnosing runtime delivery.

### 3. Prefer installed-extension assets over workspace copies

When the webview loads scripts or media, bind resources to `extensionUri/media`.

Do not switch runtime asset loading back to workspace-relative paths such as:

- `workspaceRoot/vscode-extension/media`

That causes packaging drift and can make local dirty files override installed fixes.

### 4. Keep the main app external

Keep webview runtime logic in:

- `vscode-extension/media/mainWorkbenchBootstrap.js`
- `vscode-extension/media/mainWorkbenchConsoleApp.js`

Do not move the main runtime back into a large inline template script unless there is a very strong reason and the CSP is revalidated.

### 5. Preserve the guard markers

Do not remove these markers during refactors:

- `external bootstrap loaded`
- `webview script booted`
- `snapshot message received`

They are the shortest reliable proof chain for runtime health.

## Fix Rules

When repairing the webview:

- patch the smallest broken hop first
- repackage and reinstall before concluding the fix failed
- reload the VS Code window after installation
- reopen the GM-Lite Console and re-check `WV0` then `WV2`

If the page is normal again, write down:

- root cause
- changed files
- verification markers seen after reinstall

## Packaging Guard

Before packaging or publishing, run:

```powershell
npm run verify:webview
```

This must pass before:

- `npm run release:check`
- `npm run release:package`
- `npm run release:publish`

## References

Read these only when needed:

- `references/runtime-checklist.md`: fast failure-hop checklist and expected evidence
- `references/legion-prompts.md`: standard prompts for execution, review, and compliance passes
- `D:/gm-lite/docs/2026-04-04/verification/gm_lite_webview_runtime/WV3_fix_closure.md`: closure record for the real regression and fix
