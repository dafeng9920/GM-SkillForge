"""
Quant System 基础模块
提供符合 SkillForge Evidence 规范的输出格式

版本: 1.0.0
对齐: SkillForge constitution_v1
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, List
import hashlib
import json
import uuid


# ============================================
# 枚举定义
# ============================================

class SkillStatus(str, Enum):
    """Skill 执行状态"""
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


class GateVerdict(str, Enum):
    """Gate 裁决"""
    ALLOW = "ALLOW"
    DENY = "DENY"
    WARN = "WARN"


class Severity(str, Enum):
    """违规严重程度"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


# ============================================
# Evidence 数据模型
# ============================================

@dataclass
class Provenance:
    """数据来源信息"""
    source: str
    version: Optional[str] = None
    fetched_at: Optional[str] = None
    model_version: Optional[str] = None
    input_hash: Optional[str] = None

    def to_dict(self) -> dict:
        result = {"source": self.source}
        if self.version:
            result["version"] = self.version
        if self.fetched_at:
            result["fetched_at"] = self.fetched_at
        if self.model_version:
            result["model_version"] = self.model_version
        if self.input_hash:
            result["input_hash"] = self.input_hash
        return result


@dataclass
class Evidence:
    """Evidence 引用"""
    evidence_ref: str
    data_hash: str
    provenance: Provenance

    def to_dict(self) -> dict:
        return {
            "evidence_ref": self.evidence_ref,
            "data_hash": self.data_hash,
            "provenance": self.provenance.to_dict()
        }


# ============================================
# Gate 数据模型
# ============================================

@dataclass
class Violation:
    """Gate 违规"""
    rule_id: str
    severity: Severity
    message: str
    actual_value: Optional[Any] = None
    threshold: Optional[Any] = None

    def to_dict(self) -> dict:
        result = {
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "message": self.message
        }
        if self.actual_value is not None:
            result["actual_value"] = self.actual_value
        if self.threshold is not None:
            result["threshold"] = self.threshold
        return result


@dataclass
class GateDecision:
    """Gate 决策"""
    verdict: GateVerdict
    checks_passed: List[str] = field(default_factory=list)
    violations: List[Violation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict.value,
            "checks_passed": self.checks_passed,
            "violations": [v.to_dict() for v in self.violations]
        }

    @property
    def next_action(self) -> str:
        """根据裁决决定下一步动作"""
        if self.verdict == GateVerdict.DENY:
            return "halt"
        elif self.verdict == GateVerdict.WARN:
            return "continue_with_caution"
        else:
            return "continue"


# ============================================
# Error 数据模型
# ============================================

@dataclass
class SkillError:
    """Skill 错误"""
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    retryable: bool = False

    def to_dict(self) -> dict:
        return {
            "error_code": self.error_code,
            "error_message": self.error_message,
            "retryable": self.retryable
        }


# ============================================
# Metrics 数据模型
# ============================================

@dataclass
class SkillMetrics:
    """执行指标"""
    latency_ms: int
    rows_processed: Optional[int] = None
    tokens_used: Optional[int] = None

    def to_dict(self) -> dict:
        result = {"latency_ms": self.latency_ms}
        if self.rows_processed is not None:
            result["rows_processed"] = self.rows_processed
        if self.tokens_used is not None:
            result["tokens_used"] = self.tokens_used
        return result


# ============================================
# Trace Context 数据模型
# ============================================

@dataclass
class TraceContext:
    """追踪上下文"""
    correlation_id: str
    span_id: str
    parent_span: Optional[str] = None
    session_id: Optional[str] = None

    def to_dict(self) -> dict:
        result = {
            "correlation_id": self.correlation_id,
            "span_id": self.span_id
        }
        if self.parent_span:
            result["parent_span"] = self.parent_span
        if self.session_id:
            result["session_id"] = self.session_id
        return result

    @classmethod
    def create(cls, parent_span: Optional[str] = None,
               correlation_id: Optional[str] = None,
               session_id: Optional[str] = None) -> "TraceContext":
        """创建新的 TraceContext"""
        return cls(
            correlation_id=correlation_id or f"corr-{uuid.uuid4().hex[:16]}",
            span_id=f"span-quant-{uuid.uuid4().hex[:16]}",
            parent_span=parent_span,
            session_id=session_id
        )


# ============================================
# 统一输出信封
# ============================================

@dataclass
class QuantSkillOutput:
    """
    Quant Skill 统一输出格式
    符合 SkillForge Evidence 规范
    """
    skill_id: str
    run_id: str
    trace_context: TraceContext
    timestamp: str
    status: SkillStatus
    data: Any
    evidence: Evidence
    gate_decision: GateDecision
    error: SkillError
    metrics: SkillMetrics

    # 固定版本
    envelope_version: str = "1.0"

    def to_dict(self) -> dict:
        return {
            "envelope_version": self.envelope_version,
            "skill_id": self.skill_id,
            "run_id": self.run_id,
            "trace_id": self.trace_context.span_id,
            "timestamp": self.timestamp,
            "status": self.status.value,
            "data": self.data,
            "evidence": self.evidence.to_dict(),
            "gate_decision": self.gate_decision.to_dict(),
            "error": self.error.to_dict(),
            "metrics": self.metrics.to_dict()
        }


