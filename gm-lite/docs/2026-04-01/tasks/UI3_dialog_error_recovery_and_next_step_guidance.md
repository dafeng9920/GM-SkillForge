你是任务 `UI3` 的执行者 `Kior-B`。

你只做 execution，不做 review，不做 compliance。
权威项目树以 `D:\\gm-lite` 为准。

## PreflightChecklist
- [ ] 这次修改是否只补对话框内的错误恢复与下一步指引。
- [ ] 是否保持主对话框可直接告诉用户“卡在哪、怎么继续”。
- [ ] 是否保持 fail-closed：失败时不显示虚假成功。

## ExecutionContract
- Inputs:
  - `D:\\gm-lite\\vscode-extension\\src\\views\\MainWorkbenchConsoleProvider.ts`
  - `D:\\gm-lite\\vscode-extension\\src\\core\\HumanFirstFeedbackService.ts`
  - `D:\\gm-lite\\vscode-extension\\src\\core\\ContextAwareSuggestions.ts`
  - `D:\\gm-lite\\vscode-extension\\src\\commands\\FollowbackCommand.ts`
- Constraints:
  - Do not expand into new navigation surfaces.
  - Do not rework runtime bridge internals.
  - Do not hide failure states behind generic success messages.
- Rollback plan:
  - If a recovery path cannot be determined, explicitly show the chain blockage and keep the existing behavior intact.

## RequiredChanges
- Categorize the common failure states in the dialog:
  - unclaimed
  - claimed but not executed
  - executed but no writeback
  - writeback exists but not in current chain
- For each state, present a direct recovery action.
- Ensure the dialog output is actionable, not just descriptive.
- Write the execution report to:
  - `D:\\gm-lite\\docs\\2026-04-01\\verification\\gm_lite_dialog_first_triad_surface_fix\\UI3_execution_report.md`
- Include at least one real `EvidenceRef` to code lines in `D:\\gm-lite`.

## Default next hop
- review -> `vs--cc1`
