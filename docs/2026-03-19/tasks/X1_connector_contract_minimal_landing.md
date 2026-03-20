# 任务 X1

## 唯一事实源
- `docs/2026-03-19/《外部执行与集成最小落地模块 v1｜Codex 主控分派提示词》.md`
- `docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_SCOPE.md`
- `docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_BOUNDARY_RULES.md`

## 角色
- Execution: vs--cc1
- Review: Kior-A
- Compliance: Kior-C

## 目标
- 建立 connector contract 子面的最小目录骨架、最小接口合同与只读承接说明。

## 禁止项
- 不接真实外部系统
- 不引入 runtime
- 不实现裁决逻辑
- 不回改 frozen 主线

## 并行 / 串行依赖
- 并行（第一波）

## 标准写回路径
- execution: `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X1_execution_report.md`
- review: `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X1_review_report.md`
- compliance: `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X1_compliance_attestation.md`

## 发给 Execution 的提示词
```text
你是任务 X1 的执行者 vs--cc1。

你不是审查者，也不是合规官。
你的唯一目标是：完成 connector contract 子面的最小落地骨架。

必须产出：
- 子面目录/文件骨架
- connector contract 职责文档
- 与其余子面的连接说明

禁止：
- runtime
- 真实外部接入
- 裁决逻辑
- 改写 frozen 主线

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X1_execution_report.md`
```

## 发给 Review 的提示词
```text
你是任务 X1 的审查者 Kior-A。

你只做 review，不做 execution，不做 compliance。

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X1_review_report.md`

必须包含：
1. task_id: X1
2. reviewer / executor
3. PASS / REQUIRES_CHANGES / FAIL
4. connector contract 的审查重点
5. 最少 EvidenceRef
```

## 发给 Compliance 的提示词
```text
你是任务 X1 的合规官 Kior-C。

你只做 B Guard 式硬审。

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X1_compliance_attestation.md`

必须包含：
1. task_id: X1
2. compliance_officer / executor / reviewer
3. PASS / REQUIRES_CHANGES / FAIL
4. Zero Exception Directives 检查结果
5. 最少 EvidenceRef
```

