# NEW-GM 意图迁移差异报告（2026-03-06）

## 结论（先看这个）

`D:\NEW-GM` 的“设计意图”在 `D:\GM-SkillForge` 中是**部分迁移**，不是全量缺失，也不是全量落地。

- 已落地：核心治理主线（Constitution/Fail-Closed/Gate/Evidence/AuditPack/Intent 映射）有实物证据。
- 未落地：外螺旋/内螺旋/北斗可观测等旧体系中的若干意图，尚未被明确转换成当前系统的 Intent Contract + Gate 路径。
- 因此你的怀疑成立：之前的架构审查报告主要审了当前代码安全与实现，不等于完成了 NEW-GM 意图迁移验收。

---

## 审查口径

仅判断三类状态：

1. `已落地`：有代码/合同/测试/证据文件支撑。
2. `部分落地`：有文档或片段，但缺统一映射/验收闭环。
3. `未落地`：在当前仓未找到对应实现或迁移合同。

---

## A. 已落地（有硬证据）

1. 宪法与 Fail-Closed 主线  
证据：
- `docs/2026-02-16/constitution_v1.md`
- `core/gate_engine.py`
- `core/pack_and_permit.py`

2. NEW-GM 图书馆意图迁移文档（Inventory + Mapping）  
证据：
- `docs/2026-02-17/图书馆迁移/library_intent_inventory_v1.md`
- `docs/2026-02-17/图书馆迁移/library_intent_mapping_v1.md`

3. 10D 四件套（从旧设计意图到新合同化资产）  
证据：
- `skillforge-spec-pack/skillforge/src/contracts/cognition_10d.intent.yaml`
- `skillforge-spec-pack/skillforge/src/contracts/cognition_10d_rubric.yaml`
- `skillforge-spec-pack/skillforge/src/skills/cognition_10d_generator.py`
- `docs/2026-02-17/cognition_10d_cases/README.md`

4. n8n 受控编排边界（n8n 触发、SkillForge 裁决）  
证据：
- `skillforge/src/api/routes/n8n_orchestration.py`
- `skillforge/tests/test_n8n_orchestration.py`
- `skillforge/tests/test_n8n_run_intent_production.py`

---

## B. 部分落地（有意图，但缺统一对齐）

1. 外螺旋意图（outer_spiral 系）  
现状：
- 在新仓大量出现于历史文档与计划，但缺“NEW-GM 外螺旋 → 当前 intent_id 列表”的正式对照表。
- 缺单独的 parity 回归包（按旧动线场景验证新链路）。

2. 内螺旋诊断/健康意图（inner_spiral / shadow）  
现状：
- 新仓治理和闭环有实现，但未形成对旧 inner_spiral 语义的一一映射说明。

3. 旧审计可观测语义（北斗星图/灯态）  
现状：
- NEW-GM 中是完整域模型（beidou store/journal/status），当前仓未见同级域的合同化替代说明。

---

## C. 当前明确未落地（按“旧路径直映射”检查）

以下旧路径在当前仓不存在（仅说明“未直接迁代码”，不代表不应迁移）：

- `src/gateway/routers/outer_spiral_router.py` → 不存在
- `src/gateway/routers/inner_spiral_router.py` → 不存在
- `src/services/beidou/beidou_store.py` → 不存在
- `src/services/beidou/lighting_journal.py` → 不存在
- `src/inner_spiral/healthcheck.py` → 不存在

说明：这符合“只迁意图、不拷旧代码”的原则，但前提是必须有等价的 Intent Contract 与验收闭环；当前这一层还不完整。

---

## D. 为什么你会感觉“报告没提到所以可能不存在”

`docs/2026-03-06/arch_review_gm_skillforge.md` 与 `.resolved` 主要聚焦：
- 当前系统安全漏洞与实现质量
- Gate/Permit/API 风险

对 NEW-GM 迁移维度没有单独章节，也没有“旧意图对齐率”指标，所以看不出迁移完成度。

---

## E. 新 TODO（建议今日起执行）

## P0（必须）

1. 产出 `NEW_GM_INTENT_PARITY_MATRIX_v1.md`  
要求：
- 列出 NEW-GM 高价值意图（外螺旋/内螺旋/北斗/gmhub/编排）
- 对应当前 `intent_id`、`gate_path`、`error_codes`、`required_evidence`
- 每项状态：`Implemented/Partial/Missing`

2. 产出 3 条“旧意图 → 新链路”可执行回归  
最小集合建议：
- 外螺旋意图路由（从输入到 Gate 结果）
- 内螺旋健康/审计意图
- 北斗可观测语义（用新证据模型表达）

3. 在总账本登记迁移批次  
更新：
- `docs/VERIFICATION_MAP.md` 增加 “NEW-GM Intent Migration” 专节

## P1（应做）

1. 把“旧域名词”收敛到新 intent catalog  
避免同时维护旧词（outer_spiral/beidou）和新词（run_intent/gate）造成歧义。

2. 补一份“反向追溯文档”  
`当前 intent_id -> 来源 NEW-GM 设计文档路径 -> 验收证据路径`

---

## 备注

本报告不主张回迁旧代码；仅要求把旧设计意图转换为当前系统可执行、可审计、可复验的合同化资产。
