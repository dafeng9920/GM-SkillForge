#!/usr/bin/env python3
"""
GM-SkillForge 统一最小运行接口 (v0.1)

目的：统一本地主线的最小运行接口，为多Agent并行执行提供标准入口。

统一接口：
- RunRequest: 执行请求
- RunResult: 执行结果
- ArtifactManifest: 工件清单

设计原则：
1. 不做大规模重构，只收口入口
2. 复用现有 schema 和数据结构
3. 提供统一的导入路径
4. 兼容现有的 Permit/AuditPack/GateResult 结构

Spec source: docs/2026-03-10/本地主线盘点_缺口_优先级_2026-03-10.md
Task: T-ASM-02 统一最小运行接口
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# =============================================================================
# 枚举定义
# =============================================================================

class RunStatus(str, Enum):
    """执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class ArtifactKind(str, Enum):
    """工件类型"""
    BLUEPRINT = "blueprint"           # 设计蓝图
    CONTRACT = "contract"             # 合同文件
    CODE = "code"                     # 代码变更
    TEST = "test"                     # 测试报告
    EVIDENCE = "evidence"             # 证据文件
    CONFIG = "config"                 # 配置文件
    DOCUMENTATION = "documentation"   # 文档
    OTHER = "other"                   # 其他


# =============================================================================
# 统一接口：RunRequest
# =============================================================================

@dataclass
class RunRequest:
    """
    统一执行请求

    封装本地主线执行所需的所有输入信息。
    兼容现有的 TaskContract、IntakeRequest 等结构。
    """
    # 基础标识（无默认值）
    task_id: str
    run_id: str
    objective: str                    # 执行目标描述
    executor: str                     # 执行者标识

    # schema_version（使用 field 避免参数顺序问题）
    schema_version: str = field(default="runtime_interface_v0.1")

    # 时间信息
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    expires_at: Optional[str] = None  # 可选的过期时间

    # 输入参数
    parameters: dict[str, Any] = field(default_factory=dict)

    # 约束条件
    constraints: dict[str, Any] = field(default_factory=dict)

    # 关联引用
    contract_ref: Optional[str] = None     # 关联的 contract 路径或 hash
    permit_ref: Optional[str] = None       # 关联的 permit 路径
    demand_ref: Optional[str] = None       # 关联的 demand 路径或 hash

    # 证据要求
    required_artifacts: list[str] = field(default_factory=list)
    required_evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "schema_version": self.schema_version,
            "task_id": self.task_id,
            "run_id": self.run_id,
            "objective": self.objective,
            "executor": self.executor,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "parameters": self.parameters,
            "constraints": self.constraints,
            "contract_ref": self.contract_ref,
            "permit_ref": self.permit_ref,
            "demand_ref": self.demand_ref,
            "required_artifacts": self.required_artifacts,
            "required_evidence": self.required_evidence,
        }

    def calculate_hash(self) -> str:
        """计算请求 hash (用于签名和验证)"""
        canonical = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)
        return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunRequest":
        """从字典创建 RunRequest"""
        return cls(
            task_id=data["task_id"],
            run_id=data["run_id"],
            schema_version=data.get("schema_version", "runtime_interface_v0.1"),
            objective=data["objective"],
            executor=data["executor"],
            created_at=data.get("created_at"),
            expires_at=data.get("expires_at"),
            parameters=data.get("parameters", {}),
            constraints=data.get("constraints", {}),
            contract_ref=data.get("contract_ref"),
            permit_ref=data.get("permit_ref"),
            demand_ref=data.get("demand_ref"),
            required_artifacts=data.get("required_artifacts", []),
            required_evidence=data.get("required_evidence", []),
        )


# =============================================================================
# 统一接口：ArtifactManifest
# =============================================================================

