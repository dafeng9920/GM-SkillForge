你是任务 `RB1` 的执行者 `Kior-B`。

你只做 execution，不做 review，不做 compliance。
权威项目树以 `D:\gm-lite` 为准。

## PreflightChecklist
- [ ] 这次修改是否只接通 runtime bridge，不扩散到算法/数学/文档 backlog。
- [ ] 目标路径是否仅限于 extension startup / auto-progression / runtime handoff。
- [ ] 是否保持 fail-closed：如果 driver 启动失败，不得伪造成功 writeback。

## ExecutionContract
- Inputs:
  - `D:\gm-lite\vscode-extension\src\extension.ts`
  - `D:\gm-lite\vscode-extension\src\core\AutoProgressionService.ts`
  - `D:\gm-lite\src\gm_bus\runtime\LegionRuntimeDriver.ts`
- Constraints:
  - Do not replace the bus protocol layer.
  - Do not fake writeback success.
  - Do not broaden scope to unrelated UI work.
- Rollback plan:
  - If the runtime bridge cannot be started safely, keep the system on the existing bounded auto-progression path and report the gap clearly.

## RequiredChanges
- Make the extension activation path actually instantiate or start the existing `LegionRuntimeDriver`.
- Ensure the runtime bridge is driven by the current participant / session context instead of remaining an isolated prototype.
- Ensure a claimed task can flow into execution and `submitExecutionResult()` without manual intervention.
- Write the execution report to:
  - `D:\gm-lite\docs\2026-04-01\verification\gm_lite_runtime_execution_bridge_fix\RB1_execution_report.md`
- Include at least one real `EvidenceRef` to code lines in `D:\gm-lite`.

## Default next hop
- review -> `vs--cc1`
