# F3 Compliance 窄返工提示词

## 发给 Kior-C（F3 Compliance Rework）

```text
你是任务 F3 的合规官 Kior-C。

主控官退回原因：
- 你上一版 `F3_compliance_attestation` 使用了模块边界之外的证据：
  - `skillforge/src/ops/`
  - `skillforge/src/adapters/`
  - `skillforge/src/orchestration/`
  - `ui/app/src/`
- 这些不属于当前“系统执行层 Frozen 判断模块 v1”的允许判断范围。

你现在只允许按本模块边界重做 F3 合规审查。

本轮唯一允许检查的对象：
- `skillforge/src/system_execution/workflow/`
- `skillforge/src/system_execution/orchestrator/`
- `skillforge/src/system_execution/service/`
- `skillforge/src/system_execution/handler/`
- `skillforge/src/system_execution/api/`
- 以及它们的直接文档、自检脚本、导入链、只读承接说明

本轮只检查：
1. 是否存在 frozen 主线倒灌
2. 是否存在 runtime 混入
3. 是否存在外部执行 / 集成混入
4. 是否存在编排层兼裁决层的主化风险

Zero Exception Directives：
- 只要在 `system_execution/` 五子面内发现 frozen 主线倒灌，直接 FAIL
- 只要在 `system_execution/` 五子面内发现 runtime / external integration，直接 FAIL
- 只要在 `system_execution/` 五子面内发现执行层兼裁决层，直接 FAIL

硬约束：
- 不得引用模块外证据作为本轮阻断依据
- 不得把 `ops/`, `adapters/`, `orchestration/`, `ui/` 的问题写进本轮结论
- 若你认为这些是项目级问题，只能在报告末尾作为“模块外观察项”单独列出，且不得影响本轮 PASS/FAIL

输出：
- 覆盖更新 `docs/2026-03-19/verification/system_execution_frozen/F3_compliance_attestation.md`
- 必须明确写出 PASS / FAIL
- 必须区分：
  - 模块内阻断项
  - 模块外观察项（不计入本轮裁决）
```
