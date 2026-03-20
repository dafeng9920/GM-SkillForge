"""
Evidence Transport - Evidence 搬运规则

定义集成层如何搬运 Evidence / AuditPack。

硬约束：
- 只能搬运，不可改写语义
- 必须保持引用完整性
- 不得生成新 Evidence

Task ID: E4
Executor: Kior-B
Date: 2026-03-19
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any


@dataclass
class EvidenceRef:
    """Evidence 引用"""
    evidence_id: str
    source_locator: str
    content_hash: str
    kind: str
    note: str | None = None
    created_at: str | None = None

    def to_dict(self) -> dict:
        return {
            "evidence_id": self.evidence_id,
            "source_locator": self.source_locator,
            "content_hash": self.content_hash,
            "kind": self.kind,
            "note": self.note,
            "created_at": self.created_at,
        }

    def compute_transport_hash(self) -> str:
        """计算传输哈希（用于验证搬运完整性）"""
        payload = f"{self.evidence_id}:{self.source_locator}:{self.content_hash}"
        return sha256(payload.encode()).hexdigest()


@dataclass
class AuditPackRef:
    """AuditPack 引用"""
    pack_id: str
    run_id: str
    pack_path: str
    pack_hash: str
    evidence_count: int
    created_at: str | None = None

    def to_dict(self) -> dict:
        return {
            "pack_id": self.pack_id,
            "run_id": self.run_id,
            "pack_path": self.pack_path,
            "pack_hash": self.pack_hash,
            "evidence_count": self.evidence_count,
            "created_at": self.created_at,
        }


class EvidenceTransportRule:
    """
    Evidence 搬运规则

    职责：
    1. 验证 Evidence 引用格式
    2. 验证 AuditPack 引用格式
    3. 搬运时保持引用完整性
    4. 不得修改内容
    5. 不得生成新 Evidence
    """

    def __init__(self):
        """初始化搬运规则"""
        self._transport_log: list[dict] = []

    def validate_evidence_ref(self, ref: EvidenceRef | dict) -> bool:
        """
        验证 Evidence 引用格式

        Args:
            ref: Evidence 引用

        Returns:
            True if valid
        """
        if isinstance(ref, dict):
            required_fields = ["evidence_id", "source_locator", "content_hash", "kind"]
            return all(field in ref for field in required_fields)

        # EvidenceRef 对象
        return bool(
            ref.evidence_id
            and ref.source_locator
            and ref.content_hash
            and ref.kind
        )

    def validate_audit_pack_ref(self, ref: AuditPackRef | dict) -> bool:
        """
        验证 AuditPack 引用格式

        Args:
            ref: AuditPack 引用

        Returns:
            True if valid
        """
        if isinstance(ref, dict):
            required_fields = ["pack_id", "run_id", "pack_path", "pack_hash", "evidence_count"]
            return all(field in ref for field in required_fields)

        # AuditPackRef 对象
        return bool(
            ref.pack_id
            and ref.run_id
            and ref.pack_path
            and ref.pack_hash
            and ref.evidence_count >= 0
        )

    def transport_evidence_ref(self, ref: EvidenceRef) -> EvidenceRef:
        """
        搬运 Evidence 引用

        只传递引用，不修改内容。

        Args:
            ref: Evidence 引用

        Returns:
            相同的 Evidence 引用（只读搬运）
        """
        # 验证格式
        if not self.validate_evidence_ref(ref):
            raise ValueError(f"Invalid EvidenceRef: {ref}")

        # 记录搬运
        self._log_transport("evidence", ref.to_dict())

        # 只读搬运，不修改
        return EvidenceRef(
            evidence_id=ref.evidence_id,
            source_locator=ref.source_locator,
            content_hash=ref.content_hash,
            kind=ref.kind,
            note=ref.note,
            created_at=ref.created_at,
        )

    def transport_audit_pack_ref(self, ref: AuditPackRef) -> AuditPackRef:
        """
        搬运 AuditPack 引用

        只传递引用，不修改内容。

        Args:
            ref: AuditPack 引用

        Returns:
            相同的 AuditPack 引用（只读搬运）
        """
        # 验证格式
        if not self.validate_audit_pack_ref(ref):
            raise ValueError(f"Invalid AuditPackRef: {ref}")

        # 记录搬运
        self._log_transport("audit_pack", ref.to_dict())

        # 只读搬运，不修改
        return AuditPackRef(
            pack_id=ref.pack_id,
            run_id=ref.run_id,
            pack_path=ref.pack_path,
            pack_hash=ref.pack_hash,
            evidence_count=ref.evidence_count,
            created_at=ref.created_at,
        )

    def can_transport(self, ref: EvidenceRef | AuditPackRef) -> bool:
        """
        检查是否可以搬运

        Args:
            ref: 引用对象

        Returns:
            True if can transport
        """
        if isinstance(ref, EvidenceRef):
            return self.validate_evidence_ref(ref)
        elif isinstance(ref, AuditPackRef):
            return self.validate_audit_pack_ref(ref)
        return False

    def _log_transport(self, kind: str, payload: dict) -> None:
        """记录搬运日志"""
        import time

        self._transport_log.append({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "kind": kind,
            "payload": payload,
        })

    def get_transport_log(self) -> list[dict]:
        """获取搬运日志"""
        return self._transport_log.copy()

    def clear_transport_log(self) -> None:
        """清空搬运日志"""
        self._transport_log.clear()


# 全局规则实例
_rule: EvidenceTransportRule | None = None


def get_transport_rule() -> EvidenceTransportRule:
    """获取全局搬运规则实例"""
    global _rule
    if _rule is None:
        _rule = EvidenceTransportRule()
    return _rule


def transport_evidence_ref(ref: EvidenceRef) -> EvidenceRef:
    """
    搬运 Evidence 引用（便捷函数）

    Args:
        ref: Evidence 引用

    Returns:
        搬运后的引用（内容不变）
    """
    rule = get_transport_rule()
    return rule.transport_evidence_ref(ref)


def transport_audit_pack_ref(ref: AuditPackRef) -> AuditPackRef:
    """
    搬运 AuditPack 引用（便捷函数）

    Args:
        ref: AuditPack 引用

    Returns:
        搬运后的引用（内容不变）
    """
    rule = get_transport_rule()
    return rule.transport_audit_pack_ref(ref)


__all__ = [
    "EvidenceRef",
    "AuditPackRef",
    "EvidenceTransportRule",
    "get_transport_rule",
    "transport_evidence_ref",
    "transport_audit_pack_ref",
]
