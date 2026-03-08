# T-V0-B: Skill 识别阈值外部化 — fit_score → YAML + Gate 联动

## 背景
`repo_scan.py` 有 `fit_score` 骨架但阈值硬编码在代码中。v0 需要：
- 阈值从代码提取到 YAML 配置
- `constitution_risk_gate` 根据 fit_score 做 ALLOW/DENY/REQUIRES_CHANGES 决策
- `quality_gate_levels.yml` 的 L1-L3 级别与 fit_score 阈值联动

## 任务清单

### B1: 创建 skill_thresholds.yml
**新文件**: `orchestration/skill_thresholds.yml`

```yaml
schema_version: 1

# fit_score 是 repo_scan 计算的"该仓库适合做 Skill"的综合分数 [0.0, 1.0]
thresholds:
  minimum_fit_score: 0.4       # < 0.4 → DENY（不适合做 Skill）
  review_fit_score: 0.7        # 0.4-0.7 → REQUIRES_CHANGES（需人工审查）
  auto_approve_fit_score: 0.7  # >= 0.7 → ALLOW（自动通过）

# 各质量等级对 fit_score 的要求
quality_level_requirements:
  L1: { min_fit_score: 0.3 }
  L2: { min_fit_score: 0.5 }
  L3: { min_fit_score: 0.6 }

# fit_score 计算权重（repo_scan 使用）
scoring_weights:
  has_readme: 0.15
  has_license: 0.15
  has_tests: 0.20
  has_requirements: 0.10
  code_quality_lint: 0.15
  single_purpose: 0.15
  documentation_ratio: 0.10
```

### B2: repo_scan.py — 读取外部阈值
**文件**: `skillforge/src/nodes/repo_scan.py`

1. `execute()` 中读取 `orchestration/skill_thresholds.yml`
2. 根据 `scoring_weights` 计算 `fit_score`（当前是硬编码，改为权重求和）
3. 输出增加 `fit_score_breakdown` 字段（每项评分的明细）

### B3: gate_engine.py — fit_score 门禁联动
**文件**: `skillforge/src/orchestration/gate_engine.py`

在 `_evaluate_constitution_gate()` 中增加 fit_score 检查：

```python
# 从 artifacts 中获取 repo_scan 的 fit_score
repo_scan = artifacts.get("repo_scan_fit_score", {})
fit_score = repo_scan.get("fit_score", 0.0)

# 读取阈值配置
thresholds = self._load_thresholds()  # 从 skill_thresholds.yml

if fit_score < thresholds["minimum_fit_score"]:
    return DENY(f"fit_score {fit_score} below minimum {thresholds['minimum_fit_score']}")
elif fit_score < thresholds["review_fit_score"]:
    return REQUIRES_CHANGES(f"fit_score {fit_score} needs review (threshold: {thresholds['review_fit_score']})")
else:
    # 继续其他检查...
```

### B4: validate.py — 扩展校验
**文件**: `tools/validate.py`

在 `validate_audit_config()` 中增加 2 个检查点：
- CHECK 11: `skill_thresholds.yml` 存在且 `schema_version == 1`
- CHECK 12: `thresholds.minimum_fit_score <= thresholds.review_fit_score`

### B5: 测试
**新文件**: `skillforge/tests/test_skill_threshold.py`

```python
class TestSkillThresholds:
    def test_thresholds_config_valid(self): ...
    def test_low_fit_score_denied(self): ...
    def test_medium_fit_score_requires_changes(self): ...
    def test_high_fit_score_allowed(self): ...
    def test_fit_score_breakdown_in_output(self): ...
```

## 验收条件
- `python -m pytest skillforge/tests/test_skill_threshold.py -v` 全过
- `python -m pytest skillforge/tests/test_acceptance.py -v` 不回归
- `python tools/validate.py --audit-config` 不回归（允许新增检查点）

## 关键文件清单
```
orchestration/skill_thresholds.yml              ← 新建
skillforge/src/nodes/repo_scan.py               ← 修改
skillforge/src/orchestration/gate_engine.py     ← 修改
tools/validate.py                               ← 修改
skillforge/tests/test_skill_threshold.py        ← 新建
orchestration/protocol_v0_scope.yml             ← 只读参考
```
