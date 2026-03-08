"""
GM OS 门禁错误码统一枚举 v1.1

规范:
- CV (Code Violation): 用于榜单/展示的错误码
- CVT (Code Violation Test): 用于测试/门禁 enforcement 的错误码
- CVT 错误码是 CI 可解析的硬门禁
"""

from enum import Enum
from typing import Optional, Dict, Any


class GateErrorCode(str, Enum):
    """
    门禁错误码枚举

    CVT 前缀: Code Violation Test (测试/门禁 enforcement)
    CV 前缀: Code Violation (榜单/展示)
    """

    # Phase 1 Fast-Path 门禁 (硬门禁 - 不可绕过)
    CVT_08_LLM_IN_PHASE1 = "CVT-08"  # Phase1 禁止 LLM 调用
    CVT_09_EXTERNAL_SIDE_EFFECTS_IN_PHASE1 = "CVT-09"  # Phase1 禁止外部副作用

    # Phase 1 Fast-Path 违规 (榜单)
    CV_08_LLM_IN_PHASE1 = "CV-08"  # Phase1 检测到 LLM 调用
    CV_09_EXTERNAL_SIDE_EFFECTS_IN_PHASE1 = "CV-09"  # Phase1 检测到外部副作用

    # Seal 门禁 (Phase 2)
    CVT_01_SEAL_MISSING = "CVT-01"  # seal 字段缺失
    CVT_02_DOMAIN_UNKNOWN = "CVT-02"  # domain 为 unknown
    CVT_03_MISSING_KEYS = "CVT-03"  # required_keys 非空
    CVT_04_COMMIT_NOT_READY = "CVT-04"  # commit_ready == False

    # Policy 门禁
    CVT_05_POLICY_DENIED = "CVT-05"  # 策略拒绝
    CVT_06_ADVISORY_ONLY_VIOLATION = "CVT-06"  # advisory_only 违规
    CVT07_EXECUTOR_BLOCKED = "CVT-07"  # 执行器被阻止

    # SSOT 违规
    CVT_10_CONTROL_PLANE_MISSING = "CVT-10"  # control_plane 缺失
    CVT_11_CONTRACT_HASH_MISMATCH = "CVT-11"  # contract_hash 不一致（Phase2-Confirm/Run）
    CVT_11_META_LOST = "CVT-11"  # 别名：向后兼容（应使用 CVT_11_CONTRACT_HASH_MISMATCH）

    # Phase 2 Side Effects & Authorization
    CVT_12_UNAUTHORIZED_SIDE_EFFECTS = "CVT-12"  # Phase2 未授权的副作用调用

    # Audit Chain 违规 (Phase 2)
    CVT_13_AUDIT_CHAIN_BROKEN = "CVT-13"  # 审计链断裂或事件丢失

    @classmethod
    def is_phase1_violation(cls, code: str) -> bool:
        """检查是否为 Phase1 违规"""
        return code in [cls.CVT_08_LLM_IN_PHASE1, cls.CVT_09_EXTERNAL_SIDE_EFFECTS_IN_PHASE1,
                      cls.CV_08_LLM_IN_PHASE1, cls.CV_09_EXTERNAL_SIDE_EFFECTS_IN_PHASE1]

    @classmethod
    def description(cls, code: str) -> str:
        """获取错误码描述"""
        descriptions = {
            "CVT-08": "Phase1 禁止 LLM 调用",
            "CVT-09": "Phase1 禁止外部副作用",
            "CVT-01": "SEAL_MISSING - seal 字段缺失",
            "CVT-02": "domain 为 unknown",
            "CVT-03": "required_keys 非空",
            "CVT-04": "commit_ready == False",
            "CVT-05": "策略拒绝",
            "CVT-06": "advisory_only 违规",
            "CVT-07": "执行器被阻止",
            "CVT-10": "control_plane 缺失",
            "CVT-11": "CONTRACT_HASH_MISMATCH - contract_hash 不一致",
            "CVT-12": "UNAUTHORIZED_SIDE_EFFECTS - Phase2 未授权的副作用调用",
            "CVT-13": "AUDIT_CHAIN_BROKEN - 审计链断裂或事件丢失",
        }
        return descriptions.get(code, f"未知错误码: {code}")

    @classmethod
    def http_status(cls, code: str) -> int:
        """获取错误码对应的 HTTP 状态码"""
        status_codes = {
            "CVT-01": 400,  # SEAL_MISSING
            "CVT-11": 400,  # CONTRACT_HASH_MISMATCH
            "CVT-12": 403,  # UNAUTHORIZED_SIDE_EFFECTS
            "CVT-13": 409,  # AUDIT_CHAIN_BROKEN
        }
        return status_codes.get(code, 400)  # 默认 400


class GateViolation(Exception):
    """
    门禁违反异常

    当检测到硬门禁违反时抛出此异常
    """

    def __init__(self, error_code: GateErrorCode, context: Optional[Dict[str, Any]] = None):
        self.error_code = error_code
        self.context = context or {}
        super().__init__(f"{error_code.value}: {GateErrorCode.description(error_code.value)}")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典 (用于 API 响应)"""
        return {
            "error_code": self.error_code.value,
            "error_description": GateErrorCode.description(self.error_code.value),
            "context": self.context
        }


class PhaseContext:
    """
    Phase 上下文

    用于传递当前阶段信息，确保 LLM 和 executor 调用符合 fast-path 约束。

    字段:
        phase: int (1=Phase1 fast-path, 2=Phase2 execution)
        selected_option: str (fast/steady/power 策略选择)
        risk_level: str (low/medium/high 风险等级)
        session_id: str (会话 ID)
        turn_id: str (轮次 ID)
        trace_id: str (链路追踪 ID)
    """

    def __init__(
        self,
        phase: int = 1,
        selected_option: str = "steady",
        risk_level: str = "medium",
        session_id: str = "",
        turn_id: str = "",
        trace_id: str = ""
    ):
        self.phase = phase
        self.selected_option = selected_option
        self.risk_level = risk_level
        self.session_id = session_id
        self.turn_id = turn_id
        self.trace_id = trace_id

    def is_phase1(self) -> bool:
        """检查是否为 Phase1"""
        return self.phase == 1

    def is_phase2(self) -> bool:
        """检查是否为 Phase2"""
        return self.phase == 2

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "phase": self.phase,
            "selected_option": self.selected_option,
            "risk_level": self.risk_level,
            "session_id": self.session_id,
            "turn_id": self.turn_id,
            "trace_id": self.trace_id
        }

    @classmethod
    def from_request(cls, request: Dict[str, Any]) -> "PhaseContext":
        """从 API 请求创建 PhaseContext"""
        return cls(
            phase=int(request.get("phase", 1)),
            selected_option=request.get("selected_option", "steady"),
            risk_level=request.get("risk_level", "medium"),
            session_id=request.get("session_id", ""),
            turn_id=request.get("turn_id", ""),
            trace_id=request.get("trace_id", "")
        )


# 全局 Phase Context 上下文管理器
# 用于在请求生命周期内传递 phase context
_current_phase_context: Optional[PhaseContext] = None


def get_phase_context() -> Optional[PhaseContext]:
    """获取当前 Phase Context"""
    return _current_phase_context


def set_phase_context(context: PhaseContext):
    """设置当前 Phase Context"""
    global _current_phase_context
    _current_phase_context = context


def clear_phase_context():
    """清除当前 Phase Context"""
    global _current_phase_context
    _current_phase_context = None
