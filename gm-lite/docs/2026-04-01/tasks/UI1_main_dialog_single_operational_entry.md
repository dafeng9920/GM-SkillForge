你是任务 `UI1` 的执行者 `Kior-B`。

你只做 execution，不做 review，不做 compliance。
权威项目树以 `D:\\gm-lite` 为准。

## PreflightChecklist
- [ ] 这次修改是否只收敛主对话框，不扩散到算法/数学/新导航层。
- [ ] 是否保持 triad status panes 为辅助，而不是新增主入口。
- [ ] 是否保持 fail-closed：出错时只报告真实状态，不伪造成功。

## ExecutionContract
- Inputs:
  - `D:\\gm-lite\\vscode-extension\\src\\views\\MainWorkbenchConsoleProvider.ts`
  - `D:\\gm-lite\\vscode-extension\\src\\views\\ConsoleViewProvider.ts`
  - `D:\\gm-lite\\vscode-extension\\src\\views\\StatusViewProvider.ts`
  - `D:\\gm-lite\\vscode-extension\\src\\views\\EnhancedStatusViewProvider.ts`
  - `D:\\gm-lite\\vscode-extension\\src\\commands\\FollowbackCommand.ts`
  - `D:\\gm-lite\\vscode-extension\\src\\core\\HumanFirstFeedbackService.ts`
- Constraints:
  - Do not add new major navigation surfaces.
  - Do not move the triad status into the main interaction path.
  - Do not change the runtime bridge logic.
- Rollback plan:
  - If the consolidation weakens existing entry points, preserve them as secondary aliases and keep the main dialog primary.

## RequiredChanges
- Make one dialog the primary interaction point for instruction input, chain state, and error messages.
- Demote scattered action surfaces to auxiliary/secondary access.
- Ensure the dialog clearly reflects:
  - current chain state
  - next step
  - current blockage
- Write the execution report to:
  - `D:\\gm-lite\\docs\\2026-04-01\\verification\\gm_lite_dialog_first_triad_surface_fix\\UI1_execution_report.md`
- Include at least one real `EvidenceRef` to code lines in `D:\\gm-lite`.

## Default next hop
- review -> `vs--cc1`
