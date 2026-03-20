# E6 publish / notify / sync boundary 三权任务书

适用任务：

* `E6`

对应角色：

* Execution: `Antigravity-1`
* Review: `vs--cc1`
* Compliance: `Kior-C`

唯一事实源：

* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_SCOPE.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_SCOPE.md)
* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_BOUNDARY_RULES.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_BOUNDARY_RULES.md)
* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_ACCEPTANCE.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_ACCEPTANCE.md)
* [multi-ai-collaboration.md](/d:/GM-SkillForge/multi-ai-collaboration.md)

## 执行模式
- `serial`
- `depends_on = E4,E5`
- `wave = external_execution_preparation_v1_wave3`

## 发给 Antigravity-1（Execution）

```text
你是任务 E6 的执行者 Antigravity-1。

你只负责执行，不负责放行，不负责合规裁决。

task_id: E6
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

## 发给 vs--cc1（Review）

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
```

## 发给 Kior-C（Compliance）

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
