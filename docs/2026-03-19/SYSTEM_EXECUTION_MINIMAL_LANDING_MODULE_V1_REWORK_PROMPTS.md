# 系统执行层最小落地模块局部退回返工提示词 v1

适用范围：

- `T1 workflow`
- `T2 orchestrator`
- `T4 handler`
- `T5 api`

退回原因统一口径：

- 当前模块要求统一目标路径为 `skillforge/src/system_execution/`
- 你已提交的实现仍落在 `skillforge/src/system_execution_preparation/`
- 导致模块级导入链无法闭合
- 本次返工只允许修正“统一目标路径落位”与相关文档/导入引用
- 不允许扩范围，不允许进入 runtime，不允许进入外部集成，不允许改 frozen 主线

统一回收路径：

- 执行反馈：
  - `docs/2026-03-19/verification/system_execution_minimal_landing/T{N}_execution_report.md`
- 审查反馈：
  - `docs/2026-03-19/verification/system_execution_minimal_landing/T{N}_review_report.md`
- 合规反馈：
  - `docs/2026-03-19/verification/system_execution_minimal_landing/T{N}_compliance_attestation.md`
- 主控官终验：
  - `docs/2026-03-19/verification/system_execution_minimal_landing/T{N}_final_gate.md`

---

## 1. 发给 Antigravity-1（T1 Execution Rework）

```text
你是任务 T1 的执行者 Antigravity-1。

当前状态：主控官终验退回，原因不是职责越界，而是落位路径错误。

task_id: T1
返工目标:
- 将 workflow 最小落地骨架从
  skillforge/src/system_execution_preparation/workflow/
  迁移或重建到
  skillforge/src/system_execution/workflow/

本次只允许修正：
1. 统一目标路径落位
2. 相关导入引用
3. 相关职责文档与连接说明中的路径引用
4. 自检脚本中的路径引用
5. 执行报告更新

禁止项：
- 不得新增 runtime 逻辑
- 不得新增外部集成
- 不得改变 workflow 职责边界
- 不得修改 frozen 主线
- 不得借返工扩模块

你必须交付：
- skillforge/src/system_execution/workflow/ 最小骨架
- 更新后的职责文档与连接说明
- 更新后的自检结果
- 更新后的 docs/2026-03-19/verification/system_execution_minimal_landing/T1_execution_report.md

EvidenceRef 要求：
- 必须明确旧路径与新路径
- 必须给出迁移后导入/连接自检结果
```

## 2. 发给 Antigravity-2（T2 Execution Rework）

```text
你是任务 T2 的执行者 Antigravity-2。

当前状态：主控官终验退回，原因不是职责越界，而是落位路径错误。

task_id: T2
返工目标:
- 将 orchestrator 最小落地骨架从
  skillforge/src/system_execution_preparation/orchestrator/
  迁移或重建到
  skillforge/src/system_execution/orchestrator/

本次只允许修正：
1. 统一目标路径落位
2. 相关导入引用
3. 职责文档与连接说明中的路径引用
4. 自检脚本中的路径引用
5. 执行报告更新

禁止项：
- 不得新增治理裁决语义
- 不得新增 runtime 控制
- 不得新增外部集成
- 不得修改 frozen 主线
- 不得借返工扩模块

你必须交付：
- skillforge/src/system_execution/orchestrator/ 最小骨架
- 更新后的职责文档与连接说明
- 更新后的自检结果
- 更新后的 docs/2026-03-19/verification/system_execution_minimal_landing/T2_execution_report.md

EvidenceRef 要求：
- 必须明确旧路径与新路径
- 必须证明 orchestrator 仍不具备裁决权
- 必须给出迁移后导入/连接自检结果
```

## 3. 发给 Kior-B（T4 Execution Rework）

