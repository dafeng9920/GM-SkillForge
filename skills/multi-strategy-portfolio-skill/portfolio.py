"""
多策略组合管理器
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from scipy.optimize import minimize


class MultiStrategyPortfolio:
    """
    多策略组合管理器

    负责管理多个策略的组合，优化权重分配
    """

    def __init__(self):
        self._strategies = {}
        self._weights = {}
        self._returns_history = {}

    async def add_strategy(
        self,
        strategy_id: str,
        returns: pd.Series,
        initial_weight: float = 0.0,
    ):
        """添加策略"""
        self._strategies[strategy_id] = {
            "returns": returns,
            "initial_weight": initial_weight,
        }
        self._weights[strategy_id] = initial_weight
        self._returns_history[strategy_id] = returns

    async def optimize_weights(
        self,
        method: str = "sharpe_ratio",
        risk_free_rate: float = 0.02,
        max_weight: float = 0.5,
        min_weight: float = 0.0,
    ) -> Dict[str, float]:
        """
        优化权重分配

        Args:
            method: 优化方法
            risk_free_rate: 无风险利率
            max_weight: 单个策略最大权重
            min_weight: 单个策略最小权重

        Returns:
            最优权重
        """
        if not self._strategies:
            return {}

        # 准备收益率数据
        returns_df = pd.DataFrame(self._returns_history)
        returns_df = returns_df.dropna()

        if len(returns_df) < 10:
            # 数据不足，使用等权重
            n = len(self._strategies)
            return {sid: 1.0 / n for sid in self._strategies.keys()}

        if method == "equal_weight":
            return await self._equal_weight_optimization()
        elif method == "sharpe_ratio":
            return await self._sharpe_optimization(
                returns_df, risk_free_rate, max_weight, min_weight
            )
        elif method == "min_variance":
            return await self._min_variance_optimization(
                returns_df, max_weight, min_weight
            )
        elif method == "max_diversification":
            return await self._max_diversification_optimization(
                returns_df, max_weight, min_weight
            )
        else:
            return self._weights.copy()

    async def _equal_weight_optimization(self) -> Dict[str, float]:
        """等权重优化"""
        n = len(self._strategies)
        weight = 1.0 / n
        return {sid: weight for sid in self._strategies.keys()}

    async def _sharpe_optimization(
        self, returns_df: pd.DataFrame, risk_free_rate: float,
        max_weight: float, min_weight: float
    ) -> Dict[str, float]:
        """夏普比率优化"""
        n = len(returns_df.columns)

        # 计算协方差矩阵和期望收益
        cov_matrix = returns_df.cov() * 252  # 年化
        mean_returns = returns_df.mean() * 252

        # 目标函数：负夏普比率
        def objective(weights):
            portfolio_return = np.sum(mean_returns * weights)
            portfolio_variance = np.dot(weights.T, np.dot(cov_matrix.values, weights))
            portfolio_std = np.sqrt(portfolio_variance)
            sharpe = (portfolio_return - risk_free_rate) / portfolio_std if portfolio_std > 0 else -999
            return -sharpe

        # 约束条件
        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},  # 权重和为1
        ]

        # 边界条件
        bounds = [(min_weight, max_weight) for _ in range(n)]

        # 初始权重（等权重）
        x0 = np.array([1.0 / n] * n)

        # 优化
        result = minimize(
            objective,
            x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        if result.success:
            optimal_weights = result.x
            return dict(zip(returns_df.columns, optimal_weights))

        # 优化失败，返回等权重
        return await self._equal_weight_optimization()

    async def _min_variance_optimization(
        self, returns_df: pd.DataFrame, max_weight: float, min_weight: float
    ) -> Dict[str, float]:
        """最小方差优化"""
        n = len(returns_df.columns)
        cov_matrix = returns_df.cov() * 252

        # 目标函数：组合方差
        def objective(weights):
            return np.dot(weights.T, np.dot(cov_matrix.values, weights))

        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},
        ]

        bounds = [(min_weight, max_weight) for _ in range(n)]
        x0 = np.array([1.0 / n] * n)

        result = minimize(
            objective,
            x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        if result.success:
            optimal_weights = result.x
            return dict(zip(returns_df.columns, optimal_weights))

        return await self._equal_weight_optimization()

    async def _max_diversification_optimization(
        self, returns_df: pd.DataFrame, max_weight: float, min_weight: float
    ) -> Dict[str, float]:
        """最大化分散度优化"""
        n = len(returns_df.columns)
        cov_matrix = returns_df.cov()
        stds = np.sqrt(np.diag(cov_matrix))

        # 分散度比率
        def diversification_ratio(weights):
            portfolio_std = np.sqrt(
                np.dot(weights.T, np.dot(cov_matrix.values, weights))
            )
            weighted_avg_std = np.dot(weights, stds)
            return weighted_avg_std / portfolio_std if portfolio_std > 0 else 0

        # 目标函数：负分散度
        def objective(weights):
            return -diversification_ratio(weights)

        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},
        ]

        bounds = [(min_weight, max_weight) for _ in range(n)]
        x0 = np.array([1.0 / n] * n)

        result = minimize(
            objective,
            x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        if result.success:
            optimal_weights = result.x
            return dict(zip(returns_df.columns, optimal_weights))

        return await self._equal_weight_optimization()

    async def calculate_correlation_matrix(self) -> pd.DataFrame:
        """计算策略相关性矩阵"""
        returns_df = pd.DataFrame(self._returns_history)
        return returns_df.corr()

    async def limit_correlation(
        self, max_correlation: float = 0.7
    ) -> Dict[str, float]:
        """
        限制高相关性策略

        对于高相关的策略，降低权重
        """
        corr_matrix = await self.calculate_correlation_matrix()
        weights = self._weights.copy()

        # 找出高相关对
        high_corr_pairs = []
        for i in range(len(corr_matrix)):
            for j in range(i + 1, len(corr_matrix)):
                if abs(corr_matrix.iloc[i, j]) > max_correlation:
                    high_corr_pairs.append((
                        corr_matrix.index[i],
                        corr_matrix.columns[j],
                        corr_matrix.iloc[i, j],
                    ))

        # 调整权重
        for strat1, strat2, corr in high_corr_pairs:
            weight1 = weights.get(strat1, 0)
            weight2 = weights.get(strat2, 0)

            # 降低相关性较高的策略权重
            if weight1 > weight2:
                weights[strat1] = weight1 * (1 - abs(corr) + max_correlation) / 2
            else:
                weights[strat2] = weight2 * (1 - abs(corr) + max_correlation) / 2

        # 重新归一化
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}

        return weights

    async def get_portfolio_metrics(
        self, weights: Optional[Dict[str, float]] = None
    ) -> Dict:
        """计算组合指标"""
        if weights is None:
            weights = self._weights

        returns_df = pd.DataFrame(self._returns_history)
        returns_df = returns_df[list(weights.keys())]
        weight_array = np.array([weights[sid] for sid in returns_df.columns])

        # 组合收益
        portfolio_returns = returns_df @ weight_array

        metrics = {
            "annual_return": portfolio_returns.mean() * 252,
            "annual_volatility": portfolio_returns.std() * np.sqrt(252),
            "sharpe_ratio": (
                portfolio_returns.mean() * 252
            ) / (portfolio_returns.std() * np.sqrt(252)),
            "total_return": (1 + portfolio_returns).prod() - 1,
        }

        return metrics

    def update_weights(self, weights: Dict[str, float]):
        """更新权重"""
        self._weights = weights.copy()
