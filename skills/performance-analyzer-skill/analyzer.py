"""
绩效分析器
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


class PerformanceAnalyzer:
    """
    绩效分析器

    计算策略绩效指标、生成报告
    """

    def __init__(self):
        pass

    async def calculate_metrics(
        self,
        returns: pd.Series,
        benchmark_returns: Optional[pd.Series] = None,
        risk_free_rate: float = 0.02,
    ) -> Dict:
        """
        计算绩效指标

        Args:
            returns: 策略收益率
            benchmark_returns: 基准收益率
            risk_free_rate: 无风险利率

        Returns:
            绩效指标字典
        """
        metrics = {}

        # 收益指标
        metrics.update(await self._return_metrics(returns, risk_free_rate))

        # 风险指标
        metrics.update(await self._risk_metrics(returns))

        # 风险调整收益
        metrics.update(await self._risk_adjusted_metrics(returns, risk_free_rate))

        # 基准对比
        if benchmark_returns is not None:
            metrics.update(await self._benchmark_comparison(returns, benchmark_returns, risk_free_rate))

        return metrics

    async def _return_metrics(
        self, returns: pd.Series, risk_free_rate: float
    ) -> Dict:
        """收益指标"""
        total_days = len(returns)
        years = total_days / 252  # 假设252个交易日

        total_return = (1 + returns).prod() - 1
        annual_return = (1 + total_return) ** (1 / years) - 1
        cagr = (1 + returns).prod() ** (252 / total_days) - 1

        return {
            "total_return": total_return,
            "annual_return": annual_return,
            "cagr": cagr,
        }

    async def _risk_metrics(self, returns: pd.Series) -> Dict:
        """风险指标"""
        volatility = returns.std() * np.sqrt(252)

        # 下行波动率
        downside_returns = returns[returns < 0]
        downside_deviation = downside_returns.std() * np.sqrt(252)

        # 最大回撤
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        return {
            "volatility": volatility,
            "downside_deviation": downside_deviation,
            "max_drawdown": max_drawdown,
        }

    async def _risk_adjusted_metrics(
        self, returns: pd.Series, risk_free_rate: float
    ) -> Dict:
        """风险调整收益指标"""
        excess_returns = returns - risk_free_rate / 252

        # 夏普比率
        sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(252)

        # 索提诺比率
        downside_returns = returns[returns < 0]
        sortino_ratio = excess_returns.mean() / downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0

        # 卡尔玛比率
        total_return = (1 + returns).prod() - 1
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        calmar_ratio = (1 + total_return) ** (252 / len(returns)) - 1 / abs(max_drawdown) if max_drawdown != 0 else 0

        return {
            "sharpe_ratio": sharpe_ratio,
            "sortino_ratio": sortino_ratio,
            "calmar_ratio": calmar_ratio,
        }

    async def _benchmark_comparison(
        self,
        returns: pd.Series,
        benchmark_returns: pd.Series,
        risk_free_rate: float,
    ) -> Dict:
        """基准对比指标"""
        # 对齐数据
        common_index = returns.index.intersection(benchmark_returns.index)
        returns_aligned = returns.loc[common_index]
        benchmark_aligned = benchmark_returns.loc[common_index]

        # 超额收益
        excess_returns = returns_aligned - benchmark_aligned

        # 跟踪误差
        tracking_error = excess_returns.std() * np.sqrt(252)

        # 信息比率
        information_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0

        # Beta
        covariance = np.cov(returns_aligned, benchmark_aligned)[0, 1]
        benchmark_variance = np.var(benchmark_aligned)
        beta = covariance / benchmark_variance if benchmark_variance > 0 else 0

        # Alpha (CAPM)
        strategy_return = returns_aligned.mean() * 252
        benchmark_return = benchmark_aligned.mean() * 252
        alpha = strategy_return - (risk_free_rate + beta * (benchmark_return - risk_free_rate))

        return {
            "excess_return": excess_returns.mean() * 252,
            "tracking_error": tracking_error,
            "information_ratio": information_ratio,
            "beta": beta,
            "alpha": alpha,
        }

    async def rolling_analysis(
        self,
        returns: pd.Series,
        window: int = 252,
    ) -> pd.DataFrame:
        """
        滚动窗口分析

        Args:
            returns: 收益率
            window: 窗口大小

        Returns:
            滚动指标 DataFrame
        """
        rolling_sharpe = returns.rolling(window).apply(
            lambda x: x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else 0
        )

        rolling_return = returns.rolling(window).apply(
            lambda x: (1 + x).prod() ** (252 / len(x)) - 1
        )

        rolling_volatility = returns.rolling(window).std() * np.sqrt(252)

        return pd.DataFrame({
            "rolling_sharpe": rolling_sharpe,
            "rolling_return": rolling_return,
            "rolling_volatility": rolling_volatility,
        })

    async def generate_report(
        self,
        returns: pd.Series,
        benchmark_returns: Optional[pd.Series] = None,
    ) -> str:
        """
        生成绩效报告

        Returns:
            Markdown 格式的报告
        """
        metrics = await self.calculate_metrics(returns, benchmark_returns)

        report = "# 策略绩效报告\n\n"

        report += "## 收益指标\n\n"
        report += f"- 总收益: {metrics.get('total_return', 0):.2%}\n"
        report += f"- 年化收益: {metrics.get('annual_return', 0):.2%}\n"
        report += f"- CAGR: {metrics.get('cagr', 0):.2%}\n\n"

        report += "## 风险指标\n\n"
        report += f"- 波动率: {metrics.get('volatility', 0):.2%}\n"
        report += f"- 最大回撤: {metrics.get('max_drawdown', 0):.2%}\n\n"

        report += "## 风险调整收益\n\n"
        report += f"- 夏普比率: {metrics.get('sharpe_ratio', 0):.2f}\n"
        report += f"- 索提诺比率: {metrics.get('sortino_ratio', 0):.2f}\n"
        report += f"- 卡尔玛比率: {metrics.get('calmar_ratio', 0):.2f}\n\n"

        if benchmark_returns is not None:
            report += "## 基准对比\n\n"
            report += f"- 超额收益: {metrics.get('excess_return', 0):.2%}\n"
            report += f"- 信息比率: {metrics.get('information_ratio', 0):.2f}\n"
            report += f"- Beta: {metrics.get('beta', 0):.2f}\n"
            report += f"- Alpha: {metrics.get('alpha', 0):.2%}\n\n"

        return report
