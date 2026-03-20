# 外部执行与集成准备模块 v1 边界规则

## 核心原则
1. frozen 对象主线不被倒灌
2. `system_execution` 只承接，不裁决
3. 外部执行与集成层只连接与搬运，不裁决
4. 关键动作必须依赖 permit
5. Evidence / AuditPack 由内核生成，不可被集成层改写
6. connector / integration 不提前长成 runtime
7. 不允许出现“先接上再说”的扩权行为

## 只读承接规则
- 只能读取 frozen 主线的公开承接结果
- 不得回写 GateDecision / EvidenceRef / AuditPack / permit 语义
- 不得在外部层生成新的治理裁决对象

## permit 规则
- 发布、同步、下架、通知等关键动作，必须以 permit 为前提
- 外部执行层不得自行绕过 permit 触发关键动作

## 证据规则
- Evidence / AuditPack 只能由 SkillForge 内核生成
- 外部执行与集成层只能引用、搬运、上传、通知
- 不得改写、覆盖、二次生成核心 Evidence / AuditPack 语义

## 自动暂停条件
- 任一方要求修改 frozen 对象
- 任一方把外部执行层写成裁决层
- 任一方开始进入 runtime
- 任一方开始接入真实外部系统
- 任一方开始实现真实业务逻辑
- 任一方开始绕过 permit
- 三权角色混线
- Codex 绕过分派直接吞掉模块实现
