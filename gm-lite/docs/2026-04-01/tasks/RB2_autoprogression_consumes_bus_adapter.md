你是任务 `RB2` 的执行者 `Kior-B`。

你只做 execution，不做 review，不做 compliance。
权威项目树以 `D:\\gm-lite` 为准。

## PreflightChecklist
- [ ] 这次修改是否只做 `AutoProgressionService` 对 `busAdapter` / `IBusManager` 的消费接管。
- [ ] 目标路径是否仅限于 extension auto-progression / runtime handoff。
- [ ] 是否保持 fail-closed：若 bridge 不可用，不得伪造 writeback 成功。

## ExecutionContract
- Inputs:
  - `D:\\gm-lite\\vscode-extension\\src\\core\\AutoProgressionService.ts`
  - `D:\\gm-lite\\vscode-extension\\src\\core\\BusManagerAdapter.ts`
  - `D:\\gm-lite\\vscode-extension\\src\\extension.ts`
- Constraints:
  - Do not expand into algorithm/math backlog.
  - Do not remove the bounded behavior of auto progression.
  - Do not fake runtime execution or writeback results.
- Rollback plan:
  - If bridge consumption cannot be wired safely, preserve existing behavior and report the gap explicitly.

## RequiredChanges
- Inject or expose the `busAdapter` so `AutoProgressionService` can consume it.
- Replace direct file-system claim/writeback operations with the bridge path where appropriate.
- Ensure current participant / session context is preserved through the bridge.
- Keep the existing bounded discovery semantics, but let the bridge own the execution handoff.
- Write the execution report to:
  - `D:\\gm-lite\\docs\\2026-04-01\\verification\\gm_lite_runtime_bridge_consumption_fix\\RB2_execution_report.md`
- Include at least one real `EvidenceRef` to code lines in `D:\\gm-lite`.

## Default next hop
- review -> `vs--cc1`
