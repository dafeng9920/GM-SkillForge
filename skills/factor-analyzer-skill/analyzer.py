"""
因子分析器
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Optional
from sklearn.linear_model import LinearRegression


class FactorAnalyzer:
    """量化因子分析"""

    def __init__(self):
        pass

    async def ic_analysis(
        self,
        factor_data: pd.DataFrame,
        returns: pd.Series,
        periods: List[int] = [1, 5, 10]
    ) -> Dict[str, Dict]:
        """
        IC 分析（Information Coefficient）

        Args:
            factor_data: 因子值 DataFrame (每列是一个因子)
            returns: 未来收益率 Series
            periods: 分析周期

        Returns:
            IC 统计结果
        """
        results = {}

        for factor_name in factor_data.columns:
            factor_values = factor_data[factor_name]
            results[factor_name] = {}

            for period in periods:
                # 计算未来收益
                forward_returns = returns.shift(-period)

                # 去除 NaN
                valid_mask = ~(factor_values.isna() | forward_returns.isna())
                factor_valid = factor_values[valid_mask]
                returns_valid = forward_returns[valid_mask]

                if len(returns_valid) < 10:
                    continue

                # 计算 IC (Spearman 相关系数)
                ic, p_value = stats.spearmanr(factor_valid, returns_valid)

                # 计算 Rank IC
                rank_ic = factor_valid.rank().corr(returns_valid.rank())

                # 计算 IR (Information Ratio)
                # IC 均值 / IC 标准差
                ic_series = factor_valid.rolling(20).apply(
                    lambda x: x.corr(returns_valid.loc[x.index])
                )
                ic_ir = ic_series.mean() / ic_series.std() if ic_series.std() > 0 else 0

                # t 检验
                t_stat = ic * np.sqrt(len(returns_valid) - 2) / np.sqrt(1 - ic**2)

                results[factor_name][f"period_{period}"] = {
                    "ic": ic,
                    "rank_ic": rank_ic,
                    "ic_ir": ic_ir,
                    "t_stat": t_stat,
                    "p_value": p_value,
                    "sample_size": len(returns_valid),
                }

        return results

    async def regression_analysis(
        self,
        factor_data: pd.DataFrame,
        returns: pd.Series
    ) -> Dict:
        """
        多因子回归分析

        Returns:
            回归结果（系数、t值、R²等）
        """
        # 准备数据
        X = factor_data.dropna()
        y = returns.loc[X.index]

        # 对齐数据
        common_index = X.index.intersection(y.index)
        X = X.loc[common_index]
        y = y.loc[common_index]

        # 线性回归
        model = LinearRegression()
        model.fit(X, y)

        # 计算统计量
        y_pred = model.predict(X)
        residuals = y - y_pred

        # R²
        r_squared = model.score(X, y)

        # 调整 R²
        n, k = len(y), X.shape[1]
        adj_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - k - 1)

        # 系数显著性
        results = {
            "coefficients": dict(zip(X.columns, model.coef_)),
            "intercept": model.intercept_,
            "r_squared": r_squared,
            "adj_r_squared": adj_r_squared,
            "residual_std": residuals.std(),
        }

        return results

    async def factor_attribution(
        self,
        factor_returns: Dict[str, float],
        portfolio_return: float
    ) -> Dict:
        """
        因子归因分析

        Args:
            factor_returns: 各因子收益率
            portfolio_return: 组合收益率

        Returns:
            归因结果
        """
        total_return = portfolio_return
        attribution = {}

        for factor, factor_ret in factor_returns.items():
            attribution[factor] = {
                "return": factor_ret,
                "contribution_pct": (factor_ret / total_return * 100) if total_return != 0 else 0,
            }

        return attribution

    async def orthogonalize_factors(
        self,
        factor_data: pd.DataFrame,
        reference_factors: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        因子正交化

        Args:
            factor_data: 原始因子数据
            reference_factors: 参考因子列表（对这些因子正交化）

        Returns:
            正交化后的因子数据
        """
        result = factor_data.copy()

        if reference_factors is None:
            return result

        for factor in reference_factors:
            if factor not in result.columns:
                continue

            # 对每个因子进行回归剔除
            X = result.drop(columns=[factor])
            y = result[factor]

            valid_mask = ~(X.isna().any(axis=1) | y.isna())
            X_valid = X[valid_mask]
            y_valid = y[valid_mask]

            if len(X_valid) < 10:
                continue

            model = LinearRegression()
            model.fit(X_valid, y_valid)

            # 残差即正交化后的因子
            residuals = y_valid - model.predict(X_valid)
            result.loc[valid_mask, factor] = residuals

        return result

    async def calculate_factor_correlation(
        self,
        factor_data: pd.DataFrame
    ) -> pd.DataFrame:
        """计算因子间相关性"""
        return factor_data.corr()
