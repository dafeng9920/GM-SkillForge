# 系统执行层最小落地模块边界规则 v1

## 对 frozen 主线的边界
- 系统执行层只承接 frozen 主线，不得裁决 frozen 主线。
- `permit / EvidenceRef / AuditPack / decision` 在本模块中仅允许只读承接。
- 禁止反向改写 `governance intake / gate / review / release / audit` 的任何边界口径。

## workflow 边界
- 只负责流程入口与模块连接骨架。
- 不负责治理裁决。
- 不负责 runtime 调度。
- 不负责外部集成触发。

## orchestrator 边界
- 只负责内部承接与路由骨架。
- 不负责 permit / decision / audit 裁决。
- 不负责 runtime 控制。

## service 边界
- 只负责服务层承接与只读转换骨架。
- 不负责真实业务执行。
- 不负责外部系统调用。

## handler 边界
- 只负责输入承接与调用转发骨架。
- 不负责副作用动作。
- 不负责 runtime 分支控制。

## api 边界
- 只负责最小接口层承接骨架。
- 不负责真实对外协议。
- 不负责外部集成入口。

## 与系统执行层后续部分的边界
- 本模块不进入：
  - `runtime`
  - `workflow routing`
  - `orchestrator control`
  - `service / handler / api behavior`
  - `external integration`
- 若执行单元提交内容天然属于以上范围，直接退回。

## 审查与合规边界
- Review 只检查结构与职责一致性，不新增需求。
- Compliance 只检查越界与主化风险，不代写实现。
- Codex 只做验收与退回，不代行五子面主实现。

## 禁止混入的语义类型
- 治理裁决语义
- runtime 调度语义
- 外部执行批准语义
- 真实业务执行语义
- 真实外部接入 contract
