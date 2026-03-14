# REPO-SCAN-01 仓库清理盘点报告

**任务编号**: REPO-SCAN-01
**生成时间**: 2026-03-11
**执行人**: Claude (REPO-SCAN-01)
**仓库**: GM-SkillForge
**远程**: https://github.com/genesismind-bot/GM-SkillForge.git

---

## 任务范围

- 仓库根目录文件
- 顶层目录结构
- artifacts/
- audit/
- audit_pack/
- AuditPack/
- dropzone/
- reports/

---

## 执行摘要

| 分类 | 数量 | 说明 |
|------|------|------|
| 保留 (KEEP) | 37 | 核心项目结构，无需处理 |
| 归档 (ARCHIVE) | 21 | 历史记录，建议保留或移动到归档存储 |
| 剥离 (EXTRACT) | 13 | 应移出仓库的嵌套仓库/运行时数据/敏感文件 |
| 删除候选 (DELETE) | 40+ | 临时文件、散落文件、缓存 |
| 待确认 (PENDING) | 4 | 需进一步确认用途 |

---

## 1. 保留 (KEEP) - 核心项目结构

| Path | Category | Reason | Risk |
|------|----------|--------|------|
| `adapters/` | 核心代码 | 量化适配器层，生产代码 | - |
| `configs/` | 配置 | 技能层级注册表等配置 | - |
| `contracts/` | 合约 | 智能合约代码 | - |
| `core/` | 核心代码 | 核心业务逻辑 | - |
| `data/` | 数据 | 项目数据文件 | - |
| `docker/` | 基础设施 | Docker配置 | - |
| `docs/` | 文档 | 项目文档 | - |
| `functions/` | 核心代码 | 函数库 | - |
| `orchestration/` | 核心代码 | 编排服务 | - |
| `permits/` | 治理 | 许可证管理 | - |
| `pseo/` | 核心代码 | pSEO引擎 | - |
| `schemas/` | 模式 | JSON Schema定义 | - |
| `scripts/` | 工具 | 自动化脚本 | - |
| `skills/` | 核心代码 | 技能包 | - |
| `templates/` | 模板 | HTML/MD模板 | - |
| `tests/` | 测试 | 测试代码 | - |
| `tools/` | 工具 | 工具集 | - |
| `ui/` | 前端 | Web界面 | - |
| `workflows/` | 工作流 | n8n工作流 | - |
| `skillforge/` | 核心代码 | SkillForge引擎 | - |
| `skillforge-spec-pack/` | 核心代码 | 规范包 | - |
| `skillforge-web/` | 前端 | Web前端 | - |
| `ci/` | CI配置 | CI/CD配置 | - |
| `security/` | 安全 | 安全相关配置 | - |
| `registry/` | 注册表 | 注册表服务 | - |
| `regression/` | 回归 | 回归测试 | - |
| `scanner/` | 扫描器 | 扫描工具 | - |
| `gm_plugin_core_seed/` | 核心组件 | 插件核心种子 | - |
| `openclaw-box/` | 核心组件 | OpenClaw盒子 | - |
| `quant-system/` | 核心组件 | 量化系统 | - |
| `.github/` | 仓库配置 | GitHub配置 | - |
| `.vscode/` | 仓库配置 | VSCode配置 | - |
| `.gitignore` | 仓库配置 | Git忽略规则 | - |
| `README.md` | 文档 | 项目说明 | - |
| `CODEX_STARTER.md` | 文档 | 代码启动指南 | - |
| `package.json` | 配置 | Node.js包配置 | - |
| `.env.example` | 配置模板 | 环境变量示例 | - |

---

## 2. 归档 (ARCHIVE) - 历史记录保留

