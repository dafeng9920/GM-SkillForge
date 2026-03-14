"""
组合管理器
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime


class PortfolioManager:
    """
    投资组合管理器

    负责资产配置、组合构建、再平衡
    """

    def __init__(self):
        self._current_weights = {}
        self._rebalance_history = []

    async def build_portfolio(
        self,
        assets: List[str],
        returns: pd.DataFrame,
        method: str = "equal_weight",
        constraints: Dict = None,
    ) -> Dict[str, float]:
        """
        构建投资组合

        Args:
            assets: 资产列表
            returns: 收益率数据
            method: 配置方法
            constraints: 约束条件

        Returns:
            资产权重
        """
        if constraints is None:
            constraints = {}

        if method == "equal_weight":
            weights = await self._equal_weight(assets, constraints)
        elif method == "market_cap":
            weights = await self._market_cap_weight(assets, constraints)
        elif method == "risk_parity":
            weights = await self._risk_parity(returns, constraints)
        elif method == "min_variance":
            weights = await self._min_variance(returns, constraints)
        elif method == "max_diversification":
            weights = await self._max_diversification(returns, constraints)
        else:
            raise ValueError(f"Unknown portfolio method: {method}")

        self._current_weights = weights
        return weights

    async def _equal_weight(
        self, assets: List[str], constraints: Dict
    ) -> Dict[str, float]:
        """等权重配置"""
        n = len(assets)
        weight = 1.0 / n

        # 应用约束
        min_weight = constraints.get("min_weight_per_asset", 0)
        max_weight = constraints.get("max_weight_per_asset", 1)

        weight = max(min_weight, min(max_weight, weight))

        # 重新归一化
        total = weight * n
        weight = weight / total

        return {asset: weight for asset in assets}

    async def _market_cap_weight(
        self, assets: List[str], constraints: Dict
    ) -> Dict[str, float]:
        """市值加权配置"""
        # 简化版：实际应从数据源获取市值
        market_caps = {asset: np.random.uniform(100, 1000) for asset in assets}

        total_cap = sum(market_caps.values())
        weights = {
            asset: market_caps[asset] / total_cap
            for asset in assets
        }

        # 应用约束
        return await self._apply_constraints(weights, constraints)

    async def _risk_parity(
        self, returns: pd.DataFrame, constraints: Dict
    ) -> Dict[str, float]:
        """风险平价配置"""
        # 计算协方差矩阵
        cov_matrix = returns.cov()

        # 简化版：使用逆波动率加权
        volatilities = np.sqrt(np.diag(cov_matrix))
        inv_vols = 1.0 / volatilities
        weights = inv_vols / inv_vols.sum()

        weight_dict = dict(zip(returns.columns, weights))

        # 应用约束
        return await self._apply_constraints(weight_dict, constraints)

    async def _min_variance(
        self, returns: pd.DataFrame, constraints: Dict
    ) -> Dict[str, float]:
        """最小方差配置"""
        cov_matrix = returns.cov()
        n = len(cov_matrix)

        # 简化版：使用逆协方差矩阵
        inv_cov = np.linalg.inv(cov_matrix.values)
        ones = np.ones(n)

        weights = inv_cov @ ones
        weights = weights / weights.sum()

        weight_dict = dict(zip(returns.columns, weights))

        # 应用约束
        return await self._apply_constraints(weight_dict, constraints)

    async def _max_diversification(
        self, returns: pd.DataFrame, constraints: Dict
    ) -> Dict[str, float]:
        """最大化分散度配置"""
        cov_matrix = returns.cov()
        volatilities = np.sqrt(np.diag(cov_matrix))

        # 简化版：使用相关性加权
        corr_matrix = returns.corr()
        avg_corr = corr_matrix.mean(axis=1)

        # 分散度比率 = 资产权重加权波动率 / 组合波动率
        # 这里简化为使用低相关性资产获得更高权重
        weights = 1.0 / (1 + avg_corr)
        weights = weights / weights.sum()

        weight_dict = dict(zip(returns.columns, weights))

        # 应用约束
        return await self._apply_constraints(weight_dict, constraints)

    async def _apply_constraints(
        self, weights: Dict[str, float], constraints: Dict
    ) -> Dict[str, float]:
        """应用约束条件"""
        min_weight = constraints.get("min_weight_per_asset", 0)
        max_weight = constraints.get("max_weight_per_asset", 1)

        # 调整权重到约束范围
        adjusted = {}
        for asset, weight in weights.items():
            adjusted[asset] = max(min_weight, min(max_weight, weight))

        # 重新归一化
        total = sum(adjusted.values())
        adjusted = {asset: weight / total for asset, weight in adjusted.items()}

        return adjusted

    async def rebalance(
        self,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        threshold: float = 0.05,
    ) -> Dict[str, float]:
        """
        计算再平衡操作

        Args:
            current_weights: 当前权重
            target_weights: 目标权重
            threshold: 偏离阈值

        Returns:
            需要调整的权重变化
        """
        rebalance_orders = {}

        for asset in target_weights:
            current_weight = current_weights.get(asset, 0)
            target_weight = target_weights[asset]

            deviation = abs(target_weight - current_weight)

            if deviation > threshold:
                rebalance_orders[asset] = target_weight - current_weight

        self._rebalance_history.append({
            "timestamp": datetime.now(),
            "orders": rebalance_orders,
        })

        return rebalance_orders

    async def get_portfolio_metrics(
        self,
        weights: Dict[str, float],
        returns: pd.DataFrame,
    ) -> Dict:
        """计算组合指标"""
        # 组合收益率
        portfolio_returns = returns[list(weights.keys())] @ list(weights.values())

        metrics = {
            "annual_return": portfolio_returns.mean() * 252,
            "annual_volatility": portfolio_returns.std() * np.sqrt(252),
            "sharpe_ratio": (
                portfolio_returns.mean() * 252
            ) / (portfolio_returns.std() * np.sqrt(252)),
        }

        return metrics

    def get_current_weights(self) -> Dict[str, float]:
        """获取当前权重"""
        return self._current_weights

    def get_rebalance_history(self) -> List[Dict]:
        """获取再平衡历史"""
        return self._rebalance_history
