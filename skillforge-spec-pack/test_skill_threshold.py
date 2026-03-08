#!/usr/bin/env python3
"""
test_skill_threshold.py - Tests for skill_thresholds.yml and fit_score gate integration

验收条件:
- test_thresholds_config_valid: skill_thresholds.yml 存在且 schema_version == 1
- test_low_fit_score_denied: fit_score < 40 → DENY
- test_medium_fit_score_requires_changes: 40 <= fit_score < 70 → REQUIRES_CHANGES
- test_high_fit_score_allowed: fit_score >= 70 → ALLOW
- test_fit_score_breakdown_in_output: 输出包含 fit_score_breakdown 字段
"""

import pytest
from pathlib import Path
from typing import Dict, Any, Tuple

# 尝试导入 yaml
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    pytest.skip("PyYAML not installed", allow_module_level=True)


# ── Test Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def base_path() -> Path:
    """获取项目根目录"""
    return Path(__file__).parent


@pytest.fixture
def thresholds_config(base_path: Path) -> Dict[str, Any]:
    """加载 skill_thresholds.yml 配置"""
    config_path = base_path / "orchestration" / "skill_thresholds.yml"
    if not config_path.exists():
        pytest.skip(f"Config file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture
def gate_engine_spec(base_path: Path) -> Dict[str, Any]:
    """加载 gate_engine.skill.yml 规格"""
    spec_path = base_path / "skillforge" / "specs" / "gate_engine.skill.yml"
    if not spec_path.exists():
        pytest.skip(f"Spec file not found: {spec_path}")

    with open(spec_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture
def repo_scan_spec(base_path: Path) -> Dict[str, Any]:
    """加载 repo_scan_fit_score.skill.yml 规格"""
    spec_path = base_path / "skillforge" / "specs" / "nodes" / "repo_scan_fit_score.skill.yml"
    if not spec_path.exists():
        pytest.skip(f"Spec file not found: {spec_path}")

    with open(spec_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# ── Helper Functions ───────────────────────────────────────────────────────────

def evaluate_fit_score_decision(fit_score: int, thresholds: Dict[str, Any]) -> Tuple[str, str]:
    """
    根据 fit_score 和阈值配置评估门禁决策

    Returns:
        Tuple[decision, reason]
    """
    threshold_config = thresholds.get("thresholds", {})
    minimum = threshold_config.get("minimum_fit_score", 40)
    review = threshold_config.get("review_fit_score", 70)

    if fit_score < minimum:
        return "DENY", f"fit_score {fit_score} below minimum {minimum}"
    elif fit_score < review:
        return "REQUIRES_CHANGES", f"fit_score {fit_score} needs review (threshold: {review})"
    else:
        return "ALLOW", f"fit_score {fit_score} meets auto-approve threshold"


def calculate_fit_score(breakdown: Dict[str, float], weights: Dict[str, float]) -> int:
    """
    根据评分明细和权重计算 fit_score

    Args:
        breakdown: 各项评分明细 (0-1 范围)
        weights: 各项权重 (总和为 1.0)

    Returns:
        fit_score (0-100 范围)
    """
    total = 0.0
    for key, weight in weights.items():
        score = breakdown.get(key, 0.0)
        total += score * weight * 100
    return int(total)


# ── Test Class ─────────────────────────────────────────────────────────────────

class TestSkillThresholds:
    """技能阈值测试套件"""

    def test_thresholds_config_valid(self, thresholds_config: Dict[str, Any]):
        """
        CHECK 11: skill_thresholds.yml 存在且 schema_version == 1
        """
        assert thresholds_config is not None, "Config should not be None"

        schema_version = thresholds_config.get("schema_version")
        assert schema_version in [1, "1"], f"schema_version should be 1, got {schema_version}"

    def test_threshold_values_logical(self, thresholds_config: Dict[str, Any]):
        """
        CHECK 12: thresholds.minimum_fit_score <= thresholds.review_fit_score
        """
        thresholds = thresholds_config.get("thresholds", {})

        minimum = thresholds.get("minimum_fit_score")
        review = thresholds.get("review_fit_score")

        assert minimum is not None, "minimum_fit_score should be defined"
        assert review is not None, "review_fit_score should be defined"
        assert minimum <= review, f"minimum({minimum}) should <= review({review})"

    def test_scoring_weights_sum_to_one(self, thresholds_config: Dict[str, Any]):
        """
        验证 scoring_weights 权重总和为 1.0
        """
        weights = thresholds_config.get("scoring_weights", {})

        total = sum(weights.values())
        assert 0.99 <= total <= 1.01, f"Weights should sum to 1.0, got {total}"

    def test_low_fit_score_denied(self, thresholds_config: Dict[str, Any]):
        """
        test_low_fit_score_denied: fit_score < minimum_fit_score → DENY
        """
        # 测试边界值
        low_scores = [0, 10, 20, 30, 39]

        for score in low_scores:
            decision, reason = evaluate_fit_score_decision(score, thresholds_config)
            assert decision == "DENY", f"Score {score} should be DENY, got {decision}"

    def test_medium_fit_score_requires_changes(self, thresholds_config: Dict[str, Any]):
        """
        test_medium_fit_score_requires_changes: minimum <= fit_score < review → REQUIRES_CHANGES
        """
        thresholds = thresholds_config.get("thresholds", {})
        minimum = thresholds.get("minimum_fit_score", 40)
        review = thresholds.get("review_fit_score", 70)

        # 测试中间范围
        medium_scores = [minimum, minimum + 10, 50, 60, review - 1]

        for score in medium_scores:
            decision, reason = evaluate_fit_score_decision(score, thresholds_config)
            assert decision == "REQUIRES_CHANGES", \
                f"Score {score} should be REQUIRES_CHANGES, got {decision}"

    def test_high_fit_score_allowed(self, thresholds_config: Dict[str, Any]):
        """
        test_high_fit_score_allowed: fit_score >= review_fit_score → ALLOW
        """
        thresholds = thresholds_config.get("thresholds", {})
        review = thresholds.get("review_fit_score", 70)

        # 测试高分范围
        high_scores = [review, review + 10, 80, 90, 100]

        for score in high_scores:
            decision, reason = evaluate_fit_score_decision(score, thresholds_config)
            assert decision == "ALLOW", f"Score {score} should be ALLOW, got {decision}"

    def test_fit_score_breakdown_in_output(self, repo_scan_spec: Dict[str, Any]):
        """
        test_fit_score_breakdown_in_output: 输出包含 fit_score_breakdown 字段
        """
        output = repo_scan_spec.get("output", {})
        required = output.get("required", [])

        # required 是一个列表，每个元素是单键字典
        required_keys = set()
        for item in required:
            if isinstance(item, dict):
                required_keys.update(item.keys())

        # 检查 fit_score_breakdown 字段存在
        assert "fit_score_breakdown" in required_keys, \
            f"fit_score_breakdown should be in output.required, got keys: {required_keys}"

        # 检查 threshold_decision 字段存在
        assert "threshold_decision" in required_keys, \
            f"threshold_decision should be in output.required, got keys: {required_keys}"

    def test_gate_engine_has_fit_score_rules(self, gate_engine_spec: Dict[str, Any]):
        """
        验证 gate_engine.skill.yml 包含 fit_score_rules
        """
        eval_rules = gate_engine_spec.get("evaluation_rules", {})
        constitution_gate = eval_rules.get("constitution_risk_gate", {})

        # 检查 fit_score_rules 存在
        assert "fit_score_rules" in constitution_gate, \
            "constitution_risk_gate should have fit_score_rules"

        # 检查 thresholds_config 引用
        assert "thresholds_config" in constitution_gate, \
            "constitution_risk_gate should reference thresholds_config"

    def test_quality_level_requirements_defined(self, thresholds_config: Dict[str, Any]):
        """
        验证各质量等级的 fit_score 要求已定义
        """
        qg_requirements = thresholds_config.get("quality_level_requirements", {})

        expected_levels = ["L1", "L2", "L3", "L4", "L5"]
        for level in expected_levels:
            assert level in qg_requirements, f"Level {level} should be defined"
            assert "min_fit_score" in qg_requirements[level], \
                f"Level {level} should have min_fit_score"

    def test_quality_level_fit_scores_ascending(self, thresholds_config: Dict[str, Any]):
        """
        验证质量等级的 fit_score 要求是递增的
        """
        qg_requirements = thresholds_config.get("quality_level_requirements", {})

        prev_score = 0
        for level in ["L1", "L2", "L3", "L4", "L5"]:
            if level in qg_requirements:
                score = qg_requirements[level].get("min_fit_score", 0)
                assert score >= prev_score, \
                    f"Level {level} min_fit_score({score}) should >= previous({prev_score})"
                prev_score = score

    def test_fit_score_calculation_with_weights(self, thresholds_config: Dict[str, Any]):
        """
        测试使用权重计算 fit_score
        """
        weights = thresholds_config.get("scoring_weights", {})

        # 完美评分
        perfect_breakdown = {
            "has_readme": 1.0,
            "has_license": 1.0,
            "has_tests": 1.0,
            "has_requirements": 1.0,
            "code_quality_lint": 1.0,
            "single_purpose": 1.0,
            "documentation_ratio": 1.0,
        }
        score = calculate_fit_score(perfect_breakdown, weights)
        assert score == 100, f"Perfect breakdown should yield 100, got {score}"

        # 零评分
        zero_breakdown = {k: 0.0 for k in weights}
        score = calculate_fit_score(zero_breakdown, weights)
        assert score == 0, f"Zero breakdown should yield 0, got {score}"

        # 部分评分
        partial_breakdown = {
            "has_readme": 1.0,
            "has_license": 1.0,
            "has_tests": 0.5,
            "has_requirements": 0.0,
            "code_quality_lint": 0.8,
            "single_purpose": 0.5,
            "documentation_ratio": 0.3,
        }
        score = calculate_fit_score(partial_breakdown, weights)
        assert 0 <= score <= 100, f"Score should be in [0, 100], got {score}"


class TestThresholdIntegration:
    """阈值集成测试"""

    def test_repo_scan_spec_version_updated(self, repo_scan_spec: Dict[str, Any]):
        """
        验证 repo_scan_fit_score.skill.yml 版本已更新
        """
        version = repo_scan_spec.get("schema_version")
        assert version in ["0.2.0", "0.2"], \
            f"schema_version should be 0.2.0, got {version}"

    def test_gate_engine_error_codes_include_fit_score(self, gate_engine_spec: Dict[str, Any]):
        """
        验证 gate_engine 错误码包含 fit_score 相关错误
        """
        errors = gate_engine_spec.get("errors", [])
        error_codes = [e.get("code") for e in errors]

        assert "GATE_FIT_SCORE_DENIED" in error_codes, \
            "GATE_FIT_SCORE_DENIED error code should exist"
        assert "GATE_FIT_SCORE_REVIEW" in error_codes, \
            "GATE_FIT_SCORE_REVIEW error code should exist"


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
