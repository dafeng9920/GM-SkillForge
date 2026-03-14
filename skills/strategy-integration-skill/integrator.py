"""Strategy Integration - 策略集成"""

from .integrator import StrategyIntegrator

__all__ = ["StrategyIntegrator"]


class StrategyIntegrator:
    """策略集成器"""

    def __init__(self):
        self._strategies = {}
        self._signal_queue = []

    async def register_strategy(self, strategy_id, strategy_config):
        """注册策略"""
        self._strategies[strategy_id] = strategy_config

    async def aggregate_signals(self, signals):
        """聚合信号"""
        # 投票机制
        buy_votes = sum(1 for s in signals if s["type"] == "BUY")
        sell_votes = sum(1 for s in signals if s["type"] == "SELL")

        if buy_votes > sell_votes:
            return {"action": "BUY", "confidence": buy_votes / len(signals)}
        elif sell_votes > buy_votes:
            return {"action": "SELL", "confidence": sell_votes / len(signals)}
        else:
            return {"action": "HOLD", "confidence": 0.5}

    async def resolve_conflicts(self, conflicts):
        """解决冲突"""
        # 基于优先级解决
        return sorted(conflicts, key=lambda x: x.get("priority", 0), reverse=True)

    async def allocate_resources(self, total_capital):
        """分配资源"""
        strategies_count = len(self._strategies)
        if strategies_count == 0:
            return {}

        capital_per_strategy = total_capital / strategies_count
        return {sid: capital_per_strategy for sid in self._strategies.keys()}
