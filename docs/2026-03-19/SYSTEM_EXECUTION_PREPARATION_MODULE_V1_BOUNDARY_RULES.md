# 系统执行层准备模块边界规则 v1

## 与 frozen 主线的边界
- 系统执行层准备模块只承接 frozen 主线输出，不反向解释、不反向改写。
- `governance intake / gate / review / release / audit` 的裁决语义继续停留在 frozen 主线。
- 系统执行层仅可读取以下冻结产物的边界含义：
  - `permit`
  - `EvidenceRef`
  - `AuditPack`
  - 各层输入对象与 change control 规则

## workflow 边界
- `workflow` 只描述阶段编排入口与下游挂点。
- `workflow` 不做治理裁决。
- `workflow` 不做 runtime 调度。
- `workflow` 不做外部调用编排。

## orchestrator 边界
- `orchestrator` 只负责模块内路由准备与依赖关系占位。
- `orchestrator` 不得宣告 `ALLOW / PASS / VALID`。
- `orchestrator` 不得接管治理与合规裁决权。

## service 边界
- `service` 只保留最小承接接口与只读转换占位。
- `service` 不得执行真实业务动作。
- `service` 不得直连外部系统。

## handler 边界
- `handler` 仅保留请求承接与调用转发准备位。
- `handler` 不得包含运行时分支控制。
- `handler` 不得直接触发副作用动作。

## api 边界
- `api` 仅保留边界占位、请求/响应说明与后续挂接位置。
- `api` 不得暴露真实运行时 contract。
- `api` 不得提前定义外部接入协议。

## 与 runtime / 外部执行层的边界
- 本模块不进入：
  - `runtime`
  - `external integration`
  - `workflow routing`
  - `service / handler / api behavior`
  - `orchestrator action`
- 若字段、命名或目录天然要求上述语义，则必须暂停并退回准备边界。

## compat / 风险控制
- compat 字段只能以只读背景信息存在。
- `production_status / build_validation_status / delivery_status` 只能是 source-layer 风险背景，不得主化。
- `permit=VALID` 只作为进入后续系统执行层的前置条件说明，不在本模块内触发真实执行。
- `EvidenceRef / AuditPack` 只作为证据桥接位，不在本模块内触发审计执行。

## 禁止混入的语义类型
- 治理裁决语义
- runtime 调度语义
- 外部执行批准语义
- 真实业务执行语义
- 外部集成 contract

## change control 规则
- 允许：
  - 文档补强
  - 非语义性骨架整理
  - 更清晰的占位命名修正
- 受控：
  - 五子面接口关系细化
  - skeleton 目录轻量调整
  - 需保持与 frozen 主线只读承接一致
- 禁止：
  - 倒灌 frozen 主线
  - 混入 runtime / external integration
  - 提前实现真实 handler/service/api/workflow/orchestrator 逻辑