| Path | Category | Reason | Risk |
|------|----------|--------|------|
| `artifacts/` | 归档 | TG1基线证据，历史快照 | 低 |
| `AuditPack/evidence/` | 归档 | 大量历史审计证据文件 (158KB) | 低 |
| `audit_pack/tg1_audit_pack.json` | 归档 | TG1审计包 | 低 |
| `audit/` | 归档 | 审计模板，当前审计系统 | 低 |
| `reports/l3_gap_closure/` | 归档 | L3缺口闭合历史报告 | 低 |
| `reports/skill-audit/` | 归档 | 技能审计历史报告 | 低 |
| `reports/phase1_validation.json` | 归档 | 阶段验证报告 | 低 |
| `reports/phase2_validation.json` | 归档 | 阶段验证报告 | 低 |
| `reports/phase3_4_validation.json` | 归档 | 阶段验证报告 | 低 |
| `reports/FINAL_VALIDATION_REPORT.md` | 归档 | 最终验证报告 | 低 |
| `reports/FUNCTIONAL_TEST_SUMMARY.md` | 归档 | 功能测试摘要 | 低 |
| `reports/functional_test_results.json` | 归档 | 功能测试结果 | 低 |
| `reports/api_perimeter_hardening_backlog_pack.json` | 归档 | API加固报告 | 低 |
| `reports/api_perimeter_hardening_backlog_pack.md` | 归档 | API加固报告 | 低 |
| `dropzone/REAL-TASK-002/` | 归档 | 已完成的REAL-TASK-002证据 | 低 |
| `dropzone/TASK-MAIN-01-RETRY/` | 归档 | 已完成的TASK-MAIN-01-RETRY | 低 |
| `SkillPackage/` | 归档 | 历史技能包版本 | 低 |
| `SkillPackage_R2/` | 归档 | 历史技能包版本 | 低 |
| `reports/l5-load/` | 归档 | L5负载测试报告 | 低 |
| `reports/l5-reliability/` | 归档 | L5可靠性报告 | 低 |
| `reports/l5-replay/` | 归档 | L5重放测试报告 | 低 |
| `reports/config/` | 归档 | 报告配置文件 | 低 |

---

## 3. 剥离 (EXTRACT) - 应移出仓库

| Path | Category | Reason | Risk | Suggested Action |
|------|----------|--------|------|------------------|
| `export-seo/` | 嵌套仓库 | 这是一个独立的git仓库，应使用submodule或独立维护 | 中 | 转换为submodule或移到独立仓库 |
| `git-Claude仓库/` | 嵌套仓库 | 这是另一个git仓库的克隆，不应嵌套在主仓库中 | 中 | 移出仓库或删除 |
| `db/skillforge.sqlite` | 运行时数据 | SQLite数据库文件，应在.gitignore中，不应提交 | 高 | 从git中移除，添加到.gitignore |
| `trading_data/` | 运行时数据 | 交易运行时数据，应在.gitignore中 | 高 | 添加到.gitignore |
| `demo_dashboard_data/` | 演示数据 | 演示/测试数据，应移到独立的数据仓库或.gitignore | 中 | 添加到.gitignore |
| `demo_system_data/` | 演示数据 | 演示/测试数据，应移到独立的数据仓库或.gitignore | 中 | 添加到.gitignore |
| `demo_trading_data/` | 演示数据 | 演示/测试数据，应移到独立的数据仓库或.gitignore | 中 | 添加到.gitignore |
| `.env` | 敏感配置 | 包含敏感信息，应在.gitignore中，不应提交 | 高 | 从git中移除，添加到.gitignore |
| `.env.bak` | 敏感配置 | 备份的敏感配置，应删除或.gitignore | 高 | 从git中移除，添加到.gitignore |
| `lobster-p2a.tar.gz` | 归档包 | 源码压缩包，应移到独立的归档仓库 | 低 | 移到独立归档仓库 |
| `skillforge_src.tar.gz` | 归档包 | 源码压缩包，应移到独立的归档仓库 | 低 | 移到独立归档仓库 |
| `dist/` | 构建产物 | 构建输出目录，应在.gitignore中 | 低 | 添加到.gitignore |
| `reports/ALL_TESTS_PASSED.flag` | 运行时标记 | 测试标记文件，应在.gitignore中 | 低 | 添加到.gitignore |

---

## 4. 删除候选 (DELETE) - 可安全删除

### 4.1 临时文件/缓存

| Path | Category | Reason | Risk |
|------|----------|--------|------|
| `.tmp/` | 临时文件 | 大量临时文件（数千个），应清理 | 低 |
| `.pytest_cache/` | 缓存 | pytest缓存，应在.gitignore中 | 低 |
| `GM-SkillForge.tmppytest/` | 测试临时目录 | 测试临时目录，可删除 | 低 |
| `AuditPack/evidence/*.tmp` (19个文件) | 临时文件 | 失败/中断的临时文件 | 低 |

