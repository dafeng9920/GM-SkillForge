"""
Drawdown Limiter - 回撤控制

Gate 类型: 风控层
职责: 回撤监控，触发暂停/熔断

输入: 账户状态 (equity_curve, current_capital)
输出: GateDecision + 熔断状态

Fail-Closed: 回撤超限必须 DENY
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

from ..audit_event_writer import write_gate_finish_event
from .risk_guard import GateVerdict, Violation, GateDecision

GATE_NAME = "drawdown_limiter"
GATE_VERSION = "1.0.0"


class CircuitState(str, Enum):
    """熔断状态"""
    OPEN = "OPEN"           # 正常交易
    WARNING = "WARNING"     # 警告状态
    HALTED = "HALTED"       # 熔断暂停


@dataclass
class DrawdownConfig:
    """回撤配置"""
    warning_threshold: float = 0.05   # 警告阈值 5%
    halt_threshold: float = 0.10      # 熔断阈值 10%
    recovery_threshold: float = 0.03  # 恢复阈值 3%
    cooldown_minutes: int = 30        # 冷却时间


class DrawdownLimiter:
    """回撤控制 - 账户级熔断"""

    def __init__(self, config: Optional[DrawdownConfig] = None):
        self.config = config or DrawdownConfig()
        self._peak_equity = 0.0
        self._current_drawdown = 0.0
        self._state = CircuitState.OPEN
        self._halt_since: Optional[float] = None

    def update_equity(self, current_equity: float) -> float:
        """更新权益，计算回撤"""
        if current_equity > self._peak_equity:
            self._peak_equity = current_equity

        if self._peak_equity > 0:
            self._current_drawdown = (self._peak_equity - current_equity) / self._peak_equity
        else:
            self._current_drawdown = 0.0

        return self._current_drawdown

    def get_state(self) -> CircuitState:
        """获取当前熔断状态"""
        # 检查冷却期
        if self._state == CircuitState.HALTED and self._halt_since:
            import time
            elapsed = (time.time() - self._halt_since) / 60
            if elapsed >= self.config.cooldown_minutes:
                # 检查是否恢复
                if self._current_drawdown < self.config.recovery_threshold:
                    self._state = CircuitState.OPEN
                    self._halt_since = None

        return self._state

    def execute(self, input_data: Dict[str, Any], context: Optional[Dict] = None) -> GateDecision:
        """执行回撤检查"""
        context = context or {}

        # 1. 获取当前权益
        current_equity = input_data.get("current_equity", 0)
        if current_equity <= 0:
            return GateDecision(
                verdict=GateVerdict.DENY,
                violations=[Violation(
                    rule_id="INVALID_EQUITY",
                    message="无效的权益值",
                    actual=current_equity,
                    threshold=0
                )]
            )

        # 2. 更新回撤
        drawdown = self.update_equity(current_equity)

        # 3. 检查熔断状态
        state = self.get_state()
        violations: List[Violation] = []
        checks_passed: List[str] = []

        if state == CircuitState.HALTED:
            # 已熔断，直接拒绝
            return GateDecision(
                verdict=GateVerdict.DENY,
                violations=[Violation(
                    rule_id="CIRCUIT_HALTED",
                    message=f"账户已熔断，回撤 {drawdown:.2%}",
                    actual=drawdown,
                    threshold=self.config.halt_threshold
                )]
            )

        # 4. 检查是否触发熔断
        if drawdown >= self.config.halt_threshold:
            self._state = CircuitState.HALTED
            import time
            self._halt_since = time.time()

            violations.append(Violation(
                rule_id="DRAWDOWN_HALT",
                message=f"回撤 {drawdown:.2%} 触发熔断阈值 {self.config.halt_threshold:.2%}",
                actual=drawdown,
                threshold=self.config.halt_threshold
            ))

            write_gate_finish_event(
                job_id=context.get("job_id", "unknown"),
                gate_node=GATE_NAME,
                decision="FAIL",
                metadata={"drawdown": drawdown, "state": "HALTED"}
            )

            return GateDecision(
                verdict=GateVerdict.DENY,
                violations=violations
            )

        # 5. 检查警告
        if drawdown >= self.config.warning_threshold:
            self._state = CircuitState.WARNING
            violations.append(Violation(
                rule_id="DRAWDOWN_WARNING",
                message=f"回撤 {drawdown:.2%} 接近警告阈值 {self.config.warning_threshold:.2%}",
                actual=drawdown,
                threshold=self.config.warning_threshold
            ))
            verdict = GateVerdict.WARN
        else:
            self._state = CircuitState.OPEN
            checks_passed.append("drawdown_ok")
            verdict = GateVerdict.ALLOW

        write_gate_finish_event(
            job_id=context.get("job_id", "unknown"),
            gate_node=GATE_NAME,
            decision="PASS" if verdict == GateVerdict.ALLOW else "WARN",
            metadata={"drawdown": drawdown, "state": self._state.value}
        )

        return GateDecision(
            verdict=verdict,
            checks_passed=checks_passed,
            violations=violations
        )

    def force_resume(self):
        """强制恢复（需人工确认）"""
        self._state = CircuitState.OPEN
        self._halt_since = None


def drawdown_limiter(
    current_equity: float,
    context: Optional[Dict] = None
) -> Dict[str, Any]:
    """函数式接口"""
    limiter = DrawdownLimiter()
    decision = limiter.execute({"current_equity": current_equity}, context)

    return {
        "gate_name": GATE_NAME,
        "verdict": decision.verdict.value,
        "next_action": decision.next_action,
        "state": limiter.get_state().value,
        "current_drawdown": limiter._current_drawdown,
        "peak_equity": limiter._peak_equity,
        "violations": [
            {"rule_id": v.rule_id, "message": v.message}
            for v in decision.violations
        ]
    }
