# E5 retry / compensation boundary 三权任务书

适用任务：

* `E5`

对应角色：

* Execution: `vs--cc3`
* Review: `Kior-A`
* Compliance: `Kior-C`

唯一事实源：

* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_SCOPE.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_SCOPE.md)
* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_BOUNDARY_RULES.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_BOUNDARY_RULES.md)
* [EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_ACCEPTANCE.md](/d:/GM-SkillForge/docs/2026-03-19/EXTERNAL_EXECUTION_AND_INTEGRATION_PREPARATION_MODULE_V1_ACCEPTANCE.md)
* [multi-ai-collaboration.md](/d:/GM-SkillForge/multi-ai-collaboration.md)

## 执行模式
- `serial`
- `depends_on = E2,E4`
- `wave = external_execution_preparation_v1_wave3`

## 发给 vs--cc3（Execution）

```text
你是任务 E5 的执行者 vs--cc3。

你只负责执行，不负责放行，不负责合规裁决。

task_id: E5
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

## 发给 Kior-A（Review）

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
```

## 发给 Kior-C（Compliance）

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
