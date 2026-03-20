# E1 connector contract 三权任务书

适用任务：

* `E1`

对应角色：

* Execution: `vs--cc1`
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

## 发给 vs--cc1（Execution）

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
1. 明确 connector contract 只定义外部连接契约
2. 明确不做真实外部接入
3. 明确 permit 只作为前置条件，不在此层生成
4. 明确 Evidence / AuditPack 只能引用，不能改写
5. 明确后续 runtime 的排除边界

硬约束：
- 不得接入真实外部系统
- 不得进入 runtime
- 不得改 frozen 主线
- 不得生成真实外部协议实现
- 无 permit / evidence / auditpack 规则说明不得宣称完成
```

## 发给 Kior-A（Review）

```text
你是任务 E1 的审查者 Kior-A。

你只做审查，不做执行，不做合规放行。

task_id: E1
执行者: vs--cc1
目标: 完成 connector contract 子面的最小准备骨架

审查重点：
1. connector contract 职责是否清晰
2. 不负责项是否清晰
3. 与 frozen 主线和 system_execution 的承接关系是否清楚
4. permit / evidence / auditpack 规则是否自洽
5. 是否偷带真实外部接入语义
```

## 发给 Kior-C（Compliance）

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
