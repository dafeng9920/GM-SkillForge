# ci-skill-validation-skill

> 版本: v1.0.0
> 冻结时间: 2026-02-19
> 继承自: Phase-1 Skill 化门禁

---

## 概述

CI Skill 验证 Skill - 用于自动验证其他 Skill 包的结构、契约和语义一致性。

### 核心能力

| 能力 | 说明 |
|------|------|
| 结构检查 | 验证目录和必备文件 |
| 契约检查 | 验证关键治理语义标记 |
| YAML 检查 | 验证 agents/openai.yaml 有效性 |
| 证据检查 | 验证证据引用路径存在 |
| 语义检查 | 验证错误码语义一致性 |

### 核心约束

```yaml
fail_closed: true
evidence_first: true
blocking: true
```

---

## 触发条件

- Skill 包变更（skills/ 目录）
- CI 配置变更（ci/ 目录）
- PR 合并前
- 手动触发验收

---

## 输入契约

```yaml
input:
  skills_dir: string        # Skill 目录路径（默认: skills/）
  output_dir: string        # 报告输出目录（默认: ci/out/）
  checks: array             # 要执行的检查列表
    - structure             # 结构检查
    - openai_yaml           # YAML 配置检查
    - contract_markers      # 契约标记检查
    - evidence_refs         # 证据引用检查
    - error_semantics       # 错误语义检查
  fail_fast: bool           # 首次失败即退出（默认: false）
```

---

## 输出契约

```yaml
output:
  gate_result: string       # PASS / FAIL
  total_checks: int         # 总检查数
  passed_checks: int        # 通过检查数
  failed_checks: int        # 失败检查数
  duration_ms: int          # 执行耗时
  report_path: string       # 报告路径
  checks:
    - name: string
      passed: bool
      duration_ms: int
      error: string | null
```

---

## Fail-Closed 条件

| 条件 | 行为 |
|------|------|
| 任一 required 检查失败 | gate_result = FAIL, exit_code = 1 |
| Skill 目录不存在 | gate_result = FAIL |
| 报告生成失败 | gate_result = FAIL |

---

## 检查项详情

### 1. 结构检查 (structure)

检查项：
- `SKILL.md` 存在
- `agents/openai.yaml` 存在
- `references/` 目录（可选）
- 被引用文件存在

### 2. YAML 配置检查 (openai_yaml)

检查项：
- `name` 字段非空
- `description` 字段存在
- `version` 字段存在
- `frozen_at` 字段（推荐）

### 3. 契约标记检查 (contract_markers)

检查项（按 Skill 类型）：
- permit-governance: `no-permit-no-release`, `fail_closed`, `E001`, `E003`
- release-gate: `release_allowed`, `all-or-nothing`, `E001`, `E003`
- rollback-tombstone: `tombstone_*`, `immutable`, `replay_consistency`

### 4. 证据引用检查 (evidence_refs)

检查项：
- SKILL.md 引用路径存在
- references/ 文件中引用路径存在
- 至少有一个有效证据引用

### 5. 错误语义检查 (error_semantics)

检查项：
- E001 语义一致（PERMIT_REQUIRED）
- E003 语义一致（PERMIT_INVALID_SIGNATURE）
- `release_allowed` 口径一致

---

## Evidence 字段要求

```yaml
evidence:
  gate_name: string         # skillization_gate
  timestamp: string         # ISO8601
  passed: bool
  check_results: array      # 各检查结果
  skills_checked: int
  skills_passed: int
```

---

## 执行脚本

| 脚本 | 用途 |
|------|------|
| `scripts/check_skill_structure.ps1` | 结构检查 |
| `scripts/check_openai_yaml.ps1` | YAML 配置检查 |
| `scripts/check_skill_contract_markers.ps1` | 契约标记检查 |
| `scripts/check_evidence_refs.ps1` | 证据引用检查 |
| `scripts/check_error_sem_consistency.ps1` | 错误语义检查 |
| `scripts/run_skillization_gate.ps1` | 总控入口 |

---

## 验证步骤

```powershell
# 1. 执行所有检查
pwsh -File scripts/run_skillization_gate.ps1 -RepoRoot "D:\GM-SkillForge"

# 2. 检查报告
cat ci/out/skillization_gate_report.json

# 3. 验证退出码
echo $?  # 0 = PASS, 1 = FAIL
```

---

## CI 集成

**GitHub Actions**:
```yaml
skillization-gate:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Run Skillization Gate
      run: pwsh -File skills/ci-skill-validation-skill/scripts/run_skillization_gate.ps1
```

---

## 验收标准

- [x] 5 项检查脚本存在
- [x] 总控脚本可执行
- [x] JSON 报告生成
- [x] FAIL 时非零退出码
- [x] CI 集成配置

---

## 实现引用

- **CI 配置**: `.github/workflows/ci.yml`
- **脚本目录**: `ci/` (镜像)
- **总控报告**: `docs/2026-02-18/skillization_master_control_report_v1.md`

---

*版本: v1.0.0 | 冻结时间: 2026-02-19*