**具体TMP文件清单**:
```
AuditPack/evidence/intake_manifest_REQ-20260220045939.tmp
AuditPack/evidence/intake_manifest_REQ-20260220045940.tmp
AuditPack/evidence/intake_manifest_REQ-20260220050042.tmp
AuditPack/evidence/intake_manifest_REQ-20260220050101.tmp
AuditPack/evidence/intake_manifest_REQ-20260220050457.tmp
AuditPack/evidence/intake_manifest_REQ-20260220050529.tmp
AuditPack/evidence/intake_manifest_REQ-20260220050538.tmp
AuditPack/evidence/intake_manifest_REQ-20260220164557.tmp
AuditPack/evidence/intake_manifest_REQ-20260220164730.tmp
AuditPack/evidence/intake_manifest_REQ-20260220164933.tmp
AuditPack/evidence/scan_report_SCAN-20260220045940.tmp
AuditPack/evidence/scan_report_SCAN-20260220050042.tmp
AuditPack/evidence/scan_report_SCAN-20260220050101.tmp
AuditPack/evidence/scan_report_SCAN-20260220050457.tmp
AuditPack/evidence/scan_report_SCAN-20260220050529.tmp
AuditPack/evidence/scan_report_SCAN-20260220050538.tmp
AuditPack/evidence/scan_report_SCAN-20260220164557.tmp
AuditPack/evidence/scan_report_SCAN-20260220164730.tmp
AuditPack/evidence/scan_report_SCAN-20260220164933.tmp
```

### 4.2 根目录散落文件

| Path | Category | Reason | Risk |
|------|----------|--------|------|
| `Audit_Report_Final.html` | 报告文件 | 根目录散落的报告文件 | 低 |
| `Audit_Report_genesismind_ai.html` | 报告文件 | 根目录散落的报告文件 | 低 |
| `Audit_Report_indiajobsdekho.json` | 报告文件 | 空的JSON文件 | 低 |
| `index.html` | 散落文件 | SEO检查器HTML文件 | 低 |
| `nextjs-ai-seo-checker.html` | 散落文件 | SEO检查器HTML文件 | 低 |
| `shopify-ai-seo-checker.html` | 散落文件 | SEO检查器HTML文件 | 低 |
| `svelte-ai-seo-checker.html` | 散落文件 | SEO检查器HTML文件 | 低 |
| `vite-ai-seo-checker.html` | 散落文件 | SEO检查器HTML文件 | 低 |
| `wordpress-ai-seo-checker.html` | 散落文件 | SEO检查器HTML文件 | 低 |

### 4.3 根目录散落脚本

| Path | Category | Reason | Risk |
|------|----------|--------|------|
| `test_regex.py` | 散落脚本 | 测试脚本 | 低 |
| `test_regex2.py` | 散落脚本 | 测试脚本 | 低 |
| `test_regex3.py` | 散落脚本 | 测试脚本 | 低 |
| `test_wave3_verification.py` | 散落脚本 | 测试脚本 | 低 |
| `patch_imports.py` | 散落脚本 | 补丁脚本 | 低 |
| `patch_script.py` | 散落脚本 | 补丁脚本 | 低 |
| `patch_test.py` | 散落脚本 | 补丁测试脚本 | 低 |
| `bulk_patch_imports.py` | 散落脚本 | 批量补丁脚本 | 低 |
| `create_dummy_packs.py` | 散落脚本 | 创建测试包脚本 | 低 |
| `create_valid_dummy_packs.py` | 散落脚本 | 创建有效测试包脚本 | 低 |
| `chat_to_md.py` | 散落脚本 | 转换脚本 | 低 |
| `insert_debug.py` | 散落脚本 | 调试插入脚本 | 低 |
| `rewrite_registry.py` | 散落脚本 | 重写注册表脚本 | 低 |
| `run_api.py` | 散落脚本 | API运行脚本 | 低 |
| `simple_api.py` | 散落脚本 | 简单API脚本 | 低 |
| `start_backend.py` | 散落脚本 | 后端启动脚本 | 低 |
| `start_full_api.py` | 散落脚本 | 完整API启动脚本 | 低 |
| `check_akshare_funcs.py` | 临时脚本 | 临时检查脚本 | 低 |
| `check_institution.py` | 临时脚本 | 临时检查脚本 | 低 |

