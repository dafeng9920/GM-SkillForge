# Codex 全链路治理同步公告 (v1)

**适用对象**: 本地 Codex (Main Control) / Gemini (Bridge Operator) / 云端 Codex (Execution Consumer)
**生效时间**: 2026-03-08 19:30 UTC
**当前治理层级**: **L4 - 受控多Agent执行准备态 (Controlled Multi-Agent Execution)**

---

## 1. 03-08 治理大捷摘要 (Executive Summary)

针对昨晚出现的“资产流浪”、“幻觉执行”与“注水报告”问题，主控已完成全线纠偏与架构升级。以下为核心变动，所有角色必须强制同步认知：

### 1.1 物理架构：受控桥接
- **变量定义**: 
  - `SSOT_ROOT`: 本地主仓 authoritative 根
  - `DOCS_ROOT`: 文档与审计产物根
  - `APP_ROOT`: 工作源码根目录
  - `DROPZONE_ROOT`: 产物交付出口
- **主仓保护**: `APP_ROOT` 已挂载为 **ReadOnly (只读)**。
- **唯一交付区**: `DROPZONE_ROOT` 为法定 RW 交付路径。
- **资产吸收**: 当前 authoritative absorb 通过宿主机吸收动作（`scripts/absorb.sh <TASK_ID>`）执行逻辑，吸收目标为 `DOCS_ROOT/<TASK_ID>/`。

### 1.2 协作协议：三位一体 (Trinity)
- **角色互锁**: 任务必须由 **Executor (执行)**、**Reviewer (审计)**、**Compliance (合规)** 三方联署结算。
- **架构共识**: 动手前强制执行 **Phase 0 讨论**，并产出 `blueprint.md`。

---

## 2. 给 Codex 的跟进指令 (Action Items)

### 2.1 对云端 Codex (龙爪臂) 的要求
1. **死守边界**: 意识到你无法直接修改 `APP_ROOT` 源码，不要尝试直接写 authoritative 主仓。
2. **补丁交付**: 代码变更必须以 `.diff` 存放在 `DROPZONE_ROOT/<TASK_ID>/artifacts/` 下。
3. **证据至上**: 审计结论严禁感性描述，必须引用 `DROPZONE_ROOT/<TASK_ID>/evidence/` 下的机器日志。
4. **离线自治**: 主控离线时，遵循 **AOE 规则**：遇疑即停 (Fail-Closed)，拒绝盲目通过。
5. **角色边界**: 云端 Codex 只消费 Gemini 已桥接到云端的 skill 副本，不负责主动从本地主仓抓取 skill。

### 2.2 对本地 Codex (脑控核) 的要求
1. **SSOT 维护**: 以 `SSOT_ROOT` 与 `DOCS_ROOT` 下的纠偏版资产（特别是 P3 基线）为后续任务起点。
2. **影子审计**: 资产吸收后，主控必须执行一次逻辑语义复核。
3. **二审准入**: 高复杂度（L2 级）任务，必须由你签署 `PROCEED` 后才允许云端开工。
4. **最终验收**: 最终业务验收权仅归本地 Codex，不因云端 pre-absorb/check 通过而自动转移。

### 2.3 对 Gemini (桥接官) 的要求
1. **桥接同步**: 负责把本地主仓 skill 副本同步到云端可读路径。
2. **不改权威源**: 不得把云端副本反写成主仓 authoritative 版本。
3. **同步留痕**: 必须输出实际落点、存在性验证和阻断原因，并形成 `cloud_skill_sync_report.md`。

---

## 3. 核心资产索引 (Reference)
- `docs/2026-03-08/LOBSTER_TASK_PACKAGE_SPEC.md`
- `docs/2026-03-08/CLOUD_MULTI_AGENT_OVERSIGHT_PROTOCOL_v1.md`
- `docs/2026-03-08/CLOUD_SKILL_SYNC_INSTALL_PROTOCOL_v1.md`

---
*由 Antigravity 签发，确立 L4 受控多Agent执行治理基点。*
