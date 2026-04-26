你是任务 `UI2` 的执行者 `Kior-B`。

你只做 execution，不做 review，不做 compliance。
权威项目树以 `D:\\gm-lite` 为准。

## PreflightChecklist
- [ ] 这次修改是否只做三权状态窗，不扩散到主对话框逻辑。
- [ ] 这些状态窗是否只展示 execution / review / compliance 的状态、证据、下一跳。
- [ ] 是否保持 fail-closed：状态缺失时显示真实缺失，而不是默认成功。

## ExecutionContract
- Inputs:
  - `D:\\gm-lite\\vscode-extension\\src\\views\\MainWorkbenchConsoleProvider.ts`
  - `D:\\gm-lite\\vscode-extension\\src\\views\\EnhancedStatusViewProvider.ts`
  - `D:\\gm-lite\\vscode-extension\\src\\views\\StatusViewProvider.ts`
  - `D:\\gm-lite\\vscode-extension\\src\\views\\ConsoleViewProvider.ts`
- Constraints:
  - Do not add extra panes beyond the three triad panes.
  - Do not turn the panes into alternative primary entry points.
  - Do not alter runtime logic.
- Rollback plan:
  - If the triad panes become noisy, reduce them back to compact state-only views.

## RequiredChanges
- Ensure execution / review / compliance each have a dedicated compact status display.
- Surface only the current triad state and one clear next hop per pane.
- Keep the panes visually subordinate to the main dialog.
- Write the execution report to:
  - `D:\\gm-lite\\docs\\2026-04-01\\verification\\gm_lite_dialog_first_triad_surface_fix\\UI2_execution_report.md`
- Include at least one real `EvidenceRef` to code lines in `D:\\gm-lite`.

## Default next hop
- review -> `vs--cc1`
