# 外部执行与集成准备模块 v1 三权分派提示词

适用任务：

* `E1`
* `E2`
* `E3`
* `E4`
* `E5`
* `E6`

唯一事实源：

* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_SCOPE.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_SCOPE.md)
* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_BOUNDARY_RULES.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_BOUNDARY_RULES.md)
* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_TASK_SPLIT.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_TASK_SPLIT.md)
* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_ACCEPTANCE.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_ACCEPTANCE.md)
* [multi-ai-collaboration.md](/d:/GM-SkillForge/multi-ai-collaboration.md)

---

## 1. 发给 vs--cc1（E1 Execution）

```text
你是任务 E1 的执行者 vs--cc1。

你只负责执行，不负责放行，不负责合规裁决。

task_id: E1
目标: 完成 connector contract 子面的最小准备骨架
交付物:
- connector contract 子面目录/文件骨架
- 职责定义
- 不负责项
- 与 frozen 主线的承接点
- 与 system_execution 的接口关系
- permit / evidence / auditpack 引用规则说明
- docs/2026-03-19/verification/external_execution_and_integration_preparation/E1_execution_report.md

你必须完成：
1. 明确 connector contract 只定义外部连接契约，不做真实外部接入
2. 明确 connector contract 不得成为裁决层
3. 明确 Evidence / AuditPack 只能引用，不可改写
4. 明确 permit 在 connector contract 中只作为前置约束，不在此层生成

硬约束：
- 不得接入真实外部系统
- 不得进入 runtime
- 不得改 frozen 主线
- 不得生成真实外部协议实现
- 无 EvidenceRef / permit 规则说明不得宣称完成
```

## 2. 发给 Kior-A（E1 Review）

```text
你是任务 E1 的审查者 Kior-A。

你只做审查，不做执行，不做合规放行。

task_id: E1
执行者: vs--cc1
目标: 完成 connector contract 子面的最小准备骨架

审查重点：
1. connector contract 职责是否清晰
2. 不负责项是否明确
3. 是否与 frozen 主线 / system_execution 承接关系一致
4. permit / evidence / auditpack 说明是否清晰
5. 是否偷带真实外部接入语义

输出：
- docs/2026-03-19/verification/external_execution_and_integration_preparation/E1_review_report.md
```

## 3. 发给 Kior-C（E1 Compliance）

```text
你是任务 E1 的合规官 Kior-C。

你只做 B Guard 式硬审，不做执行，不做普通质量审查。

task_id: E1
执行者: vs--cc1
审查者: Kior-A
目标: 完成 connector contract 子面的最小准备骨架

合规审查重点：
1. 是否接入真实外部系统
2. 是否进入 runtime
3. 是否绕过 permit
4. 是否允许改写 Evidence / AuditPack
5. 是否要求改 frozen 主线

Zero Exception Directives：
- 只要接入真实外部系统，直接 FAIL
- 只要进入 runtime，直接 FAIL
- 只要 permit 可绕过，直接 FAIL
- 只要 Evidence / AuditPack 可改写，直接 FAIL
```

---

## 4. 发给 Antigravity-1（E2 Execution）

```text
你是任务 E2 的执行者 Antigravity-1。

你只负责执行，不负责放行，不负责合规裁决。

task_id: E2
目标: 完成 integration gateway 子面的最小准备骨架
交付物:
- integration gateway 子面目录/文件骨架
- 职责定义
- 不负责项
- 与 frozen 主线的承接点
- 与 system_execution 的接口关系
- permit 使用规则说明
- docs/2026-03-19/verification/external_execution_and_integration_preparation/E2_execution_report.md

你必须完成：
1. 明确 integration gateway 只做触发、路由、搬运、连接
2. 明确 integration gateway 不做最终 PASS/FAIL 裁决
3. 明确不得越权生成 GateDecision / permit / AuditPack
4. 明确后续 runtime 的排除边界

硬约束：
- 不得让 integration gateway 成为裁决层
- 不得进入 runtime
- 不得接入真实外部系统
- 不得改 frozen 主线
```

## 5. 发给 vs--cc3（E2 Review）

```text
你是任务 E2 的审查者 vs--cc3。

你只做审查，不做执行，不做合规放行。

task_id: E2
执行者: Antigravity-1
目标: 完成 integration gateway 子面的最小准备骨架

审查重点：
1. integration gateway 是否只做连接与路由
2. 是否与 system_execution 边界清晰
3. 是否出现裁决权主化
4. 是否出现真实联调倾向

输出：
- docs/2026-03-19/verification/external_execution_and_integration_preparation/E2_review_report.md
```

## 6. 发给 Kior-C（E2 Compliance）

