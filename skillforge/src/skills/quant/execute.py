"""
Execute Skill - 交易执行

Skill 类型: 执行层
职责: 完整的交易执行流水线

流水线:
1. risk_guard (风控闸门)
2. drawdown_limiter (回撤控制)
3. order_router (订单路由)
4. 返回结果 + Evidence

Fail-Closed: 任何 Gate 拒绝则停止
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional
from enum import Enum

from ..audit_event_writer import write_gate_finish_event
from .risk_guard import RiskGuard, GateVerdict
from .drawdown_limiter import DrawdownLimiter, CircuitState
from .order_router import OrderRouter, OrderStatus

SKILL_NAME = "execute"
SKILL_VERSION = "1.0.0"


class ExecuteStatus(str, Enum):
    SUCCESS = "SUCCESS"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    PENDING = "PENDING"


@dataclass
class ExecuteResult:
    """执行结果"""
    status: ExecuteStatus
    order_id: Optional[str]
    symbol: str
    action: str
    quantity: int
    gate_results: Dict[str, Any]
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "order_id": self.order_id,
            "symbol": self.symbol,
            "action": self.action,
            "quantity": self.quantity,
            "gate_results": self.gate_results,
            "error": self.error,
        }


class ExecuteSkill:
    """交易执行 Skill - 完整流水线"""

    def __init__(
        self,
        mode: str = "MOCK",
        risk_config: Optional[Dict] = None,
        drawdown_config: Optional[Dict] = None
    ):
        self.risk_guard = RiskGuard()
        self.drawdown_limiter = DrawdownLimiter()
        self.order_router = OrderRouter(mode=mode)

    def execute(
        self,
        intent: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> ExecuteResult:
        """
        执行交易流水线

        Args:
            intent: 交易意图 {action, symbol, quantity, price, ...}
            context: 上下文 {total_capital, current_equity, job_id, ...}

        Returns:
            ExecuteResult
        """
        context = context or {}
        gate_results: Dict[str, Any] = {}

        # 1. 提取基本信息
        action = intent.get("action", "HOLD")
        symbol = intent.get("symbol", "UNKNOWN")
        quantity = intent.get("quantity", 0)

        # 2. HOLD 信号直接返回
        if action == "HOLD":
            return ExecuteResult(
                status=ExecuteStatus.SUCCESS,
                order_id=None,
                symbol=symbol,
                action=action,
                quantity=0,
                gate_results={"message": "HOLD signal, no execution needed"}
            )

        # 3. Gate 1: 风控闸门
        risk_decision = self.risk_guard.execute(intent, context)
        gate_results["risk_guard"] = {
            "verdict": risk_decision.verdict.value,
            "checks_passed": risk_decision.checks_passed,
            "violations": [{"rule_id": v.rule_id, "message": v.message} for v in risk_decision.violations]
        }

        if risk_decision.verdict == GateVerdict.DENY:
            return ExecuteResult(
                status=ExecuteStatus.REJECTED,
                order_id=None,
                symbol=symbol,
                action=action,
                quantity=quantity,
                gate_results=gate_results,
                error="risk_guard DENY"
            )

        # 4. Gate 2: 回撤控制
        current_equity = context.get("current_equity", 1000000)
        drawdown_decision = self.drawdown_limiter.execute(
            {"current_equity": current_equity},
            context
        )
        gate_results["drawdown_limiter"] = {
            "verdict": drawdown_decision.verdict.value,
            "state": self.drawdown_limiter.get_state().value,
            "violations": [{"rule_id": v.rule_id, "message": v.message} for v in drawdown_decision.violations]
        }

        if drawdown_decision.verdict == GateVerdict.DENY:
            return ExecuteResult(
                status=ExecuteStatus.REJECTED,
                order_id=None,
                symbol=symbol,
                action=action,
                quantity=quantity,
                gate_results=gate_results,
                error="drawdown_limiter DENY (circuit breaker)"
            )

        # 5. 执行订单路由
        order = self.order_router.route(intent, context)
        gate_results["order_router"] = order.to_dict()

        # 6. 记录交易
        if order.status in [OrderStatus.FILLED, OrderStatus.ROUTED]:
            self.risk_guard.record_trade()

        # 7. 返回结果
        status = ExecuteStatus.SUCCESS if order.status == OrderStatus.FILLED else ExecuteStatus.PENDING

        write_gate_finish_event(
            job_id=context.get("job_id", "unknown"),
            gate_node=SKILL_NAME,
            decision="PASS" if status == ExecuteStatus.SUCCESS else "WARN",
            metadata={
                "order_id": order.order_id,
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
            }
        )

        return ExecuteResult(
            status=status,
            order_id=order.order_id,
            symbol=symbol,
            action=action,
            quantity=quantity,
            gate_results=gate_results
        )


def execute(
    action: str,
    symbol: str,
    quantity: int,
    price: Optional[float] = None,
    mode: str = "MOCK",
    context: Optional[Dict] = None
) -> Dict[str, Any]:
    """函数式接口"""
    skill = ExecuteSkill(mode=mode)

    result = skill.execute({
        "action": action,
        "symbol": symbol,
        "quantity": quantity,
        "price": price,
    }, context)

    return result.to_dict()
