你是任务 `RB3` 的执行者 `Kior-B`。

你只做 execution，不做 review，不做 compliance。
权威项目树以 `D:\\gm-lite` 为准。

## PreflightChecklist
- [ ] 这次修改是否只补 runtime execution-result closure，不扩散到算法/数学/文档 backlog。
- [ ] 目标路径是否仅限于 claim -> execution -> submitResult -> writeback。
- [ ] 是否保持 fail-closed：执行失败时不得伪造写回成功。

## ExecutionContract
- Inputs:
  - `D:\\gm-lite\\vscode-extension\\src\\core\\AutoProgressionService.ts`
  - `D:\\gm-lite\\vscode-extension\\src\\core\\BusManagerAdapter.ts`
  - `D:\\gm-lite\\src\\gm_bus\\runtime\\LegionRuntimeDriver.ts`
  - `D:\\gm-lite\\vscode-extension\\src\\extension.ts`
- Constraints:
  - Do not rewrite the bus protocol layer.
  - Do not fake a writeback artifact.
  - Do not widen scope to unrelated UI work.
- Rollback plan:
  - If execution handoff cannot be safely wired, preserve the existing bridge consumption path and report the missing closure explicitly.

## RequiredChanges
- Make the post-claim runtime path able to hand off into actual execution-result submission.
- Ensure the bridge/runtime path emits a real writeback artifact for the current task chain.
- Preserve current participant / session context through execution-result submission.
- Keep fail-closed behavior if execution cannot be performed.
- Write the execution report to:
  - `D:\\gm-lite\\docs\\2026-04-01\\verification\\gm_lite_runtime_writeback_closure_fix\\RB3_execution_report.md`
- Include at least one real `EvidenceRef` to code lines in `D:\\gm-lite`.

## Default next hop
- review -> `vs--cc1`
