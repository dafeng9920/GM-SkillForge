"""
BatchPermitIssuer — 批量 Permit 签发服务，支持 N 目标批量处理。

扩展自 PermitIssuer，实现：
- 从 2 目标扩展到 N 目标（默认 5）
- 复用同一 permit/tombstone 规则
- 支持可配置的失败策略（all-or-nothing / best-effort）
- 每个目标独立 Evidence 生成
- 任一目标失败时的批次策略行为

失败策略（FailureStrategy）：
- ALL_OR_NOTHING: 任一失败则全部回滚（默认，符合审计要求）
- BEST_EFFORT: 允许部分成功，失败目标生成 tombstone
- MAJORITY_VOTE: 多数成功则批次成功

Tombstone 规则：
- 失败目标生成 tombstone 记录
- tombstone 包含: target_id, error_code, error_message, evidence_ref
- tombstone 可追溯、可重试

Contract: skillforge/src/contracts/gates/batch_permit.yaml
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .permit_issuer import PermitIssuer


TOOL_REVISION = "1.0.0"
BATCH_SERVICE_NAME = "batch_permit_issuer"

# Default batch size limits
MIN_BATCH_SIZE = 1
MAX_BATCH_SIZE = 5  # 先支持 5 目标
DEFAULT_BATCH_SIZE = 5


class FailureStrategy(Enum):
    """Batch failure handling strategies."""
    ALL_OR_NOTHING = "all_or_nothing"  # 任一失败则全部回滚
    BEST_EFFORT = "best_effort"        # 允许部分成功
    MAJORITY_VOTE = "majority_vote"    # 多数成功则批次成功


class BatchDecision(Enum):
    """Final batch decision."""
    SUCCESS = "SUCCESS"              # 全部成功
    PARTIAL_SUCCESS = "PARTIAL"      # 部分成功（仅 BEST_EFFORT）
    FAILED = "FAILED"                # 全部失败
    ROLLED_BACK = "ROLLED_BACK"      # 已回滚（ALL_OR_NOTHING）


@dataclass
class TargetResult:
    """Result for a single target in the batch."""
    target_id: str
    target_index: int
    success: bool
    permit_token: Optional[str] = None
    permit_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    evidence_ref: Optional[dict] = None
    tombstone: Optional[dict] = None  # 失败时生成的墓碑记录


@dataclass
class TombstoneRecord:
    """
    Tombstone record for failed targets.

    失败目标的墓碑记录，用于追溯和重试。
    """
    tombstone_id: str
    target_id: str
    target_index: int
    error_code: str
    error_message: str
    retryable: bool
    evidence_ref: dict
    created_at: str
    batch_id: str

    def to_dict(self) -> dict:
        return {
            "tombstone_id": self.tombstone_id,
            "target_id": self.target_id,
            "target_index": self.target_index,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "retryable": self.retryable,
            "evidence_ref": self.evidence_ref,
            "created_at": self.created_at,
            "batch_id": self.batch_id,
        }


@dataclass
class BatchResult:
    """Result of batch permit issuance."""
    batch_id: str
    batch_decision: BatchDecision
    failure_strategy: FailureStrategy
    total_targets: int
    successful_count: int
    failed_count: int
    target_results: list[TargetResult]
    tombstones: list[dict]
    batch_evidence_ref: dict
    rolled_back_permits: list[str]  # 被回滚的 permit_id 列表
    timestamp: str

    def to_dict(self) -> dict:
        return {
            "batch_id": self.batch_id,
            "batch_decision": self.batch_decision.value,
            "failure_strategy": self.failure_strategy.value,
            "total_targets": self.total_targets,
            "successful_count": self.successful_count,
            "failed_count": self.failed_count,
            "target_results": [
                {
                    "target_id": r.target_id,
                    "target_index": r.target_index,
                    "success": r.success,
                    "permit_id": r.permit_id,
                    "error_code": r.error_code,
                    "error_message": r.error_message,
                    "tombstone": r.tombstone,
                }
                for r in self.target_results
            ],
            "tombstones": self.tombstones,
            "batch_evidence_ref": self.batch_evidence_ref,
            "rolled_back_permits": self.rolled_back_permits,
            "timestamp": self.timestamp,
        }


class BatchPermitIssuer:
    """
    批量 Permit 签发服务。

    支持从 2 目标扩展到 N 目标（默认 5）。
    复用同一 permit/tombstone 规则。
    """

    service_name: str = BATCH_SERVICE_NAME
    tool_revision: str = TOOL_REVISION

    def __init__(
        self,
        signing_key: Optional[str] = None,
        key_id: str = "skillforge-permit-key-2026",
        max_batch_size: int = MAX_BATCH_SIZE,
        failure_strategy: FailureStrategy = FailureStrategy.ALL_OR_NOTHING,
    ):
        """
        Initialize BatchPermitIssuer.

        Args:
            signing_key: HMAC signing key
            key_id: Key identifier
            max_batch_size: Maximum batch size (default 5)
            failure_strategy: Failure handling strategy
        """
        self._issuer = PermitIssuer(signing_key=signing_key, key_id=key_id)
        self._max_batch_size = max_batch_size
        self._failure_strategy = failure_strategy

    def validate_batch_input(self, input_data: dict[str, Any]) -> list[str]:
        """
        Validate batch permit issuance request.

        Returns list of validation error strings. Empty list = valid.
        """
        errors: list[str] = []

        if not isinstance(input_data, dict):
            errors.append("SCHEMA_INVALID: input must be a dict")
            return errors

        # Check targets array
        targets = input_data.get("targets")
        if not targets:
            errors.append("SCHEMA_INVALID: targets array is required")
            return errors

        if not isinstance(targets, list):
            errors.append("SCHEMA_INVALID: targets must be an array")
            return errors

        # Check batch size
        if len(targets) < MIN_BATCH_SIZE:
            errors.append(f"SCHEMA_INVALID: batch size must be >= {MIN_BATCH_SIZE}")
        if len(targets) > self._max_batch_size:
            errors.append(f"SCHEMA_INVALID: batch size must be <= {self._max_batch_size}")

        # Validate each target
        for i, target in enumerate(targets):
            if not isinstance(target, dict):
                errors.append(f"SCHEMA_INVALID: targets[{i}] must be a dict")
                continue

            # Each target needs these fields
            required_fields = [
                "target_id", "repo_url", "commit_sha",
                "run_id", "intent_id", "ttl_seconds"
            ]
            for f in required_fields:
                if f not in target:
                    errors.append(f"SCHEMA_INVALID: targets[{i}].{f} is required")

        # Check shared fields
        shared_fields = ["final_gate_decision", "audit_pack_ref"]
        for f in shared_fields:
            if f not in input_data:
                errors.append(f"SCHEMA_INVALID: {f} is required (shared across targets)")

        # Validate failure_strategy if provided
        strategy = input_data.get("failure_strategy")
        if strategy and strategy not in [s.value for s in FailureStrategy]:
            errors.append(f"SCHEMA_INVALID: invalid failure_strategy '{strategy}'")

        return errors

    def issue_batch(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Issue permits for a batch of targets.

        根据 failure_strategy 决定失败行为：
        - ALL_OR_NOTHING: 任一失败则全部回滚
        - BEST_EFFORT: 允许部分成功
        - MAJORITY_VOTE: 多数成功则批次成功

        Args:
            input_data: {
                targets: [
                    {
                        target_id: str,
                        repo_url: str,
                        commit_sha: str,
                        run_id: str,
                        intent_id: str,
                        ttl_seconds: int,
                        ...
                    }
                ],
                final_gate_decision: str,
                audit_pack_ref: str,
                allowed_actions: list[str],
                failure_strategy: str,  # optional override
            }

        Returns:
            BatchResult as dict
        """
        timestamp = self._now_iso()
        batch_id = self._generate_batch_id(timestamp)

        # Get strategy (allow override per-request)
        strategy_str = input_data.get("failure_strategy")
        if strategy_str:
            strategy = FailureStrategy(strategy_str)
        else:
            strategy = self._failure_strategy

        targets = input_data.get("targets", [])
        target_results: list[TargetResult] = []
        issued_permits: list[tuple[str, str]] = []  # (target_id, permit_id)
        tombstones: list[dict] = []

        # Process each target
        for i, target in enumerate(targets):
            result = self._process_single_target(
                target=target,
                target_index=i,
                shared_input=input_data,
                batch_id=batch_id,
            )
            target_results.append(result)

            if result.success and result.permit_id:
                issued_permits.append((result.target_id, result.permit_id))
            elif result.tombstone:
                tombstones.append(result.tombstone)

        # Determine batch decision based on strategy
        successful_count = sum(1 for r in target_results if r.success)
        failed_count = len(target_results) - successful_count

        batch_decision, rolled_back = self._apply_failure_strategy(
            strategy=strategy,
            target_results=target_results,
            issued_permits=issued_permits,
            batch_id=batch_id,
        )

        # Collect ALL tombstones from target_results (including rollback ones)
        for result in target_results:
            if result.tombstone and result.tombstone not in tombstones:
                tombstones.append(result.tombstone)

        # Create batch evidence
        batch_evidence = self._create_batch_evidence(
            batch_id=batch_id,
            batch_decision=batch_decision,
            strategy=strategy,
            successful_count=successful_count,
            failed_count=failed_count,
            rolled_back=rolled_back,
        )

        result = BatchResult(
            batch_id=batch_id,
            batch_decision=batch_decision,
            failure_strategy=strategy,
            total_targets=len(targets),
            successful_count=successful_count if not rolled_back else 0,
            failed_count=failed_count if not rolled_back else len(targets),
            target_results=target_results,
            tombstones=tombstones,
            batch_evidence_ref=batch_evidence,
            rolled_back_permits=rolled_back,
            timestamp=timestamp,
        )

        return result.to_dict()

    def _process_single_target(
        self,
        target: dict[str, Any],
        target_index: int,
        shared_input: dict[str, Any],
        batch_id: str,
    ) -> TargetResult:
        """Process a single target in the batch."""
        target_id = target.get("target_id", f"target-{target_index}")

        # Build permit request
        permit_request = {
            "final_gate_decision": shared_input["final_gate_decision"],
            "audit_pack_ref": shared_input["audit_pack_ref"],
            "repo_url": target["repo_url"],
            "commit_sha": target["commit_sha"],
            "run_id": target["run_id"],
            "intent_id": target["intent_id"],
            "ttl_seconds": target["ttl_seconds"],
            "allowed_actions": shared_input.get("allowed_actions", ["release"]),
            "entry_path": target.get("entry_path"),
            "environment": target.get("environment"),
            "gate_profile": target.get("gate_profile"),
        }

        # Issue permit
        result = self._issuer.issue_permit(permit_request)

        if result.get("success"):
            return TargetResult(
                target_id=target_id,
                target_index=target_index,
                success=True,
                permit_token=result.get("permit_token"),
                permit_id=result.get("permit_id"),
                evidence_ref=result.get("evidence_refs", [{}])[0],
            )
        else:
            # Create tombstone for failed target
            tombstone = self._create_tombstone(
                target_id=target_id,
                target_index=target_index,
                error_code=result.get("error_code", "UNKNOWN"),
                error_message=result.get("error_message", "Unknown error"),
                evidence_ref=result.get("evidence_refs", [{}])[0] if result.get("evidence_refs") else {},
                batch_id=batch_id,
            )
            return TargetResult(
                target_id=target_id,
                target_index=target_index,
                success=False,
                error_code=result.get("error_code"),
                error_message=result.get("error_message"),
                tombstone=tombstone,
            )

    def _apply_failure_strategy(
        self,
        strategy: FailureStrategy,
        target_results: list[TargetResult],
        issued_permits: list[tuple[str, str]],
        batch_id: str,
    ) -> tuple[BatchDecision, list[str]]:
        """
        Apply failure strategy and determine batch decision.

        Returns: (batch_decision, rolled_back_permits)
        """
        successful_count = sum(1 for r in target_results if r.success)
        total_count = len(target_results)
        failed_count = total_count - successful_count

        if strategy == FailureStrategy.ALL_OR_NOTHING:
            # 任一失败则全部回滚
            if failed_count > 0:
                # 标记所有已签发的 permit 为已撤销（模拟）
                rolled_back = [pid for _, pid in issued_permits]
                # 为成功的目标也创建 tombstone（因为回滚）
                for result in target_results:
                    if result.success and not result.tombstone:
                        result.tombstone = self._create_tombstone(
                            target_id=result.target_id,
                            target_index=result.target_index,
                            error_code="BATCH_ROLLBACK",
                            error_message="Batch rolled back due to ALL_OR_NOTHING strategy",
                            evidence_ref=result.evidence_ref or {},
                            batch_id=batch_id,
                        )
                return (BatchDecision.ROLLED_BACK, rolled_back)
            else:
                return (BatchDecision.SUCCESS, [])

        elif strategy == FailureStrategy.BEST_EFFORT:
            # 允许部分成功
            if successful_count == 0:
                return (BatchDecision.FAILED, [])
            elif failed_count > 0:
                return (BatchDecision.PARTIAL_SUCCESS, [])
            else:
                return (BatchDecision.SUCCESS, [])

        elif strategy == FailureStrategy.MAJORITY_VOTE:
            # 多数成功则批次成功
            if successful_count > total_count / 2:
                return (BatchDecision.SUCCESS, [])
            else:
                return (BatchDecision.FAILED, [])

        return (BatchDecision.FAILED, [])

    def _create_tombstone(
        self,
        target_id: str,
        target_index: int,
        error_code: str,
        error_message: str,
        evidence_ref: dict,
        batch_id: str,
    ) -> dict:
        """Create a tombstone record for a failed target."""
        tombstone_id = f"TOMB-{batch_id}-{target_index:03d}"
        timestamp = self._now_iso()

        # Determine if retryable based on error code
        non_retryable_codes = {"I001", "I002"}  # Condition not met, Subject incomplete
        retryable = error_code not in non_retryable_codes

        tombstone = TombstoneRecord(
            tombstone_id=tombstone_id,
            target_id=target_id,
            target_index=target_index,
            error_code=error_code,
            error_message=error_message,
            retryable=retryable,
            evidence_ref=evidence_ref,
            created_at=timestamp,
            batch_id=batch_id,
        )

        return tombstone.to_dict()

    def _create_batch_evidence(
        self,
        batch_id: str,
        batch_decision: BatchDecision,
        strategy: FailureStrategy,
        successful_count: int,
        failed_count: int,
        rolled_back: list[str],
    ) -> dict:
        """Create evidence reference for the batch."""
        timestamp = self._now_iso()
        content = json.dumps({
            "batch_id": batch_id,
            "batch_decision": batch_decision.value,
            "strategy": strategy.value,
            "successful_count": successful_count,
            "failed_count": failed_count,
            "rolled_back_count": len(rolled_back),
            "timestamp": timestamp,
        }, sort_keys=True)
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        return {
            "issue_key": f"BATCH-EVIDENCE-{batch_id}",
            "source_locator": f"batch://{batch_id}",
            "content_hash": content_hash,
            "tool_revision": self.tool_revision,
            "timestamp": timestamp,
            "decision_snapshot": {
                "batch_decision": batch_decision.value,
                "strategy": strategy.value,
                "successful_count": successful_count,
                "failed_count": failed_count,
                "rolled_back": rolled_back,
            },
        }

    def _generate_batch_id(self, timestamp: str) -> str:
        """Generate unique batch ID."""
        date_part = timestamp[:10].replace("-", "")
        unique_part = uuid.uuid4().hex[:8].upper()
        return f"BATCH-{date_part}-{unique_part}"

    def _now_iso(self) -> str:
        """Return ISO-8601 UTC timestamp."""
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# Convenience function
def issue_batch_permits(
    targets: list[dict[str, Any]],
    final_gate_decision: str,
    audit_pack_ref: str,
    signing_key: Optional[str] = None,
    failure_strategy: str = "all_or_nothing",
    **kwargs,
) -> dict[str, Any]:
    """
    Convenience function to issue batch permits.

    Args:
        targets: List of target configurations
        final_gate_decision: Gate decision result (shared)
        audit_pack_ref: Audit pack reference (shared)
        signing_key: HMAC signing key
        failure_strategy: "all_or_nothing" | "best_effort" | "majority_vote"
        **kwargs: Additional shared fields

    Returns:
        BatchResult as dict
    """
    issuer = BatchPermitIssuer(
        signing_key=signing_key,
        failure_strategy=FailureStrategy(failure_strategy),
    )

    input_data = {
        "targets": targets,
        "final_gate_decision": final_gate_decision,
        "audit_pack_ref": audit_pack_ref,
        **kwargs,
    }

    return issuer.issue_batch(input_data)