@dataclass
class ArtifactRef:
    """
    工件引用

    引用工件集中的一项工件。
    兼容现有的 dropzone manifest.json 结构。
    """
    path: str                         # 相对路径
    kind: ArtifactKind                # 工件类型
    content_hash: Optional[str] = None  # SHA256 hash
    size_bytes: Optional[int] = None    # 文件大小

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "path": self.path,
            "kind": self.kind.value,
            "content_hash": self.content_hash,
            "size_bytes": self.size_bytes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ArtifactRef":
        """从字典创建 ArtifactRef"""
        return cls(
            path=data["path"],
            kind=ArtifactKind(data.get("kind", "other")),
            content_hash=data.get("content_hash"),
            size_bytes=data.get("size_bytes"),
        )


@dataclass
class ArtifactManifest:
    """
    统一工件清单

    描述执行产生的所有工件和证据。
    兼容现有的 dropzone manifest.json 结构。
    """
    task_id: str
    run_id: str

    # 工件列表
    artifacts: list[ArtifactRef] = field(default_factory=list)

    # 证据列表
    evidence: list[ArtifactRef] = field(default_factory=list)

    # 环境信息
    env: dict[str, str] = field(default_factory=dict)

    # 清单元数据
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    schema_version: str = "runtime_interface_v0.1"

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "schema_version": self.schema_version,
            "task_id": self.task_id,
            "run_id": self.run_id,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "evidence": [e.to_dict() for e in self.evidence],
            "env": self.env,
            "created_at": self.created_at,
        }

    def add_artifact(
        self,
        path: str,
        kind: ArtifactKind = ArtifactKind.OTHER,
        content_hash: Optional[str] = None,
        size_bytes: Optional[int] = None
    ) -> None:
        """添加工件"""
        self.artifacts.append(ArtifactRef(
            path=path,
            kind=kind,
            content_hash=content_hash,
            size_bytes=size_bytes,
        ))

    def add_evidence(
        self,
        path: str,
        content_hash: Optional[str] = None,
        size_bytes: Optional[int] = None
    ) -> None:
        """添加证据"""
        self.evidence.append(ArtifactRef(
            path=path,
            kind=ArtifactKind.EVIDENCE,
            content_hash=content_hash,
            size_bytes=size_bytes,
        ))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ArtifactManifest":
        """从字典创建 ArtifactManifest"""
        artifacts = [ArtifactRef.from_dict(a) for a in data.get("artifacts", [])]
        evidence = [ArtifactRef.from_dict(e) for e in data.get("evidence", [])]
        return cls(
            task_id=data["task_id"],
            run_id=data["run_id"],
            artifacts=artifacts,
            evidence=evidence,
            env=data.get("env", {}),
            created_at=data.get("created_at"),
            schema_version=data.get("schema_version", "runtime_interface_v0.1"),
        )

    @classmethod
    def from_dropzone_manifest(cls, manifest_path: Path, run_id: str) -> "ArtifactManifest":
        """
        从 dropzone manifest.json 加载

        兼容现有的 dropzone manifest 格式。
        """
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        task_id = data.get("task_id", manifest_path.parent.name)

        # 转换 artifacts 列表 (dropzone 中是简单字符串列表)
        artifacts = []
        for path in data.get("artifacts", []):
            artifacts.append(ArtifactRef(
                path=path,
                kind=ArtifactKind.OTHER,
            ))

        # 转换 evidence 列表
        evidence = []
        for path in data.get("evidence", []):
            evidence.append(ArtifactRef(
                path=path,
                kind=ArtifactKind.EVIDENCE,
            ))

        return cls(
            task_id=task_id,
            run_id=run_id,
            artifacts=artifacts,
            evidence=evidence,
            env=data.get("env", {}),
        )


# =============================================================================
# 统一接口：RunResult
# =============================================================================

@dataclass
class EvidenceRef:
    """
    证据引用

    统一的证据引用格式。
    兼容现有的 gate EvidenceRef 结构。
    """
    issue_key: str                    # 问题/任务标识
    source_locator: str               # 定位符 (路径/URL)
    content_hash: str                 # 内容 hash
    tool_revision: str                # 工具版本
    timestamp: str                    # 时间戳
    kind: str = "FILE"                # 证据类型: FILE|LOG|DIFF|SNIPPET|URL

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "issue_key": self.issue_key,
            "source_locator": self.source_locator,
            "content_hash": self.content_hash,
            "tool_revision": self.tool_revision,
            "timestamp": self.timestamp,
            "kind": self.kind,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvidenceRef":
        """从字典创建 EvidenceRef"""
        return cls(
            issue_key=data["issue_key"],
            source_locator=data["source_locator"],
            content_hash=data["content_hash"],
            tool_revision=data["tool_revision"],
            timestamp=data["timestamp"],
            kind=data.get("kind", "FILE"),
        )


