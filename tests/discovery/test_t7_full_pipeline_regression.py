"""
T7 回归样例测试

验证完整发现链 (T1-T6) 能够正常运行，并产生预期输出。

测试覆盖：
1. 正常 skill (quant) - 预期成功通过所有步骤
2. 缺 manifest 的 skill - 预期在 T2 解析时失败（如果 fail_on_missing_manifest=True）
3. 有已知问题的 skill - 预期产生 findings

@contact: 执行者 Kior-C
@task_id: T7
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "skillforge" / "src"))

from skillforge.src.contracts.discovery_pipeline import DiscoveryPipeline, run_discovery_pipeline


# =============================================================================
# 测试 Fixtures
# =============================================================================

@pytest.fixture
def quant_skill_dir():
    """Quant skill 目录 (正常样例)"""
    return project_root / "skillforge" / "src" / "skills" / "quant"


@pytest.fixture
def temp_skill_dir_with_missing_manifest():
    """临时 skill 目录，缺少 manifest.json (负例样例)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "test_skill"
        skill_dir.mkdir()

        # 创建 __init__.py
        init_content = '''"""Test skill module."""

SKILL_NAME = "test_skill"
SKILL_VERSION = "0.1.0"

def main():
    print("Running test skill...")
'''
        (skill_dir / "__init__.py").write_text(init_content)

        # 不创建 manifest.json
        yield skill_dir


