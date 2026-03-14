"""
合规检查器
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime


class CheckStatus(Enum):
    """检查状态"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


@dataclass
class CheckResult:
    """单项检查结果"""
    name: str
    status: CheckStatus
    details: str
    check_time: datetime = field(default_factory=datetime.now)


@dataclass
class ComplianceResult:
    """合规检查结果"""
    status: str  # APPROVED, REJECTED, WARNING
    decision: str  # PASS, FAIL, CONDITIONAL
    checks: List[CheckResult]
    warnings: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)


@dataclass
class ComplianceRule:
    """合规规则"""
    type: str
    params: Dict
    severity: str = "error"  # error, warning


class ComplianceChecker:
    """
    合规检查器

    负责监管规则检查、风险限额监控、黑名单过滤
    """

    def __init__(self):
        self._rules: List[ComplianceRule] = []
        self._blacklist: set = set()
        self._risk_limits: Dict = {}
        self._check_history: List[ComplianceResult] = []

    def add_rule(self, rule: ComplianceRule):
        """添加合规规则"""
        self._rules.append(rule)

    def set_blacklist(self, symbols: List[str]):
        """设置黑名单"""
        self._blacklist = set(symbols)

    def set_risk_limits(self, limits: Dict):
        """设置风险限额"""
        self._risk_limits = limits

    async def check_order(
        self,
        order: Dict,
        portfolio: Dict,
        current_prices: Dict,
    ) -> ComplianceResult:
        """
        检查订单合规性

        Args:
            order: 订单信息
            portfolio: 投资组合信息
            current_prices: 当前价格

        Returns:
            合规检查结果
        """
        check_results = []
        warnings = []
        conditions = []

        # 应用所有规则
        for rule in self._rules:
            result = await self._apply_rule(order, portfolio, current_prices, rule)
            check_results.append(result)

            if result.status == CheckStatus.FAIL and rule.severity == "error":
                return ComplianceResult(
                    status="REJECTED",
                    decision="FAIL",
                    checks=check_results,
                    warnings=warnings,
                )
            elif result.status == CheckStatus.WARNING:
                warnings.append(f"{result.name}: {result.details}")

        # 综合判断
        if any(c.status == CheckStatus.FAIL for c in check_results):
            status = "REJECTED"
            decision = "FAIL"
        elif any(c.status == CheckStatus.WARNING for c in check_results):
            status = "WARNING"
            decision = "CONDITIONAL"
        else:
            status = "APPROVED"
            decision = "PASS"

        result = ComplianceResult(
            status=status,
            decision=decision,
            checks=check_results,
            warnings=warnings,
            conditions=conditions,
        )

        # 记录历史
        self._check_history.append(result)

        return result

    async def _apply_rule(
        self,
        order: Dict,
        portfolio: Dict,
        current_prices: Dict,
        rule: ComplianceRule,
    ) -> CheckResult:
        """应用单个规则"""
        rule_type = rule.type

        if rule_type == "position_limit":
            return await self._check_position_limit(order, portfolio, rule)
        elif rule_type == "concentration_limit":
            return await self._check_concentration_limit(order, portfolio, current_prices, rule)
        elif rule_type == "blacklist":
            return await self._check_blacklist(order, rule)
        elif rule_type == "short_restriction":
            return await self._check_short_restriction(order, rule)
        elif rule_type == "leverage_limit":
            return await self._check_leverage_limit(order, portfolio, current_prices, rule)
        elif rule_type == "daily_loss_limit":
            return await self._check_daily_loss_limit(order, portfolio, rule)
        else:
            return CheckResult(
                name=rule_type,
                status=CheckStatus.PASS,
                details=f"未知规则类型: {rule_type}",
            )

    async def _check_position_limit(
        self, order: Dict, portfolio: Dict, rule: ComplianceRule
    ) -> CheckResult:
        """检查持仓限额"""
        symbol = order["symbol"]
        quantity = order["quantity"]
        max_position = rule.params.get("max_per_symbol", 10000)

        current_position = portfolio.get("positions", {}).get(symbol, 0)
        new_position = current_position + quantity

        if new_position > max_position:
            return CheckResult(
                name="position_limit",
                status=CheckStatus.FAIL,
                details=f"超出持仓限额: {new_position} > {max_position}",
            )

        return CheckResult(
            name="position_limit",
            status=CheckStatus.PASS,
            details=f"持仓合规: {new_position} <= {max_position}",
        )

    async def _check_concentration_limit(
        self, order: Dict, portfolio: Dict, current_prices: Dict, rule: ComplianceRule
    ) -> CheckResult:
        """检查集中度限制"""
        symbol = order["symbol"]
        quantity = order["quantity"]
        max_concentration = rule.params.get("max_concentration", 0.3)

        current_price = current_prices.get(symbol, 0)
        order_value = quantity * current_price

        # 计算组合总价值
        total_value = portfolio.get("cash", 0)
        for sym, qty in portfolio.get("positions", {}).items():
            price = current_prices.get(sym, 0)
            total_value += qty * price

        # 计算新仓位后的集中度
        current_position_value = portfolio.get("positions", {}).get(symbol, 0) * current_price
        new_symbol_value = current_position_value + order_value
        new_concentration = new_symbol_value / (total_value + order_value) if total_value + order_value > 0 else 0

        if new_concentration > max_concentration:
            return CheckResult(
                name="concentration_limit",
                status=CheckStatus.FAIL,
                details=f"超出集中度限制: {new_concentration:.1%} > {max_concentration:.1%}",
            )

        return CheckResult(
            name="concentration_limit",
            status=CheckStatus.PASS,
            details=f"集中度合规: {new_concentration:.1%} <= {max_concentration:.1%}",
        )

    async def _check_blacklist(
        self, order: Dict, rule: ComplianceRule
    ) -> CheckResult:
        """检查黑名单"""
        symbol = order["symbol"]

        if symbol in self._blacklist:
            return CheckResult(
                name="blacklist",
                status=CheckStatus.FAIL,
                details=f"{symbol} 在黑名单中",
            )

        return CheckResult(
            name="blacklist",
            status=CheckStatus.PASS,
            details=f"{symbol} 不在黑名单中",
        )

    async def _check_short_restriction(
        self, order: Dict, rule: ComplianceRule
    ) -> CheckResult:
        """检查融券限制"""
        if order["side"] != "SELL":
            return CheckResult(
                name="short_restriction",
                status=CheckStatus.PASS,
                details="非融券订单",
            )

        # 检查是否在限制融券名单中
        if rule.params.get("check_hard_to_borrow", False):
            # 这里应该查询硬借用券名单
            pass

        return CheckResult(
            name="short_restriction",
            status=CheckStatus.PASS,
            details="融券限制检查通过",
        )

    async def _check_leverage_limit(
        self, order: Dict, portfolio: Dict, current_prices: Dict, rule: ComplianceRule
    ) -> CheckResult:
        """检查杠杆限制"""
        max_leverage = rule.params.get("max_leverage", 1.0)

        # 计算当前杠杆
        total_value = portfolio.get("cash", 0)
        for sym, qty in portfolio.get("positions", {}).items():
            price = current_prices.get(sym, 0)
            total_value += qty * price

        equity = portfolio.get("cash", 0)
        leverage = total_value / equity if equity > 0 else 0

        if leverage > max_leverage:
            return CheckResult(
                name="leverage_limit",
                status=CheckStatus.FAIL,
                details=f"超出杠杆限制: {leverage:.2f} > {max_leverage:.2f}",
            )

        return CheckResult(
            name="leverage_limit",
            status=CheckStatus.PASS,
            details=f"杠杆合规: {leverage:.2f} <= {max_leverage:.2f}",
        )

    async def _check_daily_loss_limit(
        self, order: Dict, portfolio: Dict, rule: ComplianceRule
    ) -> CheckResult:
        """检查日内损失限额"""
        max_loss = rule.params.get("max_daily_loss", 10000)
        current_pnl = portfolio.get("daily_pnl", 0)

        if current_pnl < -max_loss:
            return CheckResult(
                name="daily_loss_limit",
                status=CheckStatus.FAIL,
                details=f"达到日内损失限额: {current_pnl} < -{max_loss}",
            )

        return CheckResult(
            name="daily_loss_limit",
            status=CheckStatus.PASS,
            details=f"日内损失合规: {current_pnl} >= -{max_loss}",
        )

    def get_check_history(self) -> List[ComplianceResult]:
        """获取检查历史"""
        return self._check_history.copy()

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total = len(self._check_history)
        if total == 0:
            return {"total_checks": 0}

        approved = sum(1 for r in self._check_history if r.status == "APPROVED")
        rejected = sum(1 for r in self._check_history if r.status == "REJECTED")
        warnings = sum(1 for r in self._check_history if r.status == "WARNING")

        return {
            "total_checks": total,
            "approved": approved,
            "rejected": rejected,
            "warnings": warnings,
            "approval_rate": approved / total,
        }
