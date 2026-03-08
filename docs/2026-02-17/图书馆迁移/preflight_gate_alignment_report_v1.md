# Preflight Gate Alignment Report v1

> **生成时间**: 2026-02-18
> **执行者**: CC-Code
> **范围**: Wave4 Batch1 - Gate 名称与注册表对齐检查

---

## 1. Gate 注册表（Canonical 名称）

来源：`skillforge-spec-pack/orchestration/nodes/*.node.schema.json`

| # | Canonical Gate 名称 | 类型 | 描述 |
|---|---------------------|------|------|
| 1 | `intake_repo` | Node | 接收仓库，验证 repo_url + commit_sha |
| 2 | `license_gate` | Gate | 许可证检查 |
| 3 | `repo_scan_fit_score` | Node | 仓库扫描适配度评估 |
| 4 | `draft_skill_spec` | Node | 技能规格草稿 |
| 5 | `constitution_risk_gate` | Gate | 宪法风险检查 |
| 6 | `scaffold_skill_impl` | Node | 技能实现脚手架 |
| 7 | `sandbox_test_and_trace` | Node | 沙箱测试与追踪 |
| 8 | `pack_audit_and_publish` | Node | 打包审计并发布 |

**注册表状态**: 8 个已注册 Gate/Node

---

## 2. Intent 合约 Gate 依赖分析

### 2.1 audit_repo.yml

| 合约中的 Gate | 在注册表中 | 状态 |
|---------------|------------|------|
| `intake_repo` | ✅ | ALIGNED |
| `license_gate` | ✅ | ALIGNED |
| `repo_scan_fit_score` | ✅ | ALIGNED |
| `pack_audit_and_publish` | ✅ | ALIGNED |

**结论**: ✅ 4/4 已对齐

---

### 2.2 generate_skill.yml

| 合约中的 Gate | 在注册表中 | 状态 | 建议 |
|---------------|------------|------|------|
| `proposal_gate` | ❌ | NOT_REGISTERED | 需实现或映射 |
| `build_gate` | ❌ | NOT_REGISTERED | 需实现或映射 |
| `license_compatibility` | ❌ | NOT_REGISTERED | 映射到 `license_gate` |
| `tier_risk_gate` | ❌ | NOT_REGISTERED | 需实现或映射 |

**结论**: ⚠️ 0/4 未对齐

**修正建议**:
- `license_compatibility` → `license_gate` (别名映射)
- `proposal_gate` → 新增注册
- `build_gate` → 新增注册
- `tier_risk_gate` → 新增注册

---

### 2.3 upgrade_skill.yml

| 合约中的 Gate | 在注册表中 | 状态 | 建议 |
|---------------|------------|------|------|
| `build_gate` | ❌ | NOT_REGISTERED | 需实现或映射 |
| `trace_reputation_gate` | ❌ | NOT_REGISTERED | 需实现或映射 |
| `compose_gate` | ❌ | NOT_REGISTERED | 映射到 `skill_compose` |
| `run_gate` | ❌ | NOT_REGISTERED | 需实现或映射 |

**结论**: ⚠️ 0/4 未对齐

**修正建议**:
- `compose_gate` → `skill_compose` (别名映射，需在 specs/nodes 中确认)
- `build_gate` → 新增注册
- `trace_reputation_gate` → 新增注册
- `run_gate` → 新增注册

---

### 2.4 tombstone.yml

| 合约中的 Gate | 在注册表中 | 状态 | 建议 |
|---------------|------------|------|------|
| `intake_validate` | ❌ | NOT_REGISTERED | 映射到 `intake_repo` |
| `constitution_risk_gate` | ✅ | ALIGNED | - |
| `tombstone_write_gate` | ❌ | NOT_REGISTERED | 需实现或映射 |
| `audit_chain_append` | ❌ | NOT_REGISTERED | 需实现或映射 |
| `tombstone_publish` | ❌ | NOT_REGISTERED | 需实现或映射 |

**结论**: ⚠️ 1/5 已对齐

**修正建议**:
- `intake_validate` → `intake_repo` (别名映射)
- `tombstone_write_gate` → 新增注册
- `audit_chain_append` → 新增注册
- `tombstone_publish` → 新增注册

---

### 2.5 time_semantics.yml

| 合约中的 Gate | 在注册表中 | 状态 | 建议 |
|---------------|------------|------|------|
| `time_constraint_gate` | ❌ | NOT_REGISTERED | 需实现或映射 |
| `data_freshness_gate` | ❌ | NOT_REGISTERED | 需实现或映射 |
| `look_ahead_prevention` | ❌ | NOT_REGISTERED | 需实现或映射 |

**结论**: ⚠️ 0/3 未对齐

**修正建议**:
- 全部为新增 Gate，需实现并注册

