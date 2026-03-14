# CLEANUP-EXEC-03: 非 Skill 主线业务边界冻结报告

**Task ID**: CLEANUP-EXEC-03
**Execution Date**: 2026-03-11
**Status**: COMPLETE
**Mode**: Fail-Closed (Observation Only)

---

## Decision

**BOUNDARY_FROZEN** - Non-Skill业务线边界已冻结，标记为剥离候选

---

## Executive Summary

根据执行单 [仓库清理_非skill剥离执行单_2026-03-11.md](../仓库清理_非skill剥离执行单_2026-03-11.md)，已完成 P0-3 任务：**冻结非 skill 主线业务边界**。

**核心决策**：
1. `quant-trading-system` 业务线 → 标记为独立仓迁移候选 A
2. `pseo-matrix` 业务线 → 标记为独立仓迁移候选 B
3. **从现在起，上述业务不再参与 SkillForge 主线完成度判断**

**硬约束遵守**：
- 未改动代码
- 未移动目录
- 未删除文件
- 未声称"已迁移完成"

---

## Boundary Decisions

### 决策 1: adapters/quant/

| 属性 | 值 |
|------|-----|
| **是否属于 SkillForge 主线** | 否 |
| **业务类型** | 量化交易适配器 |
| **归属业务线** | quant-trading-system (候选 A) |
| **从现在起不再参与主线判断** | 是 |
| **后续建议** | 独立仓迁移 |

**说明**：
- 包含量化策略、数据获取、回测等非 SkillForge 核心功能
- 属于量化交易业务线的一部分

---

### 决策 2: quant-system/

| 属性 | 值 |
|------|-----|
| **是否属于 SkillForge 主线** | 否 |
| **业务类型** | 量化交易系统 |
| **归属业务线** | quant-trading-system (候选 A) |
| **从现在起不再参与主线判断** | 是 |
| **后续建议** | 独立仓迁移 |

**说明**：
- 独立的量化交易系统，包含自己的 contracts、skills、docs
- 有独立的 CONSTITUTION_ALIGNMENT.md 和 DEPRECATED.md
- 明确为独立业务单元

---

### 决策 3: demo_trading_data/

| 属性 | 值 |
|------|-----|
| **是否属于 SkillForge 主线** | 否 |
| **业务类型** | 交易数据 (演示/测试) |
| **归属业务线** | quant-trading-system (候选 A) |
| **从现在起不再参与主线判断** | 是 |
| **后续建议** | 独立仓迁移或归档 |

**说明**：
- 演示/测试用交易数据
- 属于量化业务线的辅助资源

---

### 决策 4: trading_data/

| 属性 | 值 |
|------|-----|
| **是否属于 SkillForge 主线** | 否 |
| **业务类型** | 交易数据 (运行时) |
| **归属业务线** | quant-trading-system (候选 A) |
| **从现在起不再参与主线判断** | 是 |
| **后续建议** | 纳入 .gitignore，独立仓迁移 |

**说明**：
- 运行时生成的交易数据
- 应在 .gitignore 中排除 (P0-1 范围)

---

### 决策 5: export-seo/

| 属性 | 值 |
|------|-----|
| **是否属于 SkillForge 主线** | 否 |
| **业务类型** | SEO 审计工具导出 |
| **归属业务线** | pseo-matrix (候选 B) |
| **从现在起不再参与主线判断** | 是 |
| **后续建议** | 独立仓迁移 |

**说明**：
- 包含 SEO checker HTML 文件
- 与 pseo/ 业务相关

---

### 决策 6: pseo/

| 属性 | 值 |
|------|-----|
| **是否属于 SkillForge 主线** | 否 |
| **业务类型** | SEO 审计工具 (pSEO Matrix) |
| **归属业务线** | pseo-matrix (候选 B) |
| **从现在起不再参与主线判断** | 是 |
| **后续建议** | 独立仓迁移 |

**说明**：
- 包含多个 SEO 审计报告 HTML
- 与 SkillForge 核心业务无关

---

### 决策 7: 根目录 SEO checker HTML

| 属性 | 值 |
|------|-----|
| **是否属于 SkillForge 主线** | 否 |
| **业务类型** | SEO 审计工具 |
| **归属业务线** | pseo-matrix (候选 B) |
| **从现在起不再参与主线判断** | 是 |
| **后续建议** | 并入 export-seo，独立仓迁移 |

**文件列表**：
```
nextjs-ai-seo-checker.html
shopify-ai-seo-checker.html
svelte-ai-seo-checker.html
vite-ai-seo-checker.html
wordpress-ai-seo-checker.html
```