### 4.4 根目录散落配置/报告

| Path | Category | Reason | Risk |
|------|----------|--------|------|
| `DiffReport.json` | 散落配置 | 差异报告 | 低 |
| `RegressionReport.json` | 散落配置 | 回归报告 | 低 |
| `ReleaseManifest.json` | 散落配置 | 发布清单 | 低 |
| `Ruling.json` | 散落配置 | 规则配置 | 低 |
| `UpdatedGraph.json` | 散落配置 | 更新图配置 | 低 |
| `audit_report_boundary.json` | 散落配置 | 审计报告边界 | 低 |
| `audit_report_consistency.json` | 散落配置 | 审计报告一致性 | 低 |

### 4.5 根目录散落文档

| Path | Category | Reason | Risk |
|------|----------|--------|------|
| `multi-ai-collaboration.md` | 散落文档 | AI协作文档 | 低 |
| `test-ai-improvement.md` | 散落文档 | AI改进测试文档 | 低 |

### 4.6 日志文件

| Path | Category | Reason | Risk |
|------|----------|--------|------|
| `gcm-diagnose.log` | 诊断日志 | 旧的诊断日志文件 | 低 |
| `logs/` | 运行时日志 | 运行时日志目录 | 低 |

### 4.7 临时工作目录

| Path | Category | Reason | Risk |
|------|----------|--------|------|
| `NewSkillPackage/` | 临时工作目录 | 临时技能包工作目录 | 低 |

### 4.8 Dropzone待确认

| Path | Category | Reason | Risk |
|------|----------|--------|------|
| `dropzone/TASK-MAIN-02/` | 待处理任务 | 只有run_request/result，可能已废弃 | 中 |

---

## 5. 待确认 (PENDING) - 需要进一步确认

| Path | Category | Reason | Risk |
|------|----------|--------|------|
| `.agent/` | 配置目录 | Agent相关配置，用途需确认 | 中 |
| `.agents/` | 配置目录 | Agent相关配置，用途需确认 | 中 |
| `dropzone/` (整体) | 任务暂存区 | 任务暂存区，清理策略需确认 | 中 |

---

## 执行建议

### 高优先级（立即处理）- 安全与合规

1. **修复 .gitignore**
   ```
   # 添加以下内容
   .env
   .env.bak
   .env.local
   db/*.sqlite
   db/*.db
   trading_data/
   demo_*_data/
   .tmp/
   .pytest_cache/
   __pycache__/
   *.py[cod]
   dist/
   build/
   *.egg-info/
   logs/
   *.log
   ALL_TESTS_PASSED.flag
   GM-SkillForge.tmppytest/
   ```

2. **从Git中移除敏感文件**
   ```bash
   git rm --cached .env
   git rm --cached .env.bak
   git rm --cached db/skillforge.sqlite
   ```

3. **清理临时文件**
   - 删除 `.tmp/` 目录
   - 删除 `AuditPack/evidence/*.tmp` (19个文件)

### 中优先级（计划处理）

1. **处理嵌套仓库**
   - `export-seo/`: 转换为submodule或移出
   - `git-Claude仓库/`: 移出仓库或删除

2. **归档压缩包**
   - 移动 `lobster-p2a.tar.gz` 到独立归档位置
   - 移动 `skillforge_src.tar.gz` 到独立归档位置

3. **整理散落文件**
   - 将根目录脚本移动到 `scripts/dev/` 或删除
   - 将根目录报告移动到 `reports/` 或删除
   - 将HTML文件移动到适当位置或删除

### 低优先级（可选处理）

1. **历史数据归档**
   - 将大量历史证据和报告移到独立存储
   - 清理 `AuditPack/evidence/` 中的旧文件

2. **demo数据整理**
   - 移动或清理 `demo_*_data/` 目录

---

## 统计数据

```
总目录数: 48
根目录文件数: 40+
临时文件数: 数千个（.tmp目录）
TMP文件数: 19（AuditPack/evidence/）
嵌套仓库数: 2
敏感文件: 2（.env, .env.bak）
运行时数据库: 1（skillforge.sqlite）
```

---

## 免责声明

本报告仅供参考，执行任何删除操作前请：
1. 确保备份重要数据
2. 与团队确认文件用途
3. 在测试分支上验证操作
4. 遵循Antigravity-1闭链要求

---

**报告结束**
