# L4.5 CI 强制门接入报告

> **Job ID**: L45-D6-SEEDS-P2-20260220-006
> **Skill ID**: l45_seeds_p2_operationalization
> **Task**: T28
> **Executor**: vs--cc3
> **Date**: 2026-02-20
> **Status**: ✅ COMPLETED

---

## 1. 任务概述

将 P0/P1 seed 校验接入 CI（pre-merge 与 nightly），确保每次代码合并前和每日构建时都验证种子基础设施完整性。

### 1.1 核心目标

1. **Strict 模式**：失败即阻断，不得跳过
2. **Pre-merge 执行**：PR 合并前自动校验
3. **Nightly 执行**：每日凌晨 2:00 UTC 自动校验
4. **可审计**：校验结果保存为 artifact

---

## 2. 交付物清单

| # | 文件 | 类型 | 状态 |
|---|------|------|------|
| 1 | `.github/workflows/seeds-governance.yml` | 新建 | ✅ |
| 2 | `scripts/validate_seeds_p0_p1.py` | 新建 | ✅ |
| 3 | `docs/2026-02-20/L45_P2_CI_GOVERNANCE_REPORT_v1.md` | 新建 | ✅ |

---

## 3. 实现细节

### 3.1 验证脚本 `validate_seeds_p0_p1.py`

**功能**：
- 验证 P0 seed 文件存在性和格式（5 个文件）
- 验证 P1 seed 文件存在性和格式（5 个文件）
- 运行相关测试套件（6 个测试文件）
- 支持 `--strict` 模式（失败即退出码 1）
- 支持 `--json` 输出格式

**P0 Seeds 检查**：
| Seed | 文件 | 说明 |
|------|------|------|
| registry | `registry/skills.jsonl` | Append-only skill registry |
| ruleset_manifest | `orchestration/ruleset_manifest.yml` | Ruleset version manifest |
| audit_events | `logs/audit_events.jsonl` | Append-only audit events log |
| usage | `logs/usage.jsonl` | Usage/quota log |
| permit_policy | `security/permit_policy.yml` | Permit required policy |

**P1 Seeds 检查**：
| Seed | 文件 | 说明 |
|------|------|------|
| regression | `regression/README.md` | Regression set documentation |
| regression_case_001 | `regression/cases/case_001/input.json` | Regression case 001 input |
| i18n_keys | `ui/contracts/i18n_keys.yml` | UI i18n keys contract |
| feature_flags | `orchestration/feature_flags.yml` | Feature flags configuration |
| provenance | `templates/provenance.json` | Provenance template |

**Test Suites 检查**：
| Suite | 文件 | 必需 |
|-------|------|------|
| registry_store | `test_registry_store.py` | ✅ |
| ruleset_revision | `test_ruleset_revision_binding.py` | ✅ |
| audit_events | `test_audit_event_writer.py` | ✅ |
| usage_meter | `test_usage_meter.py` | ✅ |
| permit_required | `test_permit_required_policy.py` | ✅ |
| regression_smoke | `test_regression_seed_smoke.py` | ✅ |

### 3.2 GitHub Workflow `seeds-governance.yml`

**触发条件**：
1. **Pull Request**：PR 到 main 分支且修改了相关路径
2. **Scheduled**：每日凌晨 2:00 UTC
3. **Manual**：手动触发（可选 strict 参数）

**Workflow 步骤**：
1. Checkout repository
2. Set up Python 3.11
3. Install dependencies (pytest, pyyaml, jsonschema)
4. Create required directories
5. Run `validate_seeds_p0_p1.py --strict --json`
6. Upload validation result as artifact
7. Comment on PR with result summary

**路径过滤**（PR 触发）：
```yaml
paths:
  - 'skillforge/**'
  - 'registry/**'
  - 'logs/**'
  - 'orchestration/**'
  - 'security/**'
  - 'regression/**'
  - 'ui/**'
  - 'templates/**'
  - 'scripts/validate_seeds_p0_p1.py'
```

---

## 4. Gate 自动检查结果

```bash
python scripts/validate_seeds_p0_p1.py --strict
# === SEEDS P0/P1 Validator ===
# --- P0 Seeds ---
#   ✅ registry: file exists (1 lines)
#   ✅ ruleset_manifest: file exists
#   ✅ audit_events: file exists (1 lines)
#   ✅ usage: file exists (1 lines)
#   ✅ permit_policy: file exists
# --- P1 Seeds ---
#   ✅ regression: file exists
#   ✅ regression_case_001: file exists
#   ✅ i18n_keys: file exists
#   ✅ feature_flags: file exists
#   ✅ provenance: file exists
# --- Test Suites ---
#   ✅ registry_store: 10 passed
#   ✅ ruleset_revision: 23 passed
#   ✅ audit_events: 21 passed
#   ✅ usage_meter: 16 passed
#   ✅ permit_required: 28 passed
#   ✅ regression_smoke: 8 passed
# === Summary ===
# Total: 16
# Passed: 16
# Failed: 0
# Overall: PASS
# ✅ Validation PASSED
```

---

## 5. 约束验证

| 约束 | 状态 | 说明 |
|------|------|------|
| strict 模式失败即阻断 | ✅ | 任何检查失败返回 exit code 1 |
| pre-merge 可执行 | ✅ | PR 触发 workflow |
| nightly 可执行 | ✅ | 每日 2:00 UTC 触发 |
| 校验结果可审计 | ✅ | 上传为 artifact，保留 30 天 |

---

## 6. 禁止项验证

| 禁止项 | 状态 |
|--------|------|
| 不得跳过 strict 失败 | ✅ | workflow 在 strict 模式下失败会阻断 |

---

## 7. 使用说明

### 7.1 本地运行

```bash
# Strict 模式（推荐）
python scripts/validate_seeds_p0_p1.py --strict

# JSON 输出
python scripts/validate_seeds_p0_p1.py --strict --json

# 指定路径
python scripts/validate_seeds_p0_p1.py --strict --base-path /path/to/project
```

### 7.2 CI 运行

- **Pre-merge**: 创建 PR 后自动运行
- **Nightly**: 每日凌晨 2:00 UTC 自动运行
- **Manual**: GitHub Actions 页面手动触发

---

## 8. 常量标识

```yaml
job_id: "L45-D6-SEEDS-P2-20260220-006"
skill_id: "l45_seeds_p2_operationalization"
workflow_file: ".github/workflows/seeds-governance.yml"
validator_script: "scripts/validate_seeds_p0_p1.py"
```

---

## 9. 后续依赖

本任务 (T28) 完成后，下游任务 T33 (Kior-C) 可在所有 Wave 1 任务完成后启动。

---

> **Gate Decision**: ✅ ALLOW
> **Reviewer**: Automated
> **Timestamp**: 2026-02-20
