# CLEANUP-EXEC-02: 根目录散落文件第一次分类报告

> **任务目标**: P0-2 根目录散落文件分类（不做删除，只做归类与搬迁计划）
> **执行日期**: 2026-03-11
> **执行依据**: docs/2026-03-11/仓库清理_非skill剥离执行单_2026-03-11.md
> **硬约束**: 不删除文件、不移动文件、不改文件内容、不得遗漏、不得把"分类建议"写成"已执行搬迁"

---

## 执行摘要

| 分类 | 文件数 | 说明 |
|------|--------|------|
| keep_in_root | 2 | 保留在根目录的核心文件 |
| move_to_scripts_dev | 13 | 开发脚本移入 scripts/dev/ |
| move_to_reports_or_audit | 11 | 审计/报告产物移入 reports/ 或 audit/ |
| merge_into_pseo_bucket | 6 | SEO 页面并入 pseo 候选 |
| merge_into_quant_bucket | 2 | 量化工具并入 quant 候选 |
| delete_candidates | 1 | 临时调试日志 |
| **合计** | 35 | 完整覆盖所有指定文件 |

---

## 分类表

### 1. keep_in_root (保留根目录)

| 文件 | 大小 | 理由 |
|------|------|------|
| `simple_api.py` | 13,595 bytes | L4 API 服务器完整功能版本，属于 SkillForge 主线 API 基础设施 |
| `multi-ai-collaboration.md` | 14,030 bytes | GM 多 AI 协作工作流文档（v3，三权分立），属于主线治理文档，建议移至 docs/ 但暂保留根目录作为快速参考 |

---

### 2. move_to_scripts_dev (移入 scripts/dev/)

| 文件 | 大小 | 理由 | 目标子目录 |
|------|------|------|-----------|
| `test_regex.py` | 399 bytes | 正则测试脚本 | scripts/dev/ |
| `test_regex2.py` | 425 bytes | 正则测试脚本 v2 | scripts/dev/ |
| `test_regex3.py` | 463 bytes | 正则测试脚本 v3 | scripts/dev/ |
| `patch_imports.py` | 582 bytes | 导入补丁工具 | scripts/dev/ |
| `patch_script.py` | 568 bytes | 脚本补丁工具 | scripts/dev/ |
| `patch_test.py` | 3,548 bytes | 补丁测试脚本 | scripts/dev/ |
| `bulk_patch_imports.py` | 1,769 bytes | 批量导入补丁工具 | scripts/dev/ |
| `create_dummy_packs.py` | 1,036 bytes | 创建测试数据包 | scripts/dev/ |
| `create_valid_dummy_packs.py` | 1,613 bytes | 创建有效测试数据包 | scripts/dev/ |
| `insert_debug.py` | 1,266 bytes | 调试插入工具 | scripts/dev/ |
| `rewrite_registry.py` | 11,912 bytes | 注册表重写工具 | scripts/dev/ |
| `chat_to_md.py` | 2,283 bytes | 聊天转 Markdown 工具 | scripts/dev/ |
| `run_api.py` | 1,138 bytes | API 运行脚本（与 scripts/dev/run_api.py 重复，合并后删除根目录版本） | scripts/dev/ |

---

### 3. move_to_reports_or_audit (移入 reports/ 或 audit/)

| 文件 | 大小 | 理由 | 目标目录 |
|------|------|------|----------|
| `Audit_Report_Final.html` | 58,579 bytes | 最终审计报告产物 | reports/audit_reports/ |
| `Audit_Report_genesismind_ai.html` | 57,208 bytes | genesismind.ai 审计报告产物 | reports/audit_reports/ |
| `Audit_Report_indiajobsdekho.json` | 0 bytes | indyajobsdekho 审计报告（空文件） | reports/audit_reports/ 或删除 |
| `test_wave3_verification.py` | 17,324 bytes | Wave3 验证测试脚本/报告 | reports/wave3/ |
| `DiffReport.json` | 94 bytes | 结构差异报告 | reports/governance/ |
| `RegressionReport.json` | 1,898 bytes | 量化交易系统回归测试报告 | reports/governance/ |
| `ReleaseManifest.json` | 1,708 bytes | 量化交易系统发布清单 v1.1.0 | reports/governance/ |
| `Ruling.json` | 2,584 bytes | 治理裁决记录（RULING-2026-02-25-ROUND4-001） | reports/governance/ |
| `UpdatedGraph.json` | 4,243 bytes | 量化交易系统依赖图更新 | reports/governance/ |
| `audit_report_boundary.json` | 276 bytes | 审计报告边界检查 | reports/governance/ |
| `audit_report_consistency.json` | 388 bytes | 审计报告一致性检查 | reports/governance/ |

