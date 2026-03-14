# P0 可直接开工的 10 个 Issue 级任务

> 范围：仅限 L6 真实性闭环  
> 阶段门控：本清单未完成前，不进入 L4 实现

## ISSUE-00：宪法防绕过基线（前置）
- 目标：防止任何路径绕过系统宪法与协议硬门
- 交付物：统一 `policy_check` 前置校验 + fail-closed 拒绝策略 + 审计字段标准
- 验收标准：
  - 任意入口（API/CLI/worker）均先执行 `policy_check`
  - 缺签名/缺 nonce/schema 非法/node 未注册一律拒绝
  - 每次决策记录 `trace_id/policy_version/decision_reason/evidence_ref`

## ISSUE-01：证据包 Canonical JSON 规范落地
- 目标：统一序列化规则，避免签名与验签不一致
- 交付物：`canonical_json` 工具函数 + 用例
- 验收标准：同一 payload 在不同运行环境 hash 一致

## ISSUE-02：Envelope + Body 结构实现
- 目标：按 v1 结构拆分 `header/keywrap/ciphertext/signature/cert`
- 交付物：证据包构造器（含 schema 字段）
- 验收标准：可生成完整 envelope，字段齐全且通过 schema 校验

## ISSUE-03：混合加密替换整包 RSA
- 目标：使用 `AES-256-GCM + RSA-OAEP-256` 完成加密流程
- 交付物：加解密模块（DEK 包裹 + AEAD）
- 验收标准：正常解密通过，任意篡改密文触发解密失败

## ISSUE-04：节点签名链路（Ed25519）
- 目标：节点私钥签名 evidence，服务端可验签
- 交付物：签名与验签实现 + `signed_fields` 校验
- 验收标准：改动 header/body 任意字段，验签失败

## ISSUE-05：Nonce Challenge 防重放
- 目标：实现一次性 challenge + TTL
- 交付物：challenge 生成、下发、校验、失效机制
- 验收标准：重放旧包返回 `REPLAY_DETECTED`，过期返回 `CHALLENGE_EXPIRED`

## ISSUE-06：Node Registry 与身份校验
- 目标：建立 `node_id -> pubkey/cert/status` 注册表
- 交付物：registry 读取层 + NODE_UNTRUSTED 裁决
- 验收标准：未知节点或失效节点全部拒绝

## ISSUE-07：审计回执哈希修正
- 目标：移除 `Python hash()`，统一 `SHA-256(canonical_payload)`
- 交付物：receipt hash 生成器
- 验收标准：同 payload 多次计算结果稳定一致

## ISSUE-08：协议级 T1-T5 测试集
- 目标：覆盖最小合规测试（篡改/重放/过期/伪造）
- 交付物：`tests/protocol/` 下 5 个测试用例
- 验收标准：T1-T5 全绿；每个失败路径返回预期错误码

## ISSUE-09：Pipeline 接入与强制 Gate
- 目标：将 T1-T5 加入 CI，未通过禁止合并
- 交付物：CI 配置 + gate 脚本
- 验收标准：任一协议测试失败时 pipeline fail-closed

## ISSUE-10：第三方可验证最小演示
- 目标：做一个“外部验证脚本”独立验一条 evidence
- 交付物：`verify_evidence.py`（或等价脚本）+ 示例包
- 验收标准：第三方只拿公钥与包即可完成验签/验 nonce/验时效

## 依赖顺序（执行建议）
1. ISSUE-00
2. ISSUE-01
3. ISSUE-02
4. ISSUE-03
5. ISSUE-04
6. ISSUE-05
7. ISSUE-06
8. ISSUE-07
9. ISSUE-08
10. ISSUE-09
11. ISSUE-10

## 完成定义（P0 DoD）
- 至少 1 条真实运行证据可被第三方独立验证真实性
- T1-T5 协议测试在 CI 稳定通过
