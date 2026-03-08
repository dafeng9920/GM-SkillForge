"""
Risk Guard - 风控闸门

Gate 类型: 风控层
职责: 仓位/日亏损/交易频率限制

输入: 交易意图 (action, symbol, quantity, price)
输出: GateDecision (ALLOW/DENY/WARN)

Fail-Closed: 超限必须 DENY
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

from ..audit_event_writer import write_gate_finish_event

GATE_NAME = "risk_guard"
GATE_VERSION = "1.0.0"


class GateVerdict(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    WARN = "WARN"


@dataclass
class Violation:
    rule_id: str
    message: str
    actual: Any
    threshold: Any


@dataclass
class GateDecision:
    verdict: GateVerdict
    checks_passed: List[str] = field(default_factory=list)
    violations: List[Violation] = field(default_factory=list)

    @property
    def next_action(self) -> str:
        if self.verdict == GateVerdict.DENY:
            return "halt"
        elif self.verdict == GateVerdict.WARN:
            return "continue_with_caution"
        return "continue"


@dataclass
class RiskConfig:
    """风控配置 - 可从数据库加载"""
    max_position_pct: float = 0.1      # 单标的最大仓位 10%
    max_daily_loss_pct: float = 0.02   # 日亏损上限 2%
    max_trades_per_day: int = 20       # 每日最大交易次数
    max_order_value: float = 100000    # 单笔最大金额


class RiskGuard:
    """风控闸门 - 所有交易的前置检查"""

    def __init__(self, config: Optional[RiskConfig] = None):
        self.config = config or RiskConfig()
        self._daily_stats = {
            "trades_count": 0,
            "daily_pnl": 0.0,
            "positions": {},
        }

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """验证输入"""
        errors = []
        required = ["action", "symbol", "quantity"]
        for field_name in required:
            if field_name not in input_data:
                errors.append(f"缺少必填字段: {field_name}")

        if input_data.get("action") not in ["BUY", "SELL", "HOLD"]:
            errors.append("action 必须是 BUY/SELL/HOLD")

        if input_data.get("quantity", 0) <= 0 and input_data.get("action") != "HOLD":
            errors.append("quantity 必须大于 0")

        return errors

    def check_position_limit(self, symbol: str, value: float, total_capital: float) -> Optional[Violation]:
        """检查仓位限制"""
        position_pct = value / total_capital if total_capital > 0 else 0
        if position_pct > self.config.max_position_pct:
            return Violation(
                rule_id="POSITION_LIMIT",
                message=f"单标的仓位 {position_pct:.2%} 超过限制 {self.config.max_position_pct:.2%}",
                actual=position_pct,
                threshold=self.config.max_position_pct
            )
        return None

    def check_daily_loss(self) -> Optional[Violation]:
        """检查日亏损"""
        if self._daily_stats["daily_pnl"] < 0:
            loss_pct = abs(self._daily_stats["daily_pnl"])
            if loss_pct > self.config.max_daily_loss_pct:
                return Violation(
                    rule_id="DAILY_LOSS_LIMIT",
                    message=f"日亏损 {loss_pct:.2%} 超过限制 {self.config.max_daily_loss_pct:.2%}",
                    actual=loss_pct,
                    threshold=self.config.max_daily_loss_pct
                )
        return None

    def check_trade_frequency(self) -> Optional[Violation]:
        """检查交易频率"""
        if self._daily_stats["trades_count"] >= self.config.max_trades_per_day:
            return Violation(
                rule_id="TRADE_FREQUENCY",
                message=f"今日交易次数已达上限 {self.config.max_trades_per_day}",
                actual=self._daily_stats["trades_count"],
                threshold=self.config.max_trades_per_day
            )
        return None

    def check_order_value(self, value: float) -> Optional[Violation]:
        """检查单笔金额"""
        if value > self.config.max_order_value:
            return Violation(
                rule_id="ORDER_VALUE",
                message=f"单笔金额 {value} 超过限制 {self.config.max_order_value}",
                actual=value,
                threshold=self.config.max_order_value
            )
        return None

    def execute(self, input_data: Dict[str, Any], context: Optional[Dict] = None) -> GateDecision:
        """执行风控检查"""
        context = context or {}
        total_capital = context.get("total_capital", 1000000)

        # 1. 输入验证
        validation_errors = self.validate_input(input_data)
        if validation_errors:
            return GateDecision(
                verdict=GateVerdict.DENY,
                violations=[Violation(
                    rule_id="INPUT_VALIDATION",
                    message="; ".join(validation_errors),
                    actual=None,
                    threshold=None
                )]
            )

        # 2. HOLD 信号直接放行
        if input_data["action"] == "HOLD":
            return GateDecision(
                verdict=GateVerdict.ALLOW,
                checks_passed=["hold_signal"]
            )

        violations: List[Violation] = []
        checks_passed: List[str] = []

        # 3. 计算订单价值
        symbol = input_data["symbol"]
        quantity = input_data["quantity"]
        price = input_data.get("price", 0)
        order_value = quantity * price if price else quantity * 100  # 默认价格

        # 4. 仓位检查
        pos_violation = self.check_position_limit(symbol, order_value, total_capital)
        if pos_violation:
            violations.append(pos_violation)
        else:
            checks_passed.append("position_limit")

        # 5. 日亏损检查
        loss_violation = self.check_daily_loss()
        if loss_violation:
            violations.append(loss_violation)
        else:
            checks_passed.append("daily_loss_limit")

        # 6. 交易频率检查
        freq_violation = self.check_trade_frequency()
        if freq_violation:
            violations.append(freq_violation)
        else:
            checks_passed.append("trade_frequency")

        # 7. 单笔金额检查
        value_violation = self.check_order_value(order_value)
        if value_violation:
            violations.append(value_violation)
        else:
            checks_passed.append("order_value")

        # 8. 计算裁决 (Fail-Closed: 任何违规都 DENY)
        if violations:
            verdict = GateVerdict.DENY
        else:
            verdict = GateVerdict.ALLOW

        # 9. 记录审计
        write_gate_finish_event(
            job_id=context.get("job_id", "unknown"),
            gate_node=GATE_NAME,
            decision="PASS" if verdict == GateVerdict.ALLOW else "FAIL",
            metadata={
                "symbol": symbol,
                "action": input_data["action"],
                "verdict": verdict.value,
                "violations": len(violations),
            }
        )

        return GateDecision(
            verdict=verdict,
            checks_passed=checks_passed,
            violations=violations
        )

    def reset_daily(self):
        """重置每日统计"""
        self._daily_stats = {
            "trades_count": 0,
            "daily_pnl": 0.0,
            "positions": {},
        }

    def record_trade(self, pnl: float = 0):
        """记录交易"""
        self._daily_stats["trades_count"] += 1
        self._daily_stats["daily_pnl"] += pnl


def risk_guard(
    action: str,
    symbol: str,
    quantity: int,
    price: float = 0,
    context: Optional[Dict] = None
) -> Dict[str, Any]:
    """函数式接口"""
    guard = RiskGuard()
    decision = guard.execute({
        "action": action,
        "symbol": symbol,
        "quantity": quantity,
        "price": price,
    }, context)

    return {
        "gate_name": GATE_NAME,
        "verdict": decision.verdict.value,
        "next_action": decision.next_action,
        "checks_passed": decision.checks_passed,
        "violations": [
            {"rule_id": v.rule_id, "message": v.message}
            for v in decision.violations
        ]
    }