---

### 4. merge_into_pseo_bucket (并入 pseo 候选)

| 文件 | 大小 | 理由 | 目标 |
|------|------|------|------|
| `index.html` | 14,474 bytes | AI SEO 检查器主页，属于 pseo-matrix 产品 | 并入 pseo/ 或 export-seo/ |
| `nextjs-ai-seo-checker.html` | 14,854 bytes | Next.js 版 SEO 检查器 | 并入 pseo/ 或 export-seo/ |
| `shopify-ai-seo-checker.html` | 14,857 bytes | Shopify 版 SEO 检查器 | 并入 pseo/ 或 export-seo/ |
| `svelte-ai-seo-checker.html` | 14,855 bytes | Svelte 版 SEO 检查器 | 并入 pseo/ 或 export-seo/ |
| `vite-ai-seo-checker.html` | 14,855 bytes | Vite 版 SEO 检查器 | 并入 pseo/ 或 export-seo/ |
| `wordpress-ai-seo-checker.html` | 14,849 bytes | WordPress 版 SEO 检查器 | 并入 pseo/ 或 export-seo/ |

---

### 5. merge_into_quant_bucket (并入 quant 候选)

| 文件 | 大小 | 理由 | 目标 |
|------|------|------|------|
| `check_akshare_funcs.py` | 3,875 bytes | AKShare 函数查找工具，属于 quant-trading-system | 并入 adapters/quant/tools/ 或随 quant 独立仓迁移 |
| `check_institution.py` | 5,055 bytes | A股机构持仓数据查询工具，属于 quant-trading-system | 并入 adapters/quant/tools/ 或随 quant 独立仓迁移 |

---

### 6. delete_candidates (删除候选)

| 文件 | 理由 |
|------|------|
| `gcm-diagnose.log` | 诊断日志文件（12,483 bytes），临时调试产物，已过时效，建议删除 |

---

### 7. 超出 P0-2 重点对象的补充说明

以下文件超出 `docs/2026-03-11/仓库清理_非skill剥离执行单_2026-03-11.md` 中 P0-2 重点对象清单，但属于根目录散落文件，因此一并纳入第一次分类：

| 文件 | 理由 |
|------|------|
| `test_wave3_verification.py` | Wave3 验证测试脚本，非 P0-2 重点对象，但属于根目录散落文件 |
| `simple_api.py` | L4 API 服务器，非 P0-2 重点对象，但属于根目录散落文件 |
| `multi-ai-collaboration.md` | 多 AI 协作工作流文档，非 P0-2 重点对象，但属于根目录散落文件 |
| `rewrite_registry.py` | 注册表重写工具，非 P0-2 重点对象，但属于根目录散落文件 |
| `chat_to_md.py` | 聊天转 Markdown 工具，非 P0-2 重点对象，但属于根目录散落文件 |
| `run_api.py` | API 运行脚本，非 P0-2 重点对象，但属于根目录散落文件 |
| `DiffReport.json` | 结构差异报告，非 P0-2 重点对象，但属于根目录散落文件 |
| `RegressionReport.json` | 回归测试报告，非 P0-2 重点对象，但属于根目录散落文件 |
| `ReleaseManifest.json` | 发布清单，非 P0-2 重点对象，但属于根目录散落文件 |
| `UpdatedGraph.json` | 依赖图更新，非 P0-2 重点对象，但属于根目录散落文件 |

