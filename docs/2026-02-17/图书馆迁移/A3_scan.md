# A3 Scan: Upgrade Skill Intent Migration

**Task ID:** A3
**Executor:** VSCode-3
**Scan Date:** 2026-02-18
**Source Project:** D:\NEW-GM

---

## 1. 扫描结果汇总

| component_id | source_doc_ref | intent_summary | mapping_target | value_score | risk_level | migration_decision | evidence_ref |
|--------------|----------------|----------------|----------------|-------------|------------|-------------------|--------------|
| `draft_revision_autoinc` | `D:\NEW-GM\tests\orchestration\test_draft_revision_autoinc.py:116-136` | 版本号自增与幂等性保证：首次进入 revision=1，选择后 bump，重复同 canonical 幂等不再 bump | `skillforge/src/skills/upgrade_skill.py` | 8 | Low | **MIGRATE** | `test_draft_revision_autoinc.py:119-136` |
| `release_governor` | `D:\NEW-GM\src\services\outer_skill_factory\release_governor.py:286-616` | DRAFT→ACTIVE 升级流程：多层 Gate 验证（Build/Compose/Run/Trace Reputation），Fail-closed 原则 | `skillforge/src/skills/upgrade_skill.py` | 9 | Medium | **MIGRATE** | `release_governor.py:286-541` |
| `evolution_manager` | `D:\NEW-GM\deploy\fast_gateway_docker\src\orchestrator\agents\evolution_manager.py:312-736` | 进化管理器：优化策略、指标记录、趋势分析、违规学习 | `skillforge/src/skills/upgrade_skill.py` (参考) | 6 | Medium | **DEFER** | `evolution_manager.py:312-736` |
| `data_flywheel_constraints` | `D:\NEW-GM\docs\2026-02-17\三维RAG与数据飞轮约束_v1.md:19-24` | 数据飞轮定义：evolution.json + SKILL.md append-only 载体 | `contracts/intents/upgrade_skill.yml` | 7 | Low | **MIGRATE** | `三维RAG与数据飞轮约束_v1.md:19-24` |

---

## 2. 详细分析

### 2.1 draft_revision_autoinc (MIGRATE)

**Source Doc Ref:** `D:\NEW-GM\tests\orchestration\test_draft_revision_autoinc.py`

**核心意图提取：**
```python
# 从测试用例提取的 revision 自增逻辑
# Line 119-136:
# T1: 首次进入 revision = 1
# T2: 选择 writing_type 后 bump → revision = 2
# T3: 重复同 canonical 幂等，不再 bump → revision = 2
# T4: genre/style 继续 bump → revision = 3
```

**Intent Semantics:**
1. **原子更新约束**：每次升级操作必须是原子的
2. **幂等性保证**：相同的 canonical 输入不应触发重复递增
3. **revision 递增规则**：
   - 初始 revision = 1
   - 有意义变更时 revision += 1
   - 幂等请求保持 revision 不变

**Evidence Ref:** `test_draft_revision_autoinc.py:116-136`

---

### 2.2 release_governor (MIGRATE)

**Source Doc Ref:** `D:\NEW-GM\src\services\outer_skill_factory\release_governor.py`

**核心意图提取：**
```python
# release_draft_to_active() 函数 (Line 286-616)
# 多层 Gate 验证流程：
# B1: Build Gate - 检查 risk_level, constraints
# B2: Compose/Run Gate - 使用 FlowIR 评估
# B3: Trace Reputation Gate - 使用 TraceStore 统计
```

**Intent Semantics:**
1. **Fail-closed 原则**：任何可疑输入阻止升级
2. **Gate 链式验证**：B1 → B3 → B2，任一 DENY 即终止
3. **ReleaseDecision 输出**：
   - `ALLOW_ACTIVE` - 允许升级
   - `DENY` - 拒绝升级
   - `REQUIRES_HUMAN` - 需人工审批
4. **审计日志**：ReleaseLog 写入 JSONL

**Evidence Ref:** `release_governor.py:286-541`

---

### 2.3 evolution_manager (DEFER)

**Source Doc Ref:** `D:\NEW-GM\deploy\fast_gateway_docker\src\orchestrator\agents\evolution_manager.py`

**核心意图提取：**
```python
# EvolutionManager 类 (Line 312-736)
# 功能：
# - 优化策略（强化学习、贝叶斯优化）
# - 指标记录和趋势分析
# - 违规学习和预防策略
```

**Intent Semantics:**
1. **多策略优化**：REINFORCEMENT_LEARNING, BAYESIAN_OPTIMIZATION
2. **自适应学习率**：基于成功率动态调整
3. **违规模式学习**：从 ViolationRecord 学习预防策略

**Migration Decision: DEFER**
- 该组件更偏向"自进化"而非"upgrade_skill"核心意图
- 复杂度高，需独立评估
- 建议在后续 Wave 中单独迁移

**Evidence Ref:** `evolution_manager.py:312-736`

---

### 2.4 data_flywheel_constraints (MIGRATE)

**Source Doc Ref:** `D:\NEW-GM\docs\2026-02-17\三维RAG与数据飞轮约束_v1.md`

**核心意图提取：**
```markdown
# 数据飞轮定义 (Line 19-24)
# 经验载体：evolution.json + SKILL.md（append-only）
# 回灌入口：仅通过 Gate 流程进入下一轮评估/升级
```

**Intent Semantics:**
1. **Append-only 载体**：evolution.json 作为升级历史记录
2. **Gate 强制入口**：升级必须通过 Gate 流程

**Evidence Ref:** `三维RAG与数据飞轮约束_v1.md:19-24`

---

## 3. 迁移决策总结

| 组件 | 决策 | 理由 |
|------|------|------|
| draft_revision_autoinc | **MIGRATE** | 核心意图清晰，原子更新约束明确 |
| release_governor | **MIGRATE** | Gate 链式验证是 upgrade_skill 核心逻辑 |
| evolution_manager | **DEFER** | 复杂度高，需独立评估 |
| data_flywheel_constraints | **MIGRATE** | evolution.json 结构定义必要 |

---

## 4. 源文件不存在说明

**任务指定源文件:** `D:\NEW-GM\scripts\update_revision.py`
**状态:** **文件不存在**

**替代来源:**
1. `tests\orchestration\test_draft_revision_autoinc.py` - 提供 revision 自增语义
2. `src\services\outer_skill_factory\release_governor.py` - 提供 DRAFT→ACTIVE 升级逻辑
3. `docs\2026-02-17\三维RAG与数据飞轮约束_v1.md` - 提供 evolution.json 结构定义

---

## 5. 关键发现

1. **revision 自增逻辑** 存在于测试用例中，语义清晰可迁移
2. **Gate 链式验证** 已在 release_governor.py 中实现，支持 Fail-closed 原则
3. **evolution.json** 作为 append-only 载体，需在合约中定义 schema
4. **原子更新约束** 是核心要求，必须在合约 validation_rules 中明确
5. **evolution_manager** 复杂度高，建议 DEFER 到后续 Wave

---

## 6. 阻塞问题

**无阻塞问题** - 所有核心意图已从替代来源提取。

---

*A3 Scan Complete | 2026-02-18*