# ============================================
# 基础 Skill 类
# ============================================

class QuantSkillBase:
    """
    Quant Skill 基础类
    提供符合宪法的输出格式
    """

    def __init__(self, skill_id: str, version: str = "1.0.0"):
        self.skill_id = skill_id
        self.version = version

    def _generate_run_id(self) -> str:
        """生成运行 ID"""
        return f"run-{uuid.uuid4().hex[:16]}"

    def _generate_timestamp(self) -> str:
        """生成 ISO-8601 时间戳"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _compute_data_hash(self, data: Any) -> str:
        """计算数据哈希"""
        content = json.dumps(data, sort_keys=True, default=str)
        return f"sha256:{hashlib.sha256(content.encode()).hexdigest()[:32]}"

    def _generate_evidence_ref(self, data_hash: str) -> str:
        """生成 Evidence 引用"""
        return f"evidence://quant/{self.skill_id}/{data_hash.split(':')[1]}"

    def create_success_output(
        self,
        data: Any,
        provenance: Provenance,
        gate_decision: GateDecision,
        metrics: SkillMetrics,
        trace_context: Optional[TraceContext] = None
    ) -> QuantSkillOutput:
        """创建成功输出"""
        run_id = self._generate_run_id()
        data_hash = self._compute_data_hash(data)
        evidence_ref = self._generate_evidence_ref(data_hash)

        if trace_context is None:
            trace_context = TraceContext.create()

        return QuantSkillOutput(
            skill_id=self.skill_id,
            run_id=run_id,
            trace_context=trace_context,
            timestamp=self._generate_timestamp(),
            status=SkillStatus.COMPLETED,
            data=data,
            evidence=Evidence(
                evidence_ref=evidence_ref,
                data_hash=data_hash,
                provenance=provenance
            ),
            gate_decision=gate_decision,
            error=SkillError(),
            metrics=metrics
        )

    def create_failure_output(
        self,
        error_code: str,
        error_message: str,
        retryable: bool,
        metrics: SkillMetrics,
        trace_context: Optional[TraceContext] = None,
        gate_decision: Optional[GateDecision] = None
    ) -> QuantSkillOutput:
        """创建失败输出"""
        run_id = self._generate_run_id()
        timestamp = self._generate_timestamp()

        if trace_context is None:
            trace_context = TraceContext.create()

        if gate_decision is None:
            gate_decision = GateDecision(
                verdict=GateVerdict.DENY,
                checks_passed=[],
                violations=[Violation(
                    rule_id=error_code,
                    severity=Severity.CRITICAL,
                    message=error_message
                )]
            )

        return QuantSkillOutput(
            skill_id=self.skill_id,
            run_id=run_id,
            trace_context=trace_context,
            timestamp=timestamp,
            status=SkillStatus.FAILED,
            data=None,
            evidence=Evidence(
                evidence_ref="",
                data_hash="",
                provenance=Provenance(source="error")
            ),
            gate_decision=gate_decision,
            error=SkillError(
                error_code=error_code,
                error_message=error_message,
                retryable=retryable
            ),
            metrics=metrics
        )

    def create_rejected_output(
        self,
        error_code: str,
        error_message: str,
        validation_errors: List[str],
        trace_context: Optional[TraceContext] = None
    ) -> QuantSkillOutput:
        """创建拒绝输出（输入验证失败）"""
        run_id = self._generate_run_id()
        timestamp = self._generate_timestamp()

        if trace_context is None:
            trace_context = TraceContext.create()

        violations = [
            Violation(
                rule_id="INPUT_VALIDATION",
                severity=Severity.CRITICAL,
                message=error
            )
            for error in validation_errors
        ]

        return QuantSkillOutput(
            skill_id=self.skill_id,
            run_id=run_id,
            trace_context=trace_context,
            timestamp=timestamp,
            status=SkillStatus.REJECTED,
            data=None,
            evidence=Evidence(
                evidence_ref="",
                data_hash="",
                provenance=Provenance(source="validation")
            ),
            gate_decision=GateDecision(
                verdict=GateVerdict.DENY,
                checks_passed=[],
                violations=violations
            ),
            error=SkillError(
                error_code=error_code,
                error_message=error_message,
                retryable=False
            ),
            metrics=SkillMetrics(latency_ms=0)
        )


# ============================================
# 便捷函数
# ============================================

def create_simple_gate_decision(
    checks_passed: List[str],
    violations: List[tuple] = None  # [(rule_id, severity, message), ...]
) -> GateDecision:
    """创建简单的 Gate 决策"""
    violation_objects = []
    if violations:
        for rule_id, severity, message in violations:
            violation_objects.append(Violation(
                rule_id=rule_id,
                severity=Severity(severity),
                message=message
            ))

    # 计算裁决
    critical_violations = [v for v in violation_objects if v.severity == Severity.CRITICAL]
    warning_violations = [v for v in violation_objects if v.severity == Severity.WARNING]

    if critical_violations:
        verdict = GateVerdict.DENY
    elif warning_violations:
        verdict = GateVerdict.WARN
    else:
        verdict = GateVerdict.ALLOW

    return GateDecision(
        verdict=verdict,
        checks_passed=checks_passed,
        violations=violation_objects
    )