**说明**: 以上文件虽不在 P0-2 重点对象清单中，但实际存在于根目录且属于需要分类的散落文件。为避免遗漏，本报告将其纳入分类表。

---

### 8. 排除说明

| 文件 | 排除理由 |
|------|----------|
| `start_backend.py` | 已存在于 `scripts/dev/start_backend.py`，根目录版本在确认内容一致性后删除，本轮未纳入正式分类表 |
| `start_full_api.py` | 已存在于 `scripts/dev/start_full_api.py`，根目录版本在确认内容一致性后删除，本轮未纳入正式分类表 |

---

## 风险评估

| 风险ID | 级别 | 描述 | 缓解措施 |
|--------|------|------|----------|
| R-001 | LOW | `run_api.py` 与 scripts/dev/run_api.py 重复 | 合并后删除根目录版本 |
| R-002 | LOW | `start_backend.py`, `start_full_api.py` 与 scripts/dev/ 中文件重复 | 已在"排除说明"小节中说明，确认内容一致性后删除根目录版本 |
| R-003 | MEDIUM | `simple_api.py` 可能有其他脚本引用 | 搜索代码库引用，确认无依赖后再移动 |
| R-004 | LOW | `Audit_Report_indiajobsdekho.json` 为空文件 | 确认是否为有效占位符或直接删除 |
| R-005 | LOW | `multi-ai-collaboration.md` 建议移至 docs/ | 暂保留根目录，后续组织到 docs/ |
| R-006 | LOW | `gcm-diagnose.log` 删除候选，可能包含历史调试信息 | 确认日志已过时效且无保留价值后删除 |

---

## 执行建议

### 阶段 1: 创建目标目录
```bash
mkdir -p scripts/dev
mkdir -p reports/audit_reports
mkdir -p reports/governance
mkdir -p reports/wave3
mkdir -p logs
```

### 阶段 2: 移动开发脚本
```bash
# 移动到 scripts/dev/
mv test_regex*.py scripts/dev/
mv patch_*.py scripts/dev/
mv bulk_patch_imports.py scripts/dev/
mv create_*_packs.py scripts/dev/
mv insert_debug.py scripts/dev/
mv rewrite_registry.py scripts/dev/
mv chat_to_md.py scripts/dev/
mv run_api.py scripts/dev/  # 合并后删除重复
```

### 阶段 3: 移动报告产物
```bash
# 移动到 reports/audit_reports/
mv Audit_Report_*.html reports/audit_reports/
mv Audit_Report_indiajobsdekho.json reports/audit_reports/

# 移动到 reports/governance/
mv *.json reports/governance/  # 注意：仅移动治理相关 JSON

# 移动到 reports/wave3/
mv test_wave3_verification.py reports/wave3/
```

### 阶段 4: 合并到 pseo 候选
```bash
# 待 REPO-SCAN-03 确认合并策略后执行
# mv *.html pseo/ 或 export-seo/
```

### 阶段 5: 合并到 quant 候选
```bash
# 待 quant 独立仓迁移时执行
# mv check_*.py adapters/quant/tools/
```

### 阶段 6: 删除临时文件
```bash
# 删除临时调试日志
rm gcm-diagnose.log

# 删除根目录重复的启动脚本（在确认与 scripts/dev/ 一致后）
rm start_backend.py
rm start_full_api.py
```

---

## 证据引用

| 引用类型 | 路径 |
|----------|------|
| 执行依据 | docs/2026-03-11/仓库清理_非skill剥离执行单_2026-03-11.md |
| 扫描报告 | docs/2026-03-11/repo_cleanup_round1/REPO-SCAN-02_report.md |
| P0-2 定义 | docs/2026-03-11/仓库清理_非skill剥离执行单_2026-03-11.md (P0-2 节) |

---

## 完成确认

- [x] 所有指定文件已覆盖
- [x] 分类表完整
- [x] 不包含"已执行搬迁"表述
- [x] 风险已评估
- [x] 执行建议已提供

---

**报告生成时间**: 2026-03-11
**任务状态**: COMPLETED
**下一步**: REVIEW_report.md 审查
