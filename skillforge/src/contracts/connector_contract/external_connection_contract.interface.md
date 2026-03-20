# external_connection_contract.interface

## Interface role
- Connector Contract 接口定义
- 外部连接契约规范
- 不实现真实连接
- 不生成 permit
- 不存储凭据

## Upstream objects
- `normalized_skill_spec` (只读)
- `GateDecision` (只读)
- `EvidenceRef` (只读)
- `AuditPack` (只读)
- `ReleaseDecision` (只读)

## Allowed callers
- `system_execution.service` (Service 层)
- `system_execution.handler` (Handler 层)
- `system_execution.orchestrator` (Orchestrator 层)

## Forbidden callers
- `integration_gateway` (应调用此接口获取契约，不应反向调用)
- `secrets_boundary` (不涉及凭据存储)
- `external_action_policy` (应调用此接口获取契约，不应反向调用)

## Forbidden semantics
- implemented
- executed
- connected
- authenticated
- permit_generated
- credential_stored
- runtime_managed

## 返回值语义
- 返回 `ExternalConnectionContract` 对象（只读，不可变）
- 返回 permit 需求声明（不生成 permit）
- 返回 frozen 依赖声明（不修改 frozen 对象）
- 返回数据结构规范（不实现连接）

## Boundary note
此接口只定义外部连接的契约规范，不实现任何真实连接。真实连接由 Integration Gateway 在有 permit 的情况下执行。
