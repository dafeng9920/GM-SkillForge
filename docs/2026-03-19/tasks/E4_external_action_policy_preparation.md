# E4 external action policy 三权任务书

适用任务：

* `E4`

对应角色：

* Execution: `Kior-B`
* Review: `vs--cc1`
* Compliance: `Kior-C`

唯一事实源：

* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_SCOPE.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_SCOPE.md)
* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_BOUNDARY_RULES.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_BOUNDARY_RULES.md)
* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_ACCEPTANCE.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_ACCEPTANCE.md)
* [multi-ai-collaboration.md](/d:/GM-SkillForge/multi-ai-collaboration.md)

## 执行模式
- `serial`
- `depends_on = E1,E2,E3`
- `wave = external_execution_preparation_v1_wave2`

## 发给 Kior-B（Execution）

```text
你是任务 E4 的执行者 Kior-B。

你只负责执行，不负责放行，不负责合规裁决。

task_id: E4
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
2. 明确关键动作必须持 permit
3. 明确集成层只能搬运 Evidence / AuditPack，不可改写
4. 明确不得越权触发真实外部动作

硬约束：
- 不得绕过 permit
- 不得改写 Evidence / AuditPack 语义
- 不得进入真实外部动作
```

## 发给 vs--cc1（Review）

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
```

## 发给 Kior-C（Compliance）

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