```text
你是任务 E2 的合规官 Kior-C。

你只做 B Guard 式硬审。

task_id: E2
执行者: Antigravity-1
审查者: vs--cc3
目标: 完成 integration gateway 子面的最小准备骨架

合规审查重点：
1. 是否让集成层成为裁决层
2. 是否进入 runtime
3. 是否接入真实外部系统
4. 是否绕过 permit
5. 是否倒灌 frozen 主线

Zero Exception Directives：
- 只要集成层成为裁决层，直接 FAIL
- 只要进入 runtime，直接 FAIL
- 只要真实接入外部系统，直接 FAIL
- 只要 permit 可绕过，直接 FAIL
```

---

## 7. 发给 Antigravity-2（E3 Execution）

```text
你是任务 E3 的执行者 Antigravity-2。

你只负责执行，不负责放行，不负责合规裁决。

task_id: E3
目标: 完成 secrets / credentials boundary 子面的最小准备骨架
交付物:
- secrets / credentials boundary 子面目录/文件骨架
- 职责定义
- 不负责项
- 与 frozen 主线的承接点
- 与 system_execution 的接口关系
- secrets 分层规则
- permit/credentials 使用边界说明
- docs/2026-03-19/verification/external_execution_and_integration_preparation/E3_execution_report.md

你必须完成：
1. 明确 secrets / credentials 只定义分层与边界，不接入真实 provider
2. 明确凭据不得直接下沉进 frozen 主线
3. 明确 permit 与 credentials 不能互相替代
4. 明确后续 runtime 的排除边界

硬约束：
- 不得写入真实密钥
- 不得接入真实 secrets provider
- 不得扩到 runtime
- 不得改 frozen 主线
```

## 8. 发给 Kior-A（E3 Review）

```text
你是任务 E3 的审查者 Kior-A。

你只做审查，不做执行，不做合规放行。

task_id: E3
执行者: Antigravity-2
目标: 完成 secrets / credentials boundary 子面的最小准备骨架

审查重点：
1. 分层规则是否清晰
2. 是否把 credentials 与 permit 混成一层
3. 是否把 secrets 边界写成真实 provider 实现
4. 与 frozen 主线、system_execution 的关系是否清楚

输出：
- docs/2026-03-19/verification/external_execution_and_integration_preparation/E3_review_report.md
```

## 9. 发给 Kior-C（E3 Compliance）

```text
你是任务 E3 的合规官 Kior-C。

你只做 B Guard 式硬审。

task_id: E3
执行者: Antigravity-2
审查者: Kior-A
目标: 完成 secrets / credentials boundary 子面的最小准备骨架

合规审查重点：
1. 是否写入真实密钥
2. 是否接入真实 secrets provider
3. 是否把 credentials 变成裁决条件来源
4. 是否倒灌 frozen 主线

Zero Exception Directives：
- 只要写入真实密钥，直接 FAIL
- 只要接入真实 provider，直接 FAIL
- 只要 credentials 主化为裁决依据，直接 FAIL
```

---

## 10. 发给 Kior-B（E4 Execution）

```text
你是任务 E4 的执行者 Kior-B。

你只负责执行，不负责放行，不负责合规裁决。

task_id: E4
前置条件: E1/E2/E3 已回收
目标: 完成 external action policy 子面的最小准备骨架
交付物:
- external action policy 子面目录/文件骨架
- 职责定义
- 不负责项
- 外部动作分类
- permit 使用条件
- Evidence / AuditPack 引用规则
- docs/2026-03-19/verification/external_execution_and_integration_preparation/E4_execution_report.md

你必须完成：
1. 区分关键动作 / 非关键动作
2. 明确关键动作必须以 permit 为前提
3. 明确集成层只能搬运 Evidence / AuditPack，不可改写
4. 明确禁止越权触发真实外部动作

硬约束：
- 不得绕过 permit
- 不得改写 Evidence / AuditPack 语义
- 不得进入真实外部动作
```

## 11. 发给 vs--cc1（E4 Review）

```text
你是任务 E4 的审查者 vs--cc1。

你只做审查，不做执行，不做合规放行。

task_id: E4
执行者: Kior-B
目标: 完成 external action policy 子面的最小准备骨架

审查重点：
1. 外部动作分类是否清晰
2. permit 规则是否清楚且不可绕过
3. Evidence / AuditPack 是否保持只读语义
4. 是否偷带真实动作实现

输出：
- docs/2026-03-19/verification/external_execution_and_integration_preparation/E4_review_report.md
```

## 12. 发给 Kior-C（E4 Compliance）

```text
你是任务 E4 的合规官 Kior-C。

你只做 B Guard 式硬审。

task_id: E4
执行者: Kior-B
审查者: vs--cc1
目标: 完成 external action policy 子面的最小准备骨架

合规审查重点：
1. permit 是否可绕过
2. Evidence / AuditPack 是否可改写
3. 是否进入真实发布/通知/同步动作
4. 是否把外部动作层写成裁决层

Zero Exception Directives：
- 只要 permit 可绕过，直接 FAIL
- 只要 Evidence / AuditPack 可改写，直接 FAIL
- 只要进入真实动作，直接 FAIL
- 只要写成裁决层，直接 FAIL
```

