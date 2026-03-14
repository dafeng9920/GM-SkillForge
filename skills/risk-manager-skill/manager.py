"""
风险管理器
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from scipy import stats


class RiskManager:
    """
    风险管理器

    负责风险计算、风险限额检查、压力测试
    """

    def __init__(self):
        self._risk_limits = {}
        self._alerts = []

    async def calculate_var(
        self,
        returns: pd.Series,
        confidence_level: float = 0.95,
        time_horizon: int = 1,
    ) -> Dict[str, float]:
        """
        计算 VaR (Value at Risk)

        Args:
            returns: 收益率序列
            confidence_level: 置信水平
            time_horizon: 时间范围（天）

        Returns:
            VaR 结果
        """
        # 历史模拟法
        var_hist = returns.quantile(1 - confidence_level) * np.sqrt(time_horizon)

        # 参数法（假设正态分布）
        mu = returns.mean()
        sigma = returns.std()
        var_param = stats.norm.ppf(1 - confidence_level, mu, sigma) * np.sqrt(time_horizon)

        return {
            "var_historical": var_hist,
            "var_parametric": var_param,
            "confidence_level": confidence_level,
            "time_horizon_days": time_horizon,
        }

    async def calculate_cvar(
        self,
        returns: pd.Series,
        confidence_level: float = 0.95,
        time_horizon: int = 1,
    ) -> float:
        """
        计算 CVaR (Conditional Value at Risk)

        也称为 Expected Shortfall
        """
        var = await self.calculate_var(returns, confidence_level, time_horizon)
        var_value = var["var_historical"]

        # 计算超过 VaR 的平均损失
        tail_losses = returns[returns < var_value / np.sqrt(time_horizon)]
        cvar = tail_losses.mean() * np.sqrt(time_horizon)

        return cvar

    async def calculate_beta(
        self,
        asset_returns: pd.Series,
        market_returns: pd.Series,
    ) -> float:
        """
        计算 Beta（系统性风险）
        """
        covariance = np.cov(asset_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)

        beta = covariance / market_variance
        return beta

    async def calculate_portfolio_risk(
        self,
        weights: Dict[str, float],
        returns: pd.DataFrame,
        confidence_level: float = 0.95,
    ) -> Dict:
        """计算组合风险"""
        # 组合收益率
        portfolio_returns = returns[list(weights.keys())] @ list(weights.values())

        # VaR
        var_result = await self.calculate_var(portfolio_returns, confidence_level)
        cvar = await self.calculate_cvar(portfolio_returns, confidence_level)

        # 波动率
        volatility = portfolio_returns.std() * np.sqrt(252)  # 年化

        # 最大回撤
        cumulative = (1 + portfolio_returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        return {
            "var": var_result["var_historical"],
            "cvar": cvar,
            "volatility": volatility,
            "max_drawdown": max_drawdown,
        }

    async def risk_contribution(
        self,
        weights: Dict[str, float],
        returns: pd.DataFrame,
    ) -> Dict[str, float]:
        """
        风险归因（计算各资产对组合风险的贡献）
        """
        cov_matrix = returns.cov()

        # 组合方差
        portfolio_variance = 0
        for asset_i, weight_i in weights.items():
            for asset_j, weight_j in weights.items():
                portfolio_variance += weight_i * weight_j * cov_matrix.loc[asset_i, asset_j]

        # 边际风险贡献
        marginal_contrib = {}
        for asset_i in weights:
            contrib = 0
            for asset_j in weights:
                contrib += weights[asset_j] * cov_matrix.loc[asset_i, asset_j]
            marginal_contrib[asset_i] = contrib / np.sqrt(portfolio_variance)

        # 风险贡献
        risk_contrib = {
            asset: weights[asset] * marginal_contrib[asset] / np.sqrt(portfolio_variance)
            for asset in weights
        }

        return risk_contrib

    async def stress_test(
        self,
        portfolio_value: float,
        weights: Dict[str, float],
        scenarios: Dict[str, Dict[str, float]],
    ) -> Dict:
        """
        压力测试

        Args:
            portfolio_value: 组合价值
            weights: 资产权重
            scenarios: 压力测试场景 {场景名: {资产: 变化幅度}}

        Returns:
            压力测试结果
        """
        results = {}

        for scenario_name, shocks in scenarios.items():
            scenario_pnl = 0

            for asset, weight in weights.items():
                if asset in shocks:
                    shock = shocks[asset]
                    asset_pnl = portfolio_value * weight * shock
                    scenario_pnl += asset_pnl

            results[scenario_name] = {
                "pnl": scenario_pnl,
                "pnl_pct": scenario_pnl / portfolio_value,
            }

        return results

    def set_risk_limit(
        self,
        metric: str,
        limit: float,
        action: str = "alert",
    ):
        """设置风险限额"""
        self._risk_limits[metric] = {
            "limit": limit,
            "action": action,
        }

    async def check_risk_limits(
        self,
        risk_metrics: Dict,
    ) -> List[Dict]:
        """检查风险限额"""
        alerts = []

        for metric, value in risk_metrics.items():
            if metric in self._risk_limits:
                limit_config = self._risk_limits[metric]
                limit = limit_config["limit"]

                if value > limit:
                    alert = {
                        "type": "risk_limit_exceeded",
                        "metric": metric,
                        "value": value,
                        "limit": limit,
                        "action": limit_config["action"],
                    }
                    alerts.append(alert)
                    self._alerts.append(alert)

        return alerts

    def get_alerts(self) -> List[Dict]:
        """获取风险警报"""
        return self._alerts
