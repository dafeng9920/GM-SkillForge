# L6-P0 与 L6 全量差异清单（2026-02-26）

## 结论

1. 已达成：`L6-P0（真实性闭环）`  
2. 未达成：`L6 全量（长期稳定自治）`

依据：
- 已完成清单：`docs/2026-02-26/P0-issues/P0-10-issue-任务清单.md`
- 全量目标清单：`docs/2026-02-22/L5-L6_EXECUTION_PLAN.md`

## 已完成（L6-P0）

1. 宪法硬门与 fail-closed 前置校验（ISSUE-00）
2. Canonical JSON 与一致性哈希（ISSUE-01）
3. Envelope + Body 结构（ISSUE-02）
4. 混合加密链路（ISSUE-03）
5. Ed25519 签名验签（ISSUE-04）
6. Nonce 防重放（ISSUE-05）
7. Node Registry 身份校验（ISSUE-06）
8. Receipt hash 统一 SHA-256(canonical)（ISSUE-07）
9. 协议测试 T1-T5 + CI fail-closed（ISSUE-08/09）
10. 第三方独立验真最小演示（ISSUE-10）

## 待完成（L6 全量）

以下项目来自 `L5-L6_EXECUTION_PLAN` 的 Stage B/C 要求，当前未形成“连续周期证据”：

1. 连续 7 天 nightly gate 稳定达标（L5 入场门槛）
2. 连续 30 天稳定运行且无未处置 CRITICAL（L6 判定）
3. 自动回滚与自动恢复机制演练通过并可审计（rollback drill）
4. 漂移监控与容量预测生效（含阈值治理）
5. 月度治理审计可复现（同输入同结论偏差在阈值内）
6. 指标 M1-M10 达到 L6 门槛并持续满足（不是单次通过）

## 当前等级判定

1. `L6-P0`: `PASS`（可封板归档）
2. `L6-full`: `NOT_YET`（缺长期运行与自治治理证据）

## 下一步最小路径（建议）

1. 先补 L5 门槛证据：7 天 nightly + M1-M10 周期报告
2. 启动 L6 30 天稳定性观察窗口（自动生成周报）
3. 每周执行一次 rollback drill 并固化证据
4. 月底输出 `l6_monthly_audit.json` 再做 Final Gate

