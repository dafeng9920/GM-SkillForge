# Task Dispatcher Protocol Preparation v1 Boundary Rules

## 模块边界
- 本模块只定义协议，不实现协议
- 本模块只定义主控官与 AI 军团之间的任务流转规则
- 本模块不新增业务主线层级

## 与主控官的边界
- 主控官负责冻结边界、拆分任务、维护任务板、做最终验收
- dispatcher protocol 负责规范任务如何被投递、流转、写回、升级
- dispatcher protocol 不替代主控官做最终裁决

## 与 AI 军团的边界
- AI 军团只按 envelope 接单
- AI 军团只向标准 writeback 路径写回
- AI 军团不得绕过 review / compliance 顺序
- AI 军团不得跳过 escalation 规则

## Task Envelope 边界
- envelope 必须定义：`task_id`、`module`、`role`、`depends_on`、`parallel_group`、`writeback`、`acceptance_criteria`
- 没有完整 envelope 的任务，军团可拒收

## State Machine 边界
- 最小状态流转只允许：
  - `PENDING`
  - `ACCEPTED`
  - `IN_PROGRESS`
  - `WRITEBACK_DONE`
  - `REVIEW_TRIGGERED`
  - `REVIEW_DONE`
  - `COMPLIANCE_TRIGGERED`
  - `COMPLIANCE_DONE`
  - `GATE_READY`
- 任何状态流转必须有明确触发条件

## Writeback Contract 边界
- execution 只能写 `execution_report`
- review 只能写 `review_report`
- compliance 只能写 `compliance_attestation`
- 不写回标准路径，不算完成

## Auto-Relay 边界
- auto-relay 只负责衔接 execution -> review -> compliance -> final gate
- auto-relay 不做裁决
- auto-relay 不修改任务内容，只生成下一跳任务信封

## Escalation 边界
- 以下情况才允许升级到主控官：
  - scope violation
  - blocking dependency
  - ambiguous spec
  - review deny
  - compliance fail
  - state timeout

## change control 规则
- 允许：协议字段补充、状态命名收紧、模板补强
- 受控：新增最小字段、新增最小升级条件
- 禁止：直接扩成代码实现、直接改动现有 frozen 结论