---

## 13. 发给 vs--cc3（E5 Execution）

```text
你是任务 E5 的执行者 vs--cc3。

你只负责执行，不负责放行，不负责合规裁决。

task_id: E5
前置条件: E2/E4 已回收
目标: 完成 retry / compensation boundary 子面的最小准备骨架
交付物:
- retry / compensation boundary 子面目录/文件骨架
- 职责定义
- 不负责项
- 与 frozen 主线的承接点
- 与 system_execution 的接口关系
- permit 使用规则说明
- 后续 runtime 排除说明
- docs/2026-03-19/verification/external_execution_and_integration_preparation/E5_execution_report.md

你必须完成：
1. 明确 retry / compensation 只停留在边界说明
2. 明确不得实现真实补偿逻辑
3. 明确失败后只能给出建议，不做自动执行
4. 明确 permit 与补偿动作的关系

硬约束：
- 不得实现自动重试
- 不得实现补偿逻辑
- 只允许边界说明与接口草案
```

## 14. 发给 Kior-A（E5 Review）

```text
你是任务 E5 的审查者 Kior-A。

你只做审查，不做执行，不做合规放行。

task_id: E5
执行者: vs--cc3
目标: 完成 retry / compensation boundary 子面的最小准备骨架

审查重点：
1. 是否只停留在边界说明
2. 是否偷带真实补偿实现
3. 是否把 retry 建议写成自动执行
4. 是否与 E4/E6 关系清晰

输出：
- docs/2026-03-19/verification/external_execution_and_integration_preparation/E5_review_report.md
```

## 15. 发给 Kior-C（E5 Compliance）

```text
你是任务 E5 的合规官 Kior-C。

你只做 B Guard 式硬审。

task_id: E5
执行者: vs--cc3
审查者: Kior-A
目标: 完成 retry / compensation boundary 子面的最小准备骨架

合规审查重点：
1. 是否进入 runtime
2. 是否实现真实补偿逻辑
3. 是否让补偿建议绕过 permit
4. 是否扩大到真实业务执行

Zero Exception Directives：
- 只要进入 runtime，直接 FAIL
- 只要实现真实补偿，直接 FAIL
- 只要 permit 被绕过，直接 FAIL
```

---

## 16. 发给 Antigravity-1（E6 Execution）

```text
你是任务 E6 的执行者 Antigravity-1。

你只负责执行，不负责放行，不负责合规裁决。

task_id: E6
前置条件: E4/E5 已回收
目标: 完成 publish / notify / sync boundary 子面的最小准备骨架
交付物:
- publish / notify / sync boundary 子面目录/文件骨架
- 职责定义
- 不负责项
- permit 前置规则
- 与 system_execution / external action policy 的连接说明
- 后续 runtime 排除说明
- docs/2026-03-19/verification/external_execution_and_integration_preparation/E6_execution_report.md

你必须完成：
1. 明确 publish / notify / sync 关键动作必须持 permit
2. 明确不得触发真实发布 / 通知 / 同步
3. 明确只能做边界准备，不做真实动作执行
4. 明确与 E4/E5 的关系

硬约束：
- 不得触发真实发布 / 通知 / 同步
- 不得绕过 permit
- 不得接入真实外部系统
```

## 17. 发给 vs--cc1（E6 Review）

```text
你是任务 E6 的审查者 vs--cc1。

你只做审查，不做执行，不做合规放行。

task_id: E6
执行者: Antigravity-1
目标: 完成 publish / notify / sync boundary 子面的最小准备骨架

审查重点：
1. publish / notify / sync 边界是否清晰
2. permit 前置规则是否明确
3. 是否偷带真实动作语义
4. 是否与 E4/E5 关系自洽

输出：
- docs/2026-03-19/verification/external_execution_and_integration_preparation/E6_review_report.md
```

## 18. 发给 Kior-C（E6 Compliance）

```text
你是任务 E6 的合规官 Kior-C。

你只做 B Guard 式硬审。

task_id: E6
执行者: Antigravity-1
审查者: vs--cc1
目标: 完成 publish / notify / sync boundary 子面的最小准备骨架

合规审查重点：
1. 是否触发真实发布 / 通知 / 同步
2. 是否 permit 可绕过
3. 是否接入真实外部系统
4. 是否把 publish / notify / sync 写成裁决层

Zero Exception Directives：
- 只要触发真实动作，直接 FAIL
- 只要 permit 可绕过，直接 FAIL
- 只要接入真实外部系统，直接 FAIL
- 只要成为裁决层，直接 FAIL
```

---

## 19. Codex 终验条件

- 六个子面都完成 `execution / review / compliance`
- 并行 / 串行依赖顺序被遵守
- 无阻断性越界问题
- 正式文档 1-6 完整
- 模块报告与任务总表一致