---

## 3. 对齐状态汇总

| Intent | 已对齐 | 未对齐 | 需新增注册 | 可别名映射 |
|--------|--------|--------|------------|------------|
| audit_repo | 4 | 0 | 0 | 0 |
| generate_skill | 0 | 4 | 3 | 1 |
| upgrade_skill | 0 | 4 | 3 | 1 |
| tombstone | 1 | 4 | 3 | 1 |
| time_semantics | 0 | 3 | 3 | 0 |
| **总计** | **5** | **15** | **12** | **3** |

---

## 4. 需新增注册的 Gate 清单

| Gate 名称 | 优先级 | 所属 Intent | 说明 |
|-----------|--------|-------------|------|
| `proposal_gate` | P0 | generate_skill | 验证请求完整性 |
| `build_gate` | P0 | generate_skill, upgrade_skill | 验证构建资格 |
| `tier_risk_gate` | P0 | generate_skill | 风险等级 Gate |
| `trace_reputation_gate` | P0 | upgrade_skill | 查询 TraceStore 统计 |
| `run_gate` | P0 | upgrade_skill | 评估 run 执行权限 |
| `tombstone_write_gate` | P0 | tombstone | 废弃写入 Gate |
| `audit_chain_append` | P0 | tombstone | 审计链追加 |
| `tombstone_publish` | P0 | tombstone | 废弃发布 |
| `time_constraint_gate` | P1 | time_semantics | 时间约束验证 |
| `data_freshness_gate` | P1 | time_semantics | 数据新鲜度检查 |
| `look_ahead_prevention` | P1 | time_semantics | 前视偏差防护 |

**总计**: 11 个需新增注册

---

## 5. 别名映射建议

| 合约中的名称 | 映射到 Canonical | 说明 |
|--------------|------------------|------|
| `license_compatibility` | `license_gate` | 同一功能，命名不同 |
| `compose_gate` | `skill_compose` | 同一功能，需确认 |
| `intake_validate` | `intake_repo` | 同一功能，命名不同 |

---

## 6. 修正策略

### 6.1 策略 A: 扩展注册表（推荐）

在 `skillforge-spec-pack/orchestration/nodes/` 中新增 11 个 Gate 的 schema 文件：

```
nodes/
├── proposal_gate.node.schema.json          # 新增
├── build_gate.node.schema.json             # 新增
├── tier_risk_gate.node.schema.json         # 新增
├── trace_reputation_gate.node.schema.json  # 新增
├── run_gate.node.schema.json               # 新增
├── tombstone_write_gate.node.schema.json   # 新增
├── audit_chain_append.node.schema.json     # 新增
├── tombstone_publish.node.schema.json      # 新增
├── time_constraint_gate.node.schema.json   # 新增
├── data_freshness_gate.node.schema.json    # 新增
└── look_ahead_prevention.node.schema.json  # 新增
```

### 6.2 策略 B: 合约别名修正

修改 intent 合约中的 Gate 名称以匹配注册表：

| Intent | 原名称 | 修正为 |
|--------|--------|--------|
| generate_skill | `license_compatibility` | `license_gate` |
| upgrade_skill | `compose_gate` | `skill_compose` |
| tombstone | `intake_validate` | `intake_repo` |

### 6.3 推荐执行顺序

1. **立即执行**: 策略 B（修正 3 个别名）
2. **Batch1 期间**: 策略 A（实现 11 个新增 Gate）

---

## 7. 风险评估

| 风险项 | 级别 | 缓解措施 |
|--------|------|----------|
| Gate 名称漂移导致运行时失败 | 高 | 先修正别名，再扩展注册表 |
| 新增 Gate 实现延迟 | 中 | 优先实现 audit_repo 链路 |
| 合约与实现不一致 | 高 | 严格按 Gate 链顺序验证 |

---

## 8. 验收结论

**PREFLIGHT CHECK A2: ⚠️ CONDITIONAL PASS**

- audit_repo 的 4 个 Gate 全部对齐 ✅
- 其余 4 个 Intent 有 Gate 名称漂移，需修正

**放行条件**:
1. 执行策略 B 修正 3 个别名
2. 按顺序实现新增 Gate

---

## 9. 下一步行动

| 优先级 | 动作 | 负责者 |
|--------|------|--------|
| P0 | 修正 generate_skill.yml: license_compatibility → license_gate | CC-Code |
| P0 | 修正 upgrade_skill.yml: compose_gate → skill_compose | CC-Code |
| P0 | 修正 tombstone.yml: intake_validate → intake_repo | CC-Code |
| P0 | 实现剩余 11 个 Gate schema | Batch1 实现 |

---

*Generated by CC-Code | Wave4 Batch1 Preflight | 2026-02-18*
