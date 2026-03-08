#!/usr/bin/env python3
"""
SEEDS P0/P1 Validator - CI 强制门校验脚本

T28: 将 P0/P1 seed 校验接入 pre-merge 与 nightly

功能：
1. 验证 P0 seed 文件存在性和格式
2. 验证 P1 seed 文件存在性和格式
3. 运行相关测试确保功能可用
4. strict 模式下失败即阻断

Usage:
    python scripts/validate_seeds_p0_p1.py [--strict] [--json]

Exit codes:
    0: All checks passed
    1: One or more checks failed (strict mode)
    2: Validation error

Contract: docs/SEEDS_v0.md
Job ID: L45-D6-SEEDS-P2-20260220-006

NOTE: 若未配置 PYTEST_ADDOPTS 可能触发 Windows temp 权限问题
      建议执行: setx PYTEST_ADDOPTS "--basetemp D:\\GM-SkillForge\\.tmp\\pytest"
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any


# ============================================================================
# Pytest Temp Directory Check (强制防呆)
# ============================================================================

def check_pytest_temp_config() -> bool:
    """
    检查 PYTEST_ADDOPTS 是否已配置。

    Returns:
        True if configured, False otherwise
    """
    pytest_addopts = os.environ.get("PYTEST_ADDOPTS", "")
    if not pytest_addopts:
        print("=" * 70)
        print("WARNING: PYTEST_ADDOPTS 环境变量未配置")
        print("-" * 70)
        print("Windows 本地建议执行:")
        print('  setx PYTEST_ADDOPTS "--basetemp D:\\GM-SkillForge\\.tmp\\pytest"')
        print("")
        print("CI 环境建议在 workflow 中注入环境变量，不要写死在命令里")
        print("=" * 70)
        return False
    return True


# ============================================================================
# Constants
# ============================================================================

JOB_ID = "L45-D6-SEEDS-P2-20260220-006"
SKILL_ID = "l45_seeds_p2_operationalization"

# P0 Seeds (must exist)
P0_SEEDS = {
    "registry": {
        "path": "registry/skills.jsonl",
        "type": "file",
        "description": "Append-only skill registry",
    },
    "ruleset_manifest": {
        "path": "orchestration/ruleset_manifest.yml",
        "type": "file",
        "description": "Ruleset version manifest",
    },
    "audit_events": {
        "path": "logs/audit_events.jsonl",
        "type": "file",
        "description": "Append-only audit events log",
    },
    "usage": {
        "path": "logs/usage.jsonl",
        "type": "file",
        "description": "Usage/quota log",
    },
    "permit_policy": {
        "path": "security/permit_policy.yml",
        "type": "file",
        "description": "Permit required policy",
    },
}

# P1 Seeds (must exist)
P1_SEEDS = {
    "regression": {
        "path": "regression/README.md",
        "type": "file",
        "description": "Regression set documentation",
    },
    "regression_case_001": {
        "path": "regression/cases/case_001/input.json",
        "type": "file",
        "description": "Regression case 001 input",
    },
    "i18n_keys": {
        "path": "ui/contracts/i18n_keys.yml",
        "type": "file",
        "description": "UI i18n keys contract",
    },
    "feature_flags": {
        "path": "orchestration/feature_flags.yml",
        "type": "file",
        "description": "Feature flags configuration",
    },
    "provenance": {
        "path": "templates/provenance.json",
        "type": "file",
        "description": "Provenance template",
    },
}

# Tests to run
TEST_SUITES = {
    "registry_store": {
        "path": "skillforge/tests/test_registry_store.py",
        "description": "Registry store tests",
        "required": True,
    },
    "ruleset_revision": {
        "path": "skillforge/tests/test_ruleset_revision_binding.py",
        "description": "Ruleset revision tests",
        "required": True,
    },
    "audit_events": {
        "path": "skillforge/tests/test_audit_event_writer.py",
        "description": "Audit event writer tests",
        "required": True,
    },
    "usage_meter": {
        "path": "skillforge/tests/test_usage_meter.py",
        "description": "Usage meter tests",
        "required": True,
    },
    "permit_required": {
        "path": "skillforge/tests/test_permit_required_policy.py",
        "description": "Permit required policy tests",
        "required": True,
    },
    "regression_smoke": {
        "path": "skillforge/tests/test_regression_seed_smoke.py",
        "description": "Regression seed smoke tests",
        "required": True,
    },
}


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class CheckResult:
    """Result of a single check."""
    name: str
    category: str
    passed: bool
    message: str
    details: Optional[dict] = None


@dataclass
class ValidationResult:
    """Overall validation result."""
    timestamp: str
    job_id: str
    strict_mode: bool
    checks: list[CheckResult] = field(default_factory=list)
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    overall_passed: bool = True

    def add_check(self, result: CheckResult):
        self.checks.append(result)
        self.total_checks += 1
        if result.passed:
            self.passed_checks += 1
        else:
            self.failed_checks += 1
            if self.strict_mode:
                self.overall_passed = False

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "job_id": self.job_id,
            "strict_mode": self.strict_mode,
            "overall_passed": self.overall_passed,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "checks": [asdict(c) for c in self.checks],
        }


# ============================================================================
# Validators
# ============================================================================

class SeedsValidator:
    """P0/P1 Seeds Validator."""

    def __init__(self, base_path: Path, strict: bool = True):
        self.base_path = base_path
        self.strict = strict
        self.result = ValidationResult(
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            job_id=JOB_ID,
            strict_mode=strict,
        )

    def validate_all(self) -> ValidationResult:
        """Run all validations."""
        print(f"=== SEEDS P0/P1 Validator ===")
        print(f"Job ID: {JOB_ID}")
        print(f"Strict Mode: {self.strict}")
        print(f"Base Path: {self.base_path}")
        print()

        # P0 Seeds
        print("--- P0 Seeds ---")
        for name, config in P0_SEEDS.items():
            self._validate_seed(name, config, "P0")

        # P1 Seeds
        print("\n--- P1 Seeds ---")
        for name, config in P1_SEEDS.items():
            self._validate_seed(name, config, "P1")

        # Test Suites
        print("\n--- Test Suites ---")
        for name, config in TEST_SUITES.items():
            self._validate_test(name, config)

        # Summary
        print("\n=== Summary ===")
        print(f"Total: {self.result.total_checks}")
        print(f"Passed: {self.result.passed_checks}")
        print(f"Failed: {self.result.failed_checks}")
        print(f"Overall: {'PASS' if self.result.overall_passed else 'FAIL'}")

        return self.result

    def _validate_seed(self, name: str, config: dict, category: str):
        """Validate a single seed file/directory."""
        path = self.base_path / config["path"]
        expected_type = config.get("type", "file")
        description = config.get("description", "")

        if expected_type == "file":
            exists = path.is_file()
            exists_msg = "file exists" if exists else "file NOT found"
        else:
            exists = path.is_dir()
            exists_msg = "dir exists" if exists else "dir NOT found"

        # Validate JSONL/YML files have content
        content_valid = True
        content_msg = ""
        if exists and path.suffix == ".jsonl":
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = [l.strip() for l in f if l.strip()]
                    if len(lines) == 0:
                        content_valid = False
                        content_msg = " (empty file)"
                    else:
                        # Validate first line is valid JSON
                        json.loads(lines[0])
                        content_msg = f" ({len(lines)} lines)"
            except Exception as e:
                content_valid = False
                content_msg = f" (parse error: {e})"

        passed = exists and content_valid
        message = f"{exists_msg}{content_msg}"

        result = CheckResult(
            name=name,
            category=category,
            passed=passed,
            message=message,
            details={"path": str(path), "description": description},
        )
        self.result.add_check(result)

        status = "✅" if passed else "❌"
        print(f"  {status} {name}: {message}")

    def _validate_test(self, name: str, config: dict):
        """Validate a test suite by running it."""
        test_path = self.base_path / config["path"]
        description = config.get("description", "")
        required = config.get("required", False)

        if not test_path.exists():
            result = CheckResult(
                name=name,
                category="TEST",
                passed=False,
                message="test file NOT found",
                details={"path": str(test_path), "required": required},
            )
            self.result.add_check(result)
            print(f"  ❌ {name}: test file NOT found")
            return

        # Run pytest on the test file
        try:
            cmd = [
                sys.executable, "-m", "pytest",
                str(test_path),
                "-q", "--tb=no",
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.base_path),
                timeout=120,
            )

            passed = result.returncode == 0
            output = result.stdout.strip()

            # Parse output for pass/fail counts
            if "passed" in output:
                message = output.split('\n')[-1] if output else "passed"
            elif "failed" in output:
                message = output.split('\n')[-1] if output else "failed"
            else:
                message = f"exit code {result.returncode}"

        except subprocess.TimeoutExpired:
            passed = False
            message = "timeout (>120s)"
        except Exception as e:
            passed = False
            message = f"error: {e}"

        check_result = CheckResult(
            name=name,
            category="TEST",
            passed=passed,
            message=message,
            details={"path": str(test_path), "description": description, "required": required},
        )
        self.result.add_check(check_result)

        status = "✅" if passed else "❌"
        print(f"  {status} {name}: {message}")


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="SEEDS P0/P1 Validator - CI enforcement gate"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode: fail on any error",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )
    parser.add_argument(
        "--base-path",
        type=str,
        default=None,
        help="Base path for validation (default: current directory)",
    )

    args = parser.parse_args()

    # 强制防呆：检查 PYTEST_ADDOPTS 配置
    check_pytest_temp_config()

    # Determine base path
    if args.base_path:
        base_path = Path(args.base_path)
    else:
        # Find project root (look for skillforge directory)
        current = Path.cwd()
        while current != current.parent:
            if (current / "skillforge").exists():
                base_path = current
                break
            current = current.parent
        else:
            base_path = Path.cwd()

    # Run validation
    validator = SeedsValidator(base_path, strict=args.strict)
    result = validator.validate_all()

    # Output
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))

    # Exit code
    if not result.overall_passed:
        print("\n❌ Validation FAILED (strict mode)")
        sys.exit(1)
    else:
        print("\n✅ Validation PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
