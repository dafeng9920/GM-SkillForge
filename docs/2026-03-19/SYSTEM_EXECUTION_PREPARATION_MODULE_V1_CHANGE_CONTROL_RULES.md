# 系统执行层准备模块变更控制规则 v1

## 本阶段允许变更范围
- 文档补强
- skeleton 注释补强
- 非语义性目录整理
- 五子面占位说明增强

## 本阶段禁止变更范围
- 回改 frozen 主线对象或文档
- 引入 runtime / external integration
- 引入真实业务逻辑
- 引入真实 service / handler / api contract
- 让 workflow / orchestrator 获得裁决权

## 已冻结层保护规则
- `Production / Bridge / Governance Intake / Gate / Review / Release / Audit` frozen 文档正文不得修改。
- 对应 frozen 对象边界不得倒灌。

## 五子面对象的变更控制规则
- `workflow`
  - 允许：入口占位与阶段说明增强
  - 禁止：运行时路由、调度控制
- `orchestrator`
  - 允许：依赖关系与模块关系说明增强
  - 禁止：裁决、放行、执行控制
- `service`
  - 允许：只读承接接口占位
  - 禁止：真实业务逻辑、外部调用
- `handler`
  - 允许：请求承接占位
  - 禁止：副作用动作、运行时控制
- `api`
  - 允许：边界入口占位
  - 禁止：真实协议暴露、外部接入

## compat 字段变更控制规则
- compat 字段仅可作为背景字段说明。
- source-layer status 不得主化。
- `permit / EvidenceRef / AuditPack` 不得在本模块内被升级为执行动作。

## 禁止混入系统执行 / 外部执行语义规则
- 禁止混入：
  - runtime 控制语义
  - 外部执行批准语义
  - 外部集成 contract
  - 编排裁决语义

## 下一阶段前不得触碰的实现面
- runtime
- workflow routing
- orchestrator control
- service / handler / api behavior
- external integration
- handoff / intake execution
