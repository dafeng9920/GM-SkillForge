#!/usr/bin/env python3
"""
Cloud Lobster Mandatory Gate (LOCAL-ANTIGRAVITY)

FAIL-CLOSED 门禁：强制所有 CLOUD-ROOT 执行必须通过 cloud-lobster-closed-loop-skill

检查项目：
1. 任务是否有有效的 task_contract.json
2. 任务是否有完整的 execution_receipt.json
3. 回执是否通过 verify_execution_receipt 验证
4. 是否有完整的四件套回传 (stdout.log, stderr.log, audit_event.json)
5. 是否有 review_decision 和 final_gate 决策

任何检查失败 => DENY + 写入 docs/compliance_reviews/

Spec source: docs/2026-03-05/cloud_lobster_mandatory_gate/
Environment: LOCAL-ANTIGRAVITY (治理执行与审查)
Target: CLOUD-ROOT (业务执行)
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Error codes
ERROR_CODES = {
    "NO_CONTRACT": "SF_CLOUD_LOBSTER_NO_CONTRACT",
    "NO_RECEIPT": "SF_CLOUD_LOBSTER_NO_RECEIPT",
    "RECEIPT_INVALID": "SF_CLOUD_LOBSTER_RECEIPT_INVALID",
    "ARTIFACTS_MISSING": "SF_CLOUD_LOBSTER_ARTIFACTS_MISSING",
    "NO_VERIFICATION": "SF_CLOUD_LOBSTER_NO_VERIFICATION",
    "VERIFICATION_FAILED": "SF_CLOUD_LOBSTER_VERIFICATION_FAILED",
    "BYPASS_ATTEMPT": "SF_CLOUD_LOBSTER_BYPASS_ATTEMPT",
}


class GateDecision(str, Enum):
    """Gate decision values."""
    ALLOW = "ALLOW"
    DENY = "DENY"


class GateResult:
    """Result of the cloud lobster mandatory gate check."""

    def __init__(self):
        self.status = GateDecision.DENY
        self.task_id = None
        self.error_code = None
        self.errors = []
        self.warnings = []
        self.required_changes = []
        self.violation_evidence = {}
        self.checked_at = datetime.now(UTC).isoformat()

    def add_error(self, code: str, message: str, required_change: str, evidence: dict | None = None):
        """Add an error and set DENY status."""
        self.error_code = code
        self.errors.append({"code": code, "message": message})
        self.required_changes.append(required_change)
        if evidence:
            self.violation_evidence.update(evidence)

    def add_warning(self, message: str):
        """Add a warning."""
        self.warnings.append(message)

    def set_allow(self):
        """Set status to ALLOW."""
        self.status = GateDecision.ALLOW
        self.error_code = None


def find_cloud_tasks(dispatch_dir: Path = Path(".tmp/openclaw-dispatch")) -> list[dict]:
    """
    查找所有云端任务。

    Returns:
        List of task info dicts with task_id, contract_path, etc.
    """
    if not dispatch_dir.exists():
        return []

    tasks = []
    for task_dir in dispatch_dir.iterdir():
        if not task_dir.is_dir():
            continue

        task_id = task_dir.name
        contract_path = task_dir / "task_contract.json"
        receipt_path = task_dir / "execution_receipt.json"

        # 检查是否有合同（CLOUD-ROOT 任务的标志）
        if contract_path.exists():
            tasks.append({
                "task_id": task_id,
                "task_dir": task_dir,
                "contract_path": contract_path,
                "receipt_path": receipt_path,
                "has_contract": True,
            })
        # 检查是否有回执（可能是绕过合同的执行）
        elif receipt_path.exists():
            tasks.append({
                "task_id": task_id,
                "task_dir": task_dir,
                "contract_path": contract_path,
                "receipt_path": receipt_path,
                "has_contract": False,
            })

    return tasks


def verify_task_contract(task_info: dict) -> dict:
    """
    验证任务合同。

    Returns:
        Dict with status, error details.
    """
    result = {
        "status": "FAIL",
        "error_code": None,
        "error_details": [],
    }

    contract_path = task_info["contract_path"]

    if not contract_path.exists():
        result["error_code"] = ERROR_CODES["NO_CONTRACT"]
        result["error_details"].append(f"No task_contract.json found for task {task_info['task_id']}")
        return result

    # 读取并验证合同结构
    try:
        contract_data = json.loads(contract_path.read_text(encoding="utf-8"))

        # 检查必需字段
        required_fields = ["schema_version", "task_id", "baseline_id", "environment", "command_allowlist"]
        missing_fields = [f for f in required_fields if f not in contract_data]

        if missing_fields:
            result["error_code"] = ERROR_CODES["RECEIPT_INVALID"]
            result["error_details"].append(f"Contract missing required fields: {', '.join(missing_fields)}")
            return result

        # 检查环境是否为 CLOUD-ROOT
        if contract_data.get("environment") != "CLOUD-ROOT":
            result["error_details"].append(f"Contract environment is {contract_data.get('environment')}, expected CLOUD-ROOT")

        # 检查 fail_closed 是否为 True
        if not contract_data.get("constraints", {}).get("fail_closed", False):
            result["error_details"].append("Contract does not have fail_closed=True in constraints")

        if result["error_details"]:
            return result

        result["status"] = "PASS"
        return result

    except json.JSONDecodeError as e:
        result["error_code"] = ERROR_CODES["RECEIPT_INVALID"]
        result["error_details"].append(f"Contract invalid JSON: {e}")
        return result
    except Exception as e:
        result["error_code"] = ERROR_CODES["RECEIPT_INVALID"]
        result["error_details"].append(f"Failed to read contract: {e}")
        return result


def verify_execution_artifacts(task_info: dict) -> dict:
    """
    验证执行回执和四件套。

    Returns:
        Dict with status, error details.
    """
    result = {
        "status": "FAIL",
        "error_code": None,
        "error_details": [],
        "missing_artifacts": [],
    }

    task_dir = task_info["task_dir"]
    receipt_path = task_info["receipt_path"]

    if not receipt_path.exists():
        result["error_code"] = ERROR_CODES["NO_RECEIPT"]
        result["error_details"].append(f"No execution_receipt.json found for task {task_info['task_id']}")
        return result

    # 检查四件套
    required_artifacts = [
        ("execution_receipt.json", receipt_path),
        ("stdout.log", task_dir / "stdout.log"),
        ("stderr.log", task_dir / "stderr.log"),
        ("audit_event.json", task_dir / "audit_event.json"),
    ]

    missing = []
    for name, path in required_artifacts:
        if not path.exists():
            missing.append(name)
            result["missing_artifacts"].append(name)

    if missing:
        result["error_code"] = ERROR_CODES["ARTIFACTS_MISSING"]
        result["error_details"].append(f"Missing artifacts: {', '.join(missing)}")
        return result

    result["status"] = "PASS"
    return result


def run_verify_execution_receipt(
    task_info: dict,
    verifier_path: Path = Path("skills/openclaw-cloud-bridge-skill/scripts/verify_execution_receipt.py")
) -> dict:
    """
    运行 verify_execution_receipt.py 脚本。

    固定 verifier: skills/openclaw-cloud-bridge-skill/scripts/verify_execution_receipt.py
    确保与 enforce 脚本使用同一 verifier，避免历史任务误杀。

    Returns:
        Dict with status, error details.
    """
    result = {
        "status": "FAIL",
        "error_code": None,
        "error_details": [],
        "verifier_output": "",
    }

    contract_path = task_info["contract_path"]
    receipt_path = task_info["receipt_path"]

    if not verifier_path.exists():
        result["error_code"] = ERROR_CODES["NO_VERIFICATION"]
        result["error_details"].append(f"Verifier not found: {verifier_path}")
        return result

    # 运行验证脚本
    try:
        cmd = [
            sys.executable,
            str(verifier_path),
            "--contract", str(contract_path),
            "--receipt", str(receipt_path),
            "--quiet",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=Path.cwd())

        result["verifier_output"] = proc.stdout.strip()
        result["returncode"] = proc.returncode

        if proc.returncode == 0 and result["verifier_output"] == "PASS":
            result["status"] = "PASS"
        else:
            result["error_code"] = ERROR_CODES["VERIFICATION_FAILED"]
            result["error_details"].append(f"Verification failed: {result['verifier_output']}")
            if proc.stderr:
                result["error_details"].append(f"Error: {proc.stderr.strip()}")

    except Exception as e:
        result["error_code"] = ERROR_CODES["VERIFICATION_FAILED"]
        result["error_details"].append(f"Failed to run verifier: {e}")

    return result


def write_violation_to_compliance_review(
    gate_result: GateResult,
    task_info: dict,
    compliance_dir: Path = Path("docs/compliance_reviews")
) -> Path:
    """
    将违规记录写入 docs/compliance_reviews/。

    Returns:
        Path to the violation report file.
    """
    compliance_dir.mkdir(parents=True, exist_ok=True)

    # 生成违规报告文件名
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    violation_file = compliance_dir / f"cloud_lobster_violation_{timestamp}.json"

    # 构建违规报告
    violation_report = {
        "report_type": "cloud_lobster_violation",
        "generated_at": gate_result.checked_at,
        "task_id": task_info["task_id"],
        "decision": gate_result.status.value,
        "error_code": gate_result.error_code,
        "errors": gate_result.errors,
        "warnings": gate_result.warnings,
        "required_changes": gate_result.required_changes,
        "violation_evidence": gate_result.violation_evidence,
        "task_info": {
            "task_id": task_info["task_id"],
            "task_dir": str(task_info["task_dir"]),
            "has_contract": task_info.get("has_contract", False),
            "contract_path": str(task_info["contract_path"]) if task_info["contract_path"].exists() else None,
            "receipt_path": str(task_info["receipt_path"]) if task_info["receipt_path"].exists() else None,
        },
        "governance_context": {
            "enforcement_environment": "LOCAL-ANTIGRAVITY",
            "target_environment": "CLOUD-ROOT",
            "enforced_skill": "cloud-lobster-closed-loop-skill",
            "fail_closed_policy": True,
        },
    }

    # 写入文件
    violation_file.write_text(json.dumps(violation_report, indent=2, ensure_ascii=False), encoding="utf-8")

    return violation_file


def run_cloud_lobster_mandatory_gate(
    task_id: str | None = None,
    dispatch_dir: Path = Path(".tmp/openclaw-dispatch"),
    write_violations: bool = True,
    compliance_dir: Path = Path("docs/compliance_reviews"),
) -> GateResult:
    """
    运行 Cloud Lobster 强制门禁。

    Args:
        task_id: 要检查的任务 ID，如果为 None 则检查所有任务
        dispatch_dir: 任务分发目录
        write_violations: 是否将违规写入合规审查目录
        compliance_dir: 合规审查目录

    Returns:
        GateResult with ALLOW/DENY decision
    """
    result = GateResult()

    # 查找云端任务
    tasks = find_cloud_tasks(dispatch_dir)

    if not tasks:
        result.add_warning("No cloud tasks found in dispatch directory")
        result.set_allow()
        return result

    # 如果指定了 task_id，只检查该任务
    if task_id:
        tasks = [t for t in tasks if t["task_id"] == task_id]
        if not tasks:
            result.add_error(
                ERROR_CODES["NO_CONTRACT"],
                f"Task {task_id} not found in dispatch directory",
                f"Check task ID or verify task exists in {dispatch_dir}"
            )
            return result
        result.task_id = task_id
    else:
        # 检查所有任务，任何一个失败就 DENY
        result.task_id = f"batch_{len(tasks)}_tasks"

    # 检查每个任务
    all_passed = True
    failed_tasks = []

    for task in tasks:
        task_result = {
            "task_id": task["task_id"],
            "contract_check": None,
            "artifacts_check": None,
            "verification_check": None,
            "overall": "FAIL",
        }

        # 1. 检查合同
        contract_result = verify_task_contract(task)
        task_result["contract_check"] = contract_result

        if contract_result["status"] != "PASS":
            all_passed = False
            failed_tasks.append(task_result)

            # 记录违规
            if write_violations:
                violation_result = GateResult()
                violation_result.task_id = task["task_id"]
                violation_result.error_code = contract_result["error_code"]
                violation_result.errors = [
                    {"code": contract_result["error_code"], "message": msg}
                    for msg in contract_result["error_details"]
                ]
                violation_result.required_changes = [
                    "Use cloud-lobster-closed-loop-skill to generate valid task_contract.json"
                ]
                violation_result.violation_evidence = {
                    "violation_type": "no_contract_or_invalid",
                    "task_id": task["task_id"],
                    "contract_path": str(task["contract_path"]),
                }

                write_violation_to_compliance_review(violation_result, task, compliance_dir)

            continue

        # 2. 检查四件套
        artifacts_result = verify_execution_artifacts(task)
        task_result["artifacts_check"] = artifacts_result

        if artifacts_result["status"] != "PASS":
            all_passed = False
            failed_tasks.append(task_result)

            # 记录违规
            if write_violations:
                violation_result = GateResult()
                violation_result.task_id = task["task_id"]
                violation_result.error_code = artifacts_result["error_code"]
                violation_result.errors = [
                    {"code": artifacts_result["error_code"], "message": msg}
                    for msg in artifacts_result["error_details"]
                ]
                violation_result.required_changes = [
                    "Ensure all four artifacts (execution_receipt.json, stdout.log, stderr.log, audit_event.json) are returned"
                ]
                violation_result.violation_evidence = {
                    "violation_type": "artifacts_incomplete",
                    "task_id": task["task_id"],
                    "missing_artifacts": artifacts_result["missing_artifacts"],
                }

                write_violation_to_compliance_review(violation_result, task, compliance_dir)

            continue

        # 3. 运行 verify_execution_receipt
        verification_result = run_verify_execution_receipt(task)
        task_result["verification_check"] = verification_result

        if verification_result["status"] != "PASS":
            all_passed = False
            failed_tasks.append(task_result)

            # 记录违规
            if write_violations:
                violation_result = GateResult()
                violation_result.task_id = task["task_id"]
                violation_result.error_code = verification_result["error_code"]
                violation_result.errors = [
                    {"code": verification_result["error_code"], "message": msg}
                    for msg in verification_result["error_details"]
                ]
                violation_result.required_changes = [
                    "Fix execution receipt to pass verify_execution_receipt.py validation"
                ]
                violation_result.violation_evidence = {
                    "violation_type": "receipt_verification_failed",
                    "task_id": task["task_id"],
                    "verifier_output": verification_result.get("verifier_output", ""),
                }

                write_violation_to_compliance_review(violation_result, task, compliance_dir)

            continue

        # 所有检查通过
        task_result["overall"] = "PASS"

    # 汇总结果
    if all_passed:
        result.set_allow()
        result.add_warning(f"All {len(tasks)} task(s) passed cloud lobster mandatory gate")
    else:
        result.add_error(
            ERROR_CODES["BYPASS_ATTEMPT"],
            f"{len(failed_tasks)} task(s) failed cloud lobster mandatory gate",
            "Use cloud-lobster-closed-loop-skill for all CLOUD-ROOT executions",
            {
                "failed_tasks": failed_tasks,
                "total_tasks": len(tasks),
                "passed_tasks": len(tasks) - len(failed_tasks),
            }
        )

    return result


def main() -> int:
    """CLI entry point for cloud lobster mandatory gate."""
    parser = argparse.ArgumentParser(
        description="Cloud Lobster Mandatory Gate - Enforce cloud-lobster-closed-loop-skill (FAIL-CLOSED)"
    )
    parser.add_argument(
        "--task-id",
        help="Specific task ID to check (checks all tasks if not provided)",
    )
    parser.add_argument(
        "--dispatch-dir",
        type=Path,
        default=Path(".tmp/openclaw-dispatch"),
        help="Task dispatch directory (default: .tmp/openclaw-dispatch)",
    )
    parser.add_argument(
        "--compliance-dir",
        type=Path,
        default=Path("docs/compliance_reviews"),
        help="Compliance review directory for violation reports (default: docs/compliance_reviews)",
    )
    parser.add_argument(
        "--no-write-violations",
        action="store_true",
        help="Do not write violation reports to compliance directory",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only output decision (ALLOW/DENY)",
    )
    args = parser.parse_args()

    # 运行门禁
    print("=" * 60)
    print("[CL-MG] Cloud Lobster Mandatory Gate")
    print(f"[CL-MG] Started at {datetime.now(UTC).isoformat()}")
    print(f"[CL-MG] Environment: LOCAL-ANTIGRAVITY -> CLOUD-ROOT")
    print(f"[CL-MG] Dispatch dir: {args.dispatch_dir}")
    print("=" * 60)

    result = run_cloud_lobster_mandatory_gate(
        task_id=args.task_id,
        dispatch_dir=args.dispatch_dir,
        write_violations=not args.no_write_violations,
        compliance_dir=args.compliance_dir,
    )

    print("=" * 60)
    print(f"[CL-MG] Final Decision: {result.status.value}")
    print("=" * 60)

    if result.status == GateDecision.DENY:
        print(f"\n[CL-MG] DENY - Cloud lobster mandatory gate failed")
        print(f"[CL-MG] Error code: {result.error_code}")
        print(f"\n[CL-MG] Errors ({len(result.errors)}):")
        for e in result.errors:
            print(f"  [{e['code']}] {e['message']}")
        print(f"\n[CL-MG] Required changes ({len(result.required_changes)}):")
        for i, c in enumerate(result.required_changes, 1):
            print(f"  {i}. {c}")

        if not args.no_write_violations:
            print(f"\n[CL-MG] Violation reports written to: {args.compliance_dir}")
    else:
        print(f"\n[CL-MG] ALLOW - All cloud tasks comply with mandatory gate")
        print(f"[CL-MG] ✓ Task contract present and valid")
        print(f"[CL-MG] ✓ Four artifacts complete")
        print(f"[CL-MG] ✓ Receipt verification passed")

    if result.warnings:
        print(f"\n[CL-MG] Warnings ({len(result.warnings)}):")
        for w in result.warnings:
            print(f"  - {w}")

    if args.quiet:
        print(result.status.value)

    return 0 if result.status == GateDecision.ALLOW else 1


if __name__ == "__main__":
    sys.exit(main())
