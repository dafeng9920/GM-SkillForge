# E2 integration gateway 三权任务书

适用任务：

* `E2`

对应角色：

* Execution: `Antigravity-1`
* Review: `vs--cc3`
* Compliance: `Kior-C`

唯一事实源：

* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_SCOPE.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_SCOPE.md)
* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_BOUNDARY_RULES.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_BOUNDARY_RULES.md)
* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_ACCEPTANCE.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_ACCEPTANCE.md)
* [multi-ai-collaboration.md](/d:/GM-SkillForge/multi-ai-collaboration.md)

## 执行模式
- `parallel`
- `wave = external_execution_preparation_v1_wave1`

## 发给 Antigravity-1（Execution）

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
2. 明确不做最终 PASS/FAIL 裁决
3. 明确不得越权生成 GateDecision / permit / AuditPack
4. 明确后续 runtime 的排除边界

硬约束：
- 不得让 integration gateway 成为裁决层
- 不得进入 runtime
- 不得接入真实外部系统
- 不得改 frozen 主线
```

## 发给 vs--cc3（Review）

```text
你是任务 E2 的审查者 vs--cc3。

你只做审查，不做执行，不做合规放行。

task_id: E2
执行者: Antigravity-1
目标: 完成 integration gateway 子面的最小准备骨架

审查重点：
1. integration gateway 是否只做连接与路由
2. 与 system_execution 的边界是否清晰
3. 是否出现裁决权主化
4. 是否出现真实联调倾向
```

## 发给 Kior-C（Compliance）

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