```text
你是任务 T4 的执行者 Kior-B。

当前状态：主控官终验退回，原因不是职责越界，而是落位路径错误。

task_id: T4
返工目标:
- 将 handler 最小落地骨架从
  skillforge/src/system_execution_preparation/handler/
  迁移或重建到
  skillforge/src/system_execution/handler/

本次只允许修正：
1. 统一目标路径落位
2. 相关导入引用
3. 职责文档与边界文档中的路径引用
4. 自检脚本中的路径引用
5. 执行报告更新

禁止项：
- 不得新增副作用动作
- 不得新增 runtime 分支控制
- 不得新增外部集成
- 不得修改 frozen 主线
- 不得借返工扩模块

你必须交付：
- skillforge/src/system_execution/handler/ 最小骨架
- 更新后的职责文档与边界文档
- 更新后的自检结果
- 更新后的 docs/2026-03-19/verification/system_execution_minimal_landing/T4_execution_report.md

EvidenceRef 要求：
- 必须明确旧路径与新路径
- 必须证明 handler 仍只做输入承接与调用转发
- 必须给出迁移后导入/连接自检结果
```

## 4. 发给 vs--cc3（T5 Execution Rework）

```text
你是任务 T5 的执行者 vs--cc3。

当前状态：主控官终验退回，原因不是职责越界，而是落位路径错误。

task_id: T5
返工目标:
- 将 api 最小落地骨架从
  skillforge/src/system_execution_preparation/api/
  迁移或重建到
  skillforge/src/system_execution/api/

本次只允许修正：
1. 统一目标路径落位
2. 相关导入引用
3. 职责文档与连接说明中的路径引用
4. 自检脚本中的路径引用
5. 执行报告更新

禁止项：
- 不得新增真实外部协议
- 不得新增外部集成
- 不得新增 runtime 逻辑
- 不得修改 frozen 主线
- 不得借返工扩模块

你必须交付：
- skillforge/src/system_execution/api/ 最小骨架
- 更新后的职责文档与连接说明
- 更新后的自检结果
- 更新后的 docs/2026-03-19/verification/system_execution_minimal_landing/T5_execution_report.md

EvidenceRef 要求：
- 必须明确旧路径与新路径
- 必须证明 api 仍不是外部集成层
- 必须给出迁移后导入/连接自检结果
```

---

## 5. 发给 Review Wing 的统一返工审查提示词

```text
你是系统执行层最小落地模块返工轮的审查者。

本轮只审查一件事：
- 退回任务是否已按统一目标路径 `skillforge/src/system_execution/` 重交

你不得新增需求，不得借审查扩模块。

统一审查重点：
1. 新路径是否正确
2. 旧路径引用是否已清理或明确退役
3. 文档与骨架路径是否一致
4. 导入/连接自检是否与新路径一致
5. 返工后是否仍保持原职责边界

输出：
- 更新对应 `T{N}_review_report.md`
- 明确写出：
  - PASS / REQUIRES_CHANGES / DENY
  - 是否还存在路径阻断问题
```

## 6. 发给 Kior-C 的统一返工合规提示词

```text
你是系统执行层最小落地模块返工轮的合规官 Kior-C。

本轮只做 B Guard 式硬审，不做执行，不做普通质量审查。

本轮只检查：
1. 返工是否只修正统一目标路径落位
2. 返工过程中是否引入 runtime
3. 返工过程中是否引入外部执行/集成
4. 返工过程中是否倒灌 frozen 主线
5. 返工过程中是否把 workflow/orchestrator 变成裁决者
6. 返工过程中是否把 service/handler/api 变成真实执行层

Zero Exception Directives：
- 只要返工借机扩模块，直接 FAIL
- 只要返工进入 runtime/external integration，直接 FAIL
- 只要返工修改 frozen 主线，直接 FAIL

输出：
- 更新对应 `T{N}_compliance_attestation.md`
- 必须明确写出 PASS 或 FAIL
```

## 7. 主控官回收规则

- 仅当以下条件同时成立，Codex 才重新做终验：
  - 新路径已统一到 `skillforge/src/system_execution/`
  - `execution_report / review_report / compliance_attestation` 全部更新
  - 模块级导入链可闭合
- 若仍存在路径不统一：
  - 直接再次 `REQUIRES_CHANGES`