**说明**：
- 与 export-seo/ 内文件重复
- P0-2 根目录散落文件整理范围

---

## Out of Mainline Scope

以下路径已正式标记为 **非 SkillForge 主线业务**：

| 路径 | 业务线 | 剥离类型 |
|------|--------|----------|
| `adapters/quant/` | quant-trading-system | 独立仓迁移 |
| `quant-system/` | quant-trading-system | 独立仓迁移 |
| `demo_trading_data/` | quant-trading-system | 独立仓迁移/归档 |
| `trading_data/` | quant-trading-system | .gitignore + 独立仓迁移 |
| `export-seo/` | pseo-matrix | 独立仓迁移 |
| `pseo/` | pseo-matrix | 独立仓迁移 |
| `根目录 SEO checker HTML` | pseo-matrix | 独立仓迁移 |

**生效时间**：2026-03-11
**含义**：上述路径不再参与任何 SkillForge 主线完成度判断

---

## Migration Candidates

### 候选 A: quant-trading-system

**建议仓库名**: `quant-trading-system`

**迁移范围**：
```
adapters/quant/
quant-system/
demo_trading_data/
trading_data/
check_akshare_funcs.py
check_institution.py
scripts/check_quant_stack.py
scripts/start_quant_stack.ps1
scripts/start_quant_stack.sh
docs/2026-02-22/量化/
docs/A_SHARE_STRATEGY_GUIDE.md
docs/QUANT_STRATEGY_GUIDE.md
```

**预期保留依赖**：
- 无 (独立业务线)

---

### 候选 B: pseo-matrix

**建议仓库名**: `pseo-matrix`

**迁移范围**：
```
export-seo/
pseo/
nextjs-ai-seo-checker.html
shopify-ai-seo-checker.html
svelte-ai-seo-checker.html
vite-ai-seo-checker.html
wordpress-ai-seo-checker.html
```

**预期保留依赖**：
- 无 (独立业务线)

---

## Archive Candidates

| 路径 | 理由 | 建议操作 |
|------|------|----------|
| `lobster-p2a.tar.gz` | 未知来源归档 | 按 REPO-SCAN-03 处理 |
| `skillforge_src.tar.gz` | 源码备份 | 按 REPO-SCAN-03 处理 |
| `Audit_Report_*.html` (根目录) | 审计报告产物 | 移入 `audit/` 或 `reports/` |

---

## Risks

| Risk ID | Severity | Description | Mitigation |
|---------|----------|-------------|------------|
| R-03-001 | LOW | quant-system 可能有未文档化的依赖 | 迁移前进行依赖扫描 |
| R-03-002 | LOW | pseo 业务可能仍在使用中 | 迁移前确认业务状态 |
| R-03-003 | LOW | 根目录 HTML 可能被外部引用 | 确认无外部链接后再移动 |
| R-03-004 | MEDIUM | trading_data 运行时生成需 .gitignore | 纳入 P0-1 执行 |

---

## Evidence References

| Evidence Type | Path/Reference | Status |
|---------------|----------------|--------|
| 执行单 | docs/2026-03-11/仓库清理_非skill剥离执行单_2026-03-11.md | EXISTS |
| SCAN-01 Report | docs/2026-03-11/repo_cleanup_round1/REPO-SCAN-01_report.md | EXISTS |
| SCAN-02 Report | docs/2026-03-11/repo_cleanup_round1/REPO-SCAN-02_report.md | EXISTS |
| 边界冻结记录 | 本文档 | COMPLETE |

---

## Mainline Retention

以下 **保留为 SkillForge 主线**：

```
core/
contracts/
schemas/
orchestration/
skills/
skillforge/
scripts/ (除 quant 相关)
configs/
permits/
docs/ (除 quant/seo 子目录)
workflows/
ui/ (SkillForge 主线相关部分)
```

---

## Completion Statement

**P0-3 任务完成**：

- [x] 7 个目标路径边界已明确
- [x] 非 Skill 业务线已标记为剥离候选
- [x] 后续主线判断不再混入这些业务
- [x] 未改动代码/移动目录/删除文件
- [x] 未声称"已迁移完成"

**后续步骤**：
1. P0-1: Git 忽略与运行时杂质收口
2. P0-2: 根目录散落文件分类
3. P1-1: 独立仓迁移 (需单独决策)
4. P1-2: 归档操作 (需单独决策)

---

**CLEANUP-EXEC-03 完**
**Signed-off-by**: CLEANUP-EXEC-03 (Automated)
**Gate Decision**: BOUNDARY_FROZEN
**Date**: 2026-03-11
