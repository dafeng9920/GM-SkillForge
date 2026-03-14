# P3 Baseline Inventory (纠偏版)

**任务ID**: T3-A-P3-BASELINE
**状态**: ✅ COMPLETED
**更新时间**: 2026-03-08 10:36 UTC

---

## 分类标准

| 类别 | 含义 | 条件 |
|------|------|------|
| **promote_now** | 立即晋升为正式产物 | 文件存在、哈希有效、用途明确、已验证 |
| **keep_docs_backed_with_reason** | 保留为文档支撑 | 有历史价值但非核心交付物 |
| **defer** | 延后处理 | 需要更多信息或依赖未解决 |

---

## 分类结果

### Wave 1: 已晋升 Mainline

#### 1. intent_map.yml

| 属性 | 值 |
|------|-----|
| **disposition** | **promote_now** |
| **reason** | 核心编排文件，定义 intent 映射关系，已晋升 mainline，无替代方案 |
| **路径** | `skillforge/src/orchestration/intent_map.yml` |
| **SHA256** | `366829a26ce47f24aa46c9968dfc5e7e68f31a3bc1468d81061a7b87300e730a` |
| **大小** | 509 bytes |
| **schema_version** | `0.1.0` |
| **map_version** | `l4.2-first-batch` |

---

#### 2. outer_intent_ingest.yml

| 属性 | 值 |
|------|-----|
| **disposition** | **promote_now** |
| **reason** | 已晋升 mainline，定义外源 intent 接入流程 |
| **路径** | `contracts/intents/outer_intent_ingest.yml` |
| **SHA256** | `5fcb7d9da5c545487870e627f8f7cc7bd7d8386b998854e222f8d774b5b3cde5` |
| **大小** | 169 bytes |
| **integration_level** | `mainline` |

---

#### 3. outer_contract_freeze.yml

| 属性 | 值 |
|------|-----|
| **disposition** | **promote_now** |
| **reason** | 已晋升 mainline，定义 contract 冻结流程 |
| **路径** | `contracts/intents/outer_contract_freeze.yml` |
| **SHA256** | `9d90d8f42d0a67562eb4ff3897f190336e6ad55491e68a7c637f7fecd8694ca2` |
| **大小** | 178 bytes |
| **integration_level** | `mainline` |

---

### Wave 2: 待处理

#### 4. audit_repo_skill.yml

| 属性 | 值 |
|------|-----|
| **disposition** | **defer** |
| **reason** | 待 Wave 2 处理，需进一步审核 skill 定义完整性及与 governor-skill 的关系 |
| **路径** | `contracts/intents/audit_repo_skill.yml` |
| **SHA256** | 待 Wave 2 计算 |
| **dependency** | Wave 2 governance 审核完成 |
---

#### 5. tombstone_skill.yml

| 属性 | 值 |
|------|-----|
| **disposition** | **defer** |
| **reason** | 待 Wave 2 处理，需确认 tombstone 机制与现有 governance 流程的集成点 |
| **路径** | `contracts/intents/tombstone_skill.yml` |
| **SHA256** | 待 Wave 2 计算 |
| **dependency** | Wave 2 governance 审核完成 |

---
## 分类汇总

| 类别 | 数量 | 文件 |
|------|------|------|
| promote_now | 3 | intent_map.yml, outer_intent_ingest.yml, outer_contract_freeze.yml |
| keep_docs_backed_with_reason | 0 | - |
| defer | 2 | audit_repo_skill.yml, tombstone_skill.yml |

---

## 验证状态

| 检查项 | 状态 | 证据 |
|--------|------|------|
| Wave 1 文件存在 | ✅ 3/3 | 路径可访问 |
| Wave 1 SHA256 已记录 | ✅ 3/3 | 完整哈希已记录 |
| Wave 1 integration_level = mainline | ✅ 2/2 | contracts 已晋升 |
| Wave 2 文件待处理 | ⏳ 2 | 待 Wave 2 审核 |

---

## 结论

**Wave 1**: 3 个文件已晋升 mainline，disposition = promote_now

**Wave 2**: 2 个文件待处理，disposition = defer
- audit_repo_skill.yml
- tombstone_skill.yml

**遗留项**: 是，存在 2 个 Wave 2 待处理文件
