# Runtime Checklist

## Fast Path

1. Search GM-Lite frame for `WV0`
2. Search GM-Lite frame for `webview script booted`
3. Search GM-Lite frame for `snapshot message received`
4. Search GM-Lite frame for `SNAPSHOT` or `TRIAD`
5. Search Extension Host for `WV2-FROM-WEBVIEW`

## Evidence Matrix

### Boot failed

- frontend `WV0` missing
- host `WV2-FROM-WEBVIEW` missing

### App script failed

- `WV0` present
- `webview script booted` missing

### Snapshot delivery failed

- `webview script booted` present
- `snapshot message received` missing
- backend may still emit `WV3-BACKEND refresh() sending snapshot`

### Render layer failed

- `snapshot message received` present
- page still broken
- inspect `SNAPSHOT render... failed` or `TRIAD Missing DOM nodes`

## Common File Targets

- `D:/gm-lite/vscode-extension/src/views/MainWorkbenchConsoleProvider.ts`
- `D:/gm-lite/vscode-extension/media/mainWorkbenchBootstrap.js`
- `D:/gm-lite/vscode-extension/media/mainWorkbenchConsoleApp.js`
- `D:/gm-lite/scripts/verify_main_workbench_webview.cjs`

## Packaging Confirmation

Installed extension should contain:

- `media/mainWorkbenchBootstrap.js`
- `media/mainWorkbenchConsoleApp.js`

Built package should pass:

- `npm run verify:webview`
- `npm run release:package`