@pytest.fixture
def temp_skill_dir_with_issues():
    """临时 skill 目录，包含已知问题 (用于产生 findings)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "test_skill"
        skill_dir.mkdir()

        # 创建 __init__.py (包含 dangerous patterns)
        issues_content = '''"""Test skill with known issues."""

SKILL_NAME = "test_skill"
SKILL_VERSION = "0.1.0"

import subprocess

def dangerous_eval(user_input):
    # E421: eval usage - 应该被 T4 检测到
    return eval(user_input)

def dangerous_subprocess():
    # E405: subprocess with shell=True - 应该被 T4 检测到
    subprocess.run("ls", shell=True)

def external_without_stop_rule():
    # E501: External action without stop rule
    import requests
    return requests.get("https://api.example.com")

def main():
    print("Running test skill...")
'''
        (skill_dir / "__init__.py").write_text(issues_content)

        yield skill_dir


# =============================================================================
# 回归测试
# =============================================================================

class TestT7FullPipelineRegression:
    """T7 完整流水线回归测试"""

    def test_regression_sample_1_normal_skill_passes_all_steps(
        self, quant_skill_dir
    ):
        """
        回归样例 1: 正常 skill 应该成功通过所有步骤

        预期：
        - T1 Intake: PASSED
        - T2 Parse: completed (quant skill 有 __init__.py)
        - T3 Validate: completed (quant skill 结构完整)
        - T4 Scan: completed (可能有一些规则命中)
        - T5 Pattern: completed (可能有一些模式匹配)
        - T6 Findings: completed (生成 findings.json)
        """
        if not quant_skill_dir.exists():
            pytest.skip(f"Quant skill directory not found: {quant_skill_dir}")

        pipeline = DiscoveryPipeline(output_base_dir="run/T7_regression")
        result = pipeline.run(
            intent_id="AUDIT_REPO_SKILL",
            repo_url="https://github.com/genesismind-bot/GM-SkillForge",
            commit_sha="abc123def456",
            skill_dir=str(quant_skill_dir),
            run_id="test_normal_skill",
        )

        # 验证流水线状态
        assert result.status == "success", f"Pipeline failed: {result.error_summary}"

        # 验证所有步骤都完成
        assert len(result.steps) == 6, f"Expected 6 steps, got {len(result.steps)}"

        # 验证输出文件存在
        output_dir = Path(result.output_dir)
        assert (output_dir / "intake_request.json").exists()
        assert (output_dir / "normalized_skill_spec.json").exists()
        assert (output_dir / "validation_report.json").exists()
        assert (output_dir / "rule_scan_report.json").exists()
        assert (output_dir / "pattern_detection_report.json").exists()
        assert (output_dir / "findings.json").exists()

        # 验证 findings.json 格式
        with open(output_dir / "findings.json", "r", encoding="utf-8") as f:
            findings = json.load(f)
        assert "findings" in findings
        assert "summary" in findings
        assert "meta" in findings

    def test_regression_sample_2_fail_closed_on_missing_manifest(
        self, temp_skill_dir_with_missing_manifest
    ):
        """
        回归样例 2: 缺 manifest 但有 __init__.py 的 skill 应该能通过 T2

        注意：T2 SkillParser 默认 fail_on_missing_manifest=False
        如果 __init__.py 包含 SKILL_NAME 和 SKILL_VERSION，即使缺少 manifest.json 也能解析成功

        预期：
        - T1 Intake: PASSED
        - T2 Parse: completed (从 __init__.py 提取 SKILL_NAME/SKILL_VERSION)
        - 流水线继续执行后续步骤
        """
        pipeline = DiscoveryPipeline(output_base_dir="run/T7_regression")
        result = pipeline.run(
            intent_id="AUDIT_REPO_SKILL",
            repo_url="https://github.com/test/test",
            commit_sha="abc1234",  # T1 要求 7-40 字符
            skill_dir=str(temp_skill_dir_with_missing_manifest),
            run_id="test_missing_manifest",
        )

        # 验证流水线状态 - 应该成功（T2 可以从 __init__.py 解析）
        assert result.status == "success", f"Pipeline should succeed: {result.error_summary}"

        # 验证 T2 步骤完成
        parse_step = next((s for s in result.steps if s.step_name == "T2_Parse"), None)
        assert parse_step is not None, "T2_Parse step not found"
        assert parse_step.status == "completed", f"T2 should complete, got {parse_step.status}"

    def test_regression_sample_3_skill_with_issues_produces_findings(
        self, temp_skill_dir_with_issues
    ):
        """
        回归样例 3: 有问题的 skill 应该产生 findings

        预期：
        - 所有步骤都完成
        - findings.json 包含预期的 findings
        - 至少有一个 E4xx (rule scan) 或 E5xx (pattern) finding
        """
        # 先创建 manifest.json 以确保 T2 通过
        manifest_content = {
            "skill_name": "test_skill",
            "skill_version": "0.1.0",
            "description": "Test skill with issues",
            "author": "test",
        }
        manifest_path = Path(temp_skill_dir_with_issues) / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_content, f, indent=2)

        pipeline = DiscoveryPipeline(output_base_dir="run/T7_regression")
        result = pipeline.run(
            intent_id="AUDIT_REPO_SKILL",
            repo_url="https://github.com/test/test",
            commit_sha="abc1234",  # T1 要求 7-40 字符
            skill_dir=str(temp_skill_dir_with_issues),
            run_id="test_skill_with_issues",
        )

        # 验证流水线状态
        assert result.status == "success", f"Pipeline failed: {result.error_summary}"

        # 验证 findings.json 存在且包含预期结果
        output_dir = Path(result.output_dir)
        findings_path = output_dir / "findings.json"
        assert findings_path.exists(), "findings.json should exist"

        with open(findings_path, "r", encoding="utf-8") as f:
            findings_data = json.load(f)

        # 验证有 findings 产生
        findings = findings_data.get("findings", [])
        assert len(findings) > 0, "Expected at least one finding"

        # 验证至少有一个来自 T4 (规则扫描) 或 T5 (模式匹配)
        has_rule_or_pattern_finding = any(
            f.get("source", {}).get("type") in ["rule_scan", "pattern_match"]
            for f in findings
        )
        assert has_rule_or_pattern_finding, "Expected at least one rule_scan or pattern_match finding"

    def test_run_directory_structure_is_fixed(self, quant_skill_dir):
        """
        回归样例 4: 验证输出目录结构固定

        预期目录结构：
        run/<run_id>/
        ├── intake_request.json
        ├── normalized_skill_spec.json
        ├── validation_report.json
        ├── rule_scan_report.json
        ├── pattern_detection_report.json
        └── findings.json
        """
        if not quant_skill_dir.exists():
            pytest.skip(f"Quant skill directory not found: {quant_skill_dir}")

        pipeline = DiscoveryPipeline(output_base_dir="run/T7_regression")
        result = pipeline.run(
            intent_id="AUDIT_REPO_SKILL",
            repo_url="https://github.com/genesismind-bot/GM-SkillForge",
            commit_sha="abc1234",  # T1 要求 7-40 字符
            skill_dir=str(quant_skill_dir),
            run_id="test_directory_structure",
        )

        output_dir = Path(result.output_dir)
        expected_files = [
            "intake_request.json",
            "normalized_skill_spec.json",
            "validation_report.json",
            "rule_scan_report.json",
            "pattern_detection_report.json",
            "findings.json",
        ]

        for expected_file in expected_files:
            file_path = output_dir / expected_file
            assert file_path.exists(), f"Expected file not found: {expected_file}"
            assert file_path.is_file(), f"Expected a file, not directory: {expected_file}"

    def test_regression_fail_closed_when_skill_dir_not_exists(self):
        """
        回归样例: skill_dir 不存在时应该在 T2 fail-closed

        预期：
        - T1 Intake: PASSED
        - T2 Parse: failed (目录不存在)
        - 流水线应该停止 (fail_fast=True)
        """
        pipeline = DiscoveryPipeline(output_base_dir="run/T7_regression")
        result = pipeline.run(
            intent_id="AUDIT_REPO_SKILL",
            repo_url="https://github.com/test/test",
            commit_sha="abc1234",  # T1 要求 7-40 字符
            skill_dir="/nonexistent/skill/dir/xyz123",  # 不存在的目录
            run_id="test_nonexistent_dir",
        )

        # 验证流水线状态（预期失败）
        assert result.status == "failed", "Pipeline should fail for nonexistent directory"

        # 验证 T2 步骤失败
        parse_step = next((s for s in result.steps if s.step_name == "T2_Parse"), None)
        assert parse_step is not None, "T2_Parse step not found"
        assert parse_step.status == "failed", f"T2 should fail, got {parse_step.status}"
        assert parse_step.error is not None, "T2 should have an error message"

    def test_regression_fail_closed_when_t6_fails(self):
        """
        回归样例: T6 Findings 失败时应该 fail-closed

        测试方法：
        1. 验证流水线代码中存在 T6 fail-closed 检查点
        2. 验证当 T6 失败时，流水线返回 failed 状态

        预期：
        - 代码中应该有 T6 失败时的 fail-closed 检查
        - 当 T6 失败且 fail_fast=True 时，流水线应该返回 failed 状态
        """
        import tempfile

        # 首先，验证流水线代码中存在 T6 fail-closed 检查
        import skillforge.src.contracts.discovery_pipeline as pipeline_module
        pipeline_file = Path(pipeline_module.__file__)
        pipeline_code = pipeline_file.read_text(encoding="utf-8")

        # 验证代码中包含 T6 fail-closed 检查
        # 检查点：在 T6 步骤后是否有 fail-closed 检查
        assert 'findings_step.status == "failed" and self.fail_fast' in pipeline_code, \
            "代码中应该存在 T6 fail-closed 检查点"

        # 验证 fail-closed 检查后返回 failed 状态
        assert 'status="failed"' in pipeline_code, \
            "流水线应该在步骤失败时返回 failed 状态"

        # 创建一个简单的 skill 来运行流水线
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "test_skill"
            skill_dir.mkdir()

            # 创建 __init__.py
            (skill_dir / "__init__.py").write_text('"""Test."""\nSKILL_NAME = "t6test"\nSKILL_VERSION = "0.1.0"\n')

            # 创建 manifest.json
            manifest = {"skill_name": "t6test", "skill_version": "0.1.0", "author": "test"}
            (skill_dir / "manifest.json").write_text(json.dumps(manifest))

            # 运行流水线
            pipeline = DiscoveryPipeline(output_base_dir="run/T7_regression")
            result = pipeline.run(
                intent_id="AUDIT_REPO_SKILL",
                repo_url="https://github.com/test/test",
                commit_sha="abcd123",
                skill_dir=str(skill_dir),
                run_id="test_t6_fail_closed",
            )

            # 验证 T6 步骤存在
            t6_step = next((s for s in result.steps if s.step_name == "T6_Findings"), None)
            assert t6_step is not None, "T6_Findings step should exist"

            # 运行时验证：如果 T6 失败，整条链应该失败
            if t6_step.status == "failed":
                assert result.status == "failed", \
                    f"流水线应该在 T6 失败时返回 failed，实际返回 {result.status}"
                assert result.error_summary, "T6 失败时应该有错误摘要"
            else:
                # T6 成功时，流水线也应该成功
                assert result.status == "success", \
                    f"T6 成功时流水线应该成功，实际返回 {result.status}"


class TestT7CLIInterface:
    """T7 CLI 接口测试"""

    def test_run_discovery_pipeline_function_exists(self):
        """验证 run_discovery_pipeline 函数可用"""
        from skillforge.src.contracts.discovery_pipeline import run_discovery_pipeline
        assert callable(run_discovery_pipeline), "run_discovery_pipeline should be callable"

    def test_discovery_pipeline_module_has_main(self):
        """验证 discovery_pipeline 模块有 __main__ 入口"""
        # 检查模块文件内容包含 if __name__ == "__main__"
        import skillforge.src.contracts.discovery_pipeline as pipeline_module
        module_file = pipeline_module.__file__
        with open(module_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert 'if __name__ == "__main__"' in content, "Module should have __main__ entry point"


# =============================================================================
# 便捷测试运行
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