@dataclass
class RunResult:
    """
    统一执行结果

    封装执行后的所有输出信息。
    兼容现有的 ExecutionReceipt、GateResult 等结构。
    """
    # 基础标识
    task_id: str
    run_id: str
    executor: str
    status: RunStatus

    # 时间信息
    started_at: str
    finished_at: str
    schema_version: str = "runtime_interface_v0.1"

    # 执行内容
    executed_commands: list[str] = field(default_factory=list)
    exit_code: Optional[int] = None

    # 输出
    output: dict[str, Any] = field(default_factory=dict)
    summary: str = ""

    # 产物
    manifest: Optional[ArtifactManifest] = None
    evidence_refs: list[EvidenceRef] = field(default_factory=list)

    # 错误信息
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    error_details: dict[str, Any] = field(default_factory=dict)

    # 关联引用
    contract_ref: Optional[str] = None
    permit_ref: Optional[str] = None
    receipt_ref: Optional[str] = None     # 执行回执引用

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        result = {
            "schema_version": self.schema_version,
            "task_id": self.task_id,
            "run_id": self.run_id,
            "executor": self.executor,
            "status": self.status.value,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "executed_commands": self.executed_commands,
            "exit_code": self.exit_code,
            "output": self.output,
            "summary": self.summary,
            "evidence_refs": [e.to_dict() for e in self.evidence_refs],
            "contract_ref": self.contract_ref,
            "permit_ref": self.permit_ref,
            "receipt_ref": self.receipt_ref,
        }

        if self.manifest:
            result["manifest"] = self.manifest.to_dict()

        if self.error_code:
            result["error_code"] = self.error_code
        if self.error_message:
            result["error_message"] = self.error_message
        if self.error_details:
            result["error_details"] = self.error_details

        return result

    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.status == RunStatus.SUCCESS

    @property
    def is_failure(self) -> bool:
        """是否失败"""
        return self.status == RunStatus.FAILURE

    @classmethod
    def success_result(
        cls,
        task_id: str,
        run_id: str,
        executor: str,
        started_at: str,
        finished_at: str,
        summary: str = "",
        manifest: Optional[ArtifactManifest] = None,
    ) -> "RunResult":
        """创建成功结果"""
        return cls(
            task_id=task_id,
            run_id=run_id,
            executor=executor,
            status=RunStatus.SUCCESS,
            started_at=started_at,
            finished_at=finished_at,
            summary=summary,
            manifest=manifest,
        )

    @classmethod
    def failure_result(
        cls,
        task_id: str,
        run_id: str,
        executor: str,
        started_at: str,
        finished_at: str,
        error_code: str,
        error_message: str,
        error_details: Optional[dict[str, Any]] = None,
    ) -> "RunResult":
        """创建失败结果"""
        return cls(
            task_id=task_id,
            run_id=run_id,
            executor=executor,
            status=RunStatus.FAILURE,
            started_at=started_at,
            finished_at=finished_at,
            error_code=error_code,
            error_message=error_message,
            error_details=error_details or {},
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunResult":
        """从字典创建 RunResult"""
        manifest = None
        if "manifest" in data:
            manifest = ArtifactManifest.from_dict(data["manifest"])

        evidence_refs = [
            EvidenceRef.from_dict(e) for e in data.get("evidence_refs", [])
        ]

        return cls(
            task_id=data["task_id"],
            run_id=data["run_id"],
            executor=data["executor"],
            status=RunStatus(data["status"]),
            started_at=data["started_at"],
            finished_at=data["finished_at"],
            schema_version=data.get("schema_version", "runtime_interface_v0.1"),
            executed_commands=data.get("executed_commands", []),
            exit_code=data.get("exit_code"),
            output=data.get("output", {}),
            summary=data.get("summary", ""),
            manifest=manifest,
            evidence_refs=evidence_refs,
            error_code=data.get("error_code"),
            error_message=data.get("error_message"),
            error_details=data.get("error_details", {}),
            contract_ref=data.get("contract_ref"),
            permit_ref=data.get("permit_ref"),
            receipt_ref=data.get("receipt_ref"),
        )


# =============================================================================
# 统一入口：RuntimeSession
# =============================================================================

class RuntimeSession:
    """
    运行时会话

    统一的执行会话管理，提供：
    1. 创建 RunRequest
    2. 记录 RunResult
    3. 生成 ArtifactManifest
    4. 关联 Permit/Contract/Receipt
    """

    def __init__(
        self,
        task_id: str,
        executor: str,
        base_path: Optional[Path] = None,
    ):
        """
        初始化运行会话

        Args:
            task_id: 任务标识
            executor: 执行者标识
            base_path: 基础路径（用于解析相对路径）
        """
        import uuid
        self.task_id = task_id
        self.executor = executor
        self.base_path = base_path or Path.cwd()
        self.run_id = f"{task_id}-{uuid.uuid4().hex[:8].upper()}"

        self._request: Optional[RunRequest] = None
        self._result: Optional[RunResult] = None
        self._manifest: Optional[ArtifactManifest] = None
        self._started_at: Optional[str] = None

    def create_request(
        self,
        objective: str,
        parameters: Optional[dict[str, Any]] = None,
        constraints: Optional[dict[str, Any]] = None,
        contract_ref: Optional[str] = None,
        permit_ref: Optional[str] = None,
    ) -> RunRequest:
        """创建执行请求"""
        self._request = RunRequest(
            task_id=self.task_id,
            run_id=self.run_id,
            objective=objective,
            executor=self.executor,
            parameters=parameters or {},
            constraints=constraints or {},
            contract_ref=contract_ref,
            permit_ref=permit_ref,
        )
        return self._request

    def start_run(self) -> str:
        """开始执行，记录开始时间"""
        self._started_at = datetime.now(UTC).isoformat()
        return self._started_at

    def complete_run(
        self,
        status: RunStatus,
        summary: str = "",
        executed_commands: Optional[list[str]] = None,
        exit_code: Optional[int] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> RunResult:
        """完成执行，生成结果"""
        if not self._started_at:
            self.start_run()

        finished_at = datetime.now(UTC).isoformat()

        if status == RunStatus.SUCCESS:
            self._result = RunResult.success_result(
                task_id=self.task_id,
                run_id=self.run_id,
                executor=self.executor,
                started_at=self._started_at,
                finished_at=finished_at,
                summary=summary,
                manifest=self._manifest,
            )
        else:
            self._result = RunResult.failure_result(
                task_id=self.task_id,
                run_id=self.run_id,
                executor=self.executor,
                started_at=self._started_at,
                finished_at=finished_at,
                error_code=error_code or "UNKNOWN",
                error_message=error_message or "Execution failed",
            )

        if executed_commands:
            self._result.executed_commands = executed_commands
        if exit_code is not None:
            self._result.exit_code = exit_code

        return self._result

    def create_manifest(self) -> ArtifactManifest:
        """创建工件清单"""
        self._manifest = ArtifactManifest(
            task_id=self.task_id,
            run_id=self.run_id,
        )
        return self._manifest

    @property
    def request(self) -> Optional[RunRequest]:
        """获取执行请求"""
        return self._request

    @property
    def result(self) -> Optional[RunResult]:
        """获取执行结果"""
        return self._result

    @property
    def manifest(self) -> Optional[ArtifactManifest]:
        """获取工件清单"""
        return self._manifest


# =============================================================================
# 导出接口
# =============================================================================

__all__ = [
    # 枚举
    "RunStatus",
    "ArtifactKind",
    # 核心接口
    "RunRequest",
    "RunResult",
    "ArtifactManifest",
    # 辅助类型
    "ArtifactRef",
    "EvidenceRef",
    # 会话管理
    "RuntimeSession",
]