# CLI entry point
def main():
    """CLI entry point for BatchPermitIssuer."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="BatchPermitIssuer - Batch permit issuance")
    parser.add_argument("--signing-key", required=True, help="HMAC signing key")
    parser.add_argument("--targets-file", required=True, help="JSON file containing targets array")
    parser.add_argument("--final-decision", required=True, help="Final gate decision")
    parser.add_argument("--audit-pack-ref", required=True, help="Audit pack reference")
    parser.add_argument("--strategy", default="all_or_nothing",
                        choices=["all_or_nothing", "best_effort", "majority_vote"],
                        help="Failure handling strategy")
    parser.add_argument("--output", help="Output JSON file path")
    args = parser.parse_args()

    # Load targets
    try:
        with open(args.targets_file, "r", encoding="utf-8") as f:
            targets = json.load(f)
    except Exception as e:
        print(f"Error loading targets file: {e}", file=sys.stderr)
        sys.exit(1)

    issuer = BatchPermitIssuer(
        signing_key=args.signing_key,
        failure_strategy=FailureStrategy(args.strategy),
    )

    input_data = {
        "targets": targets,
        "final_gate_decision": args.final_decision,
        "audit_pack_ref": args.audit_pack_ref,
    }

    result = issuer.issue_batch(input_data)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
    else:
        print(json.dumps(result, indent=2))

    # Exit with appropriate code
    if result["batch_decision"] == "SUCCESS":
        sys.exit(0)
    elif result["batch_decision"] == "PARTIAL_SUCCESS":
        sys.exit(0)  # Partial success is still OK for CLI
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
