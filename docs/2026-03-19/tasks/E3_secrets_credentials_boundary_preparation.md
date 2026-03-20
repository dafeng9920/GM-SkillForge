# E3 secrets / credentials boundary 三权任务书

适用任务：

* `E3`

对应角色：

* Execution: `Antigravity-2`
* Review: `Kior-A`
* Compliance: `Kior-C`

唯一事实源：

* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_SCOPE.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_SCOPE.md)
* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_BOUNDARY_RULES.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_BOUNDARY_RULES.md)
* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_ACCEPTANCE.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_ACCEPTANCE.md)
* [multi-ai-collaboration.md](/d:/GM-SkillForge/multi-ai-collaboration.md)

## 执行模式
- `parallel`
- `wave = external_execution_preparation_v1_wave1`

## 发给 Antigravity-2（Execution）

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
1. 明确 secrets / credentials 只定义分层与边界
2. 明确不接入真实 provider
3. 明确凭据不得下沉进 frozen 主线
4. 明确 permit 与 credentials 不能互相替代
5. 明确后续 runtime 的排除边界

硬约束：
- 不得写入真实密钥
- 不得接入真实 secrets provider
- 不得扩到 runtime
- 不得改 frozen 主线
```

## 发给 Kior-A（Review）

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
```

## 发给 Kior-C（Compliance）

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
