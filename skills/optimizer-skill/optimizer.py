"""
参数优化器
"""

import itertools
import random
from typing import Dict, List, Any, Callable
from enum import Enum
from dataclasses import dataclass
import pandas as pd


class OptimizationMethod(Enum):
    """优化方法"""
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN = "bayesian"
    GENETIC = "genetic"


@dataclass
class OptimizationResult:
    """优化结果"""
    best_params: Dict[str, Any]
    best_score: float
    all_results: List[Dict]
    optimization_history: List[Dict]


class ParameterOptimizer:
    """
    参数优化器

    支持多种优化方法寻找最优参数组合
    """

    def __init__(self):
        pass

    async def optimize(
        self,
        strategy: Callable,
        parameter_space: Dict[str, List],
        data: pd.DataFrame,
        method: OptimizationMethod = OptimizationMethod.GRID_SEARCH,
        objective: str = "sharpe_ratio",
        n_trials: int = 100,
        constraints: List[Callable] = None,
    ) -> OptimizationResult:
        """
        优化参数

        args:
            strategy: 策略函数
            parameter_space: 参数空间
            data: 历史数据
            method: 优化方法
            objective: 优化目标
            n_trials: 试验次数（用于随机搜索等）
            constraints: 约束条件列表

        Returns:
            优化结果
        """
        if constraints is None:
            constraints = []

        if method == OptimizationMethod.GRID_SEARCH:
            return await self._grid_search(
                strategy, parameter_space, data, objective, constraints
            )
        elif method == OptimizationMethod.RANDOM_SEARCH:
            return await self._random_search(
                strategy, parameter_space, data, objective, n_trials, constraints
            )
        elif method == OptimizationMethod.BAYESIAN:
            return await self._bayesian_optimization(
                strategy, parameter_space, data, objective, n_trials, constraints
            )
        else:
            raise ValueError(f"Unknown optimization method: {method}")

    async def _grid_search(
        self,
        strategy: Callable,
        parameter_space: Dict[str, List],
        data: pd.DataFrame,
        objective: str,
        constraints: List[Callable],
    ) -> OptimizationResult:
        """网格搜索"""
        # 生成所有参数组合
        param_names = list(parameter_space.keys())
        param_values = list(parameter_space.values())
        all_combinations = list(itertools.product(*param_values))

        results = []
        best_score = float("-inf")
        best_params = None

        for combination in all_combinations:
            params = dict(zip(param_names, combination))

            # 检查约束
            if not all(constraint(params) for constraint in constraints):
                continue

            # 运行回测
            try:
                backtest_result = await strategy(data, params)
                score = backtest_result["metrics"].get(objective, 0)

                results.append({
                    "params": params,
                    "score": score,
                    "metrics": backtest_result["metrics"],
                })

                if score > best_score:
                    best_score = score
                    best_params = params

            except Exception as e:
                print(f"Error with params {params}: {e}")

        return OptimizationResult(
            best_params=best_params,
            best_score=best_score,
            all_results=results,
            optimization_history=[],
        )

    async def _random_search(
        self,
        strategy: Callable,
        parameter_space: Dict[str, List],
        data: pd.DataFrame,
        objective: str,
        n_trials: int,
        constraints: List[Callable],
    ) -> OptimizationResult:
        """随机搜索"""
        results = []
        best_score = float("-inf")
        best_params = None

        for _ in range(n_trials):
            # 随机采样参数
            params = {
                key: random.choice(values)
                for key, values in parameter_space.items()
            }

            # 检查约束
            if not all(constraint(params) for constraint in constraints):
                continue

            # 运行回测
            try:
                backtest_result = await strategy(data, params)
                score = backtest_result["metrics"].get(objective, 0)

                results.append({
                    "params": params,
                    "score": score,
                    "metrics": backtest_result["metrics"],
                })

                if score > best_score:
                    best_score = score
                    best_params = params

            except Exception as e:
                print(f"Error with params {params}: {e}")

        return OptimizationResult(
            best_params=best_params,
            best_score=best_score,
            all_results=results,
            optimization_history=[],
        )

    async def _bayesian_optimization(
        self,
        strategy: Callable,
        parameter_space: Dict[str, List],
        data: pd.DataFrame,
        objective: str,
        n_trials: int,
        constraints: List[Callable],
    ) -> OptimizationResult:
        """贝叶斯优化（简化版）"""
        # 这里简化实现，实际应使用 scikit-optimize 或 optuna
        return await self._random_search(
            strategy, parameter_space, data, objective, n_trials, constraints
        )

    async def cross_validate(
        self,
        strategy: Callable,
        params: Dict,
        data: pd.DataFrame,
        n_folds: int = 5,
    ) -> Dict[str, float]:
        """
        交叉验证

        Args:
            strategy: 策略函数
            params: 参数
            data: 历史数据
            n_folds: 折数

        Returns:
            各折的指标
        """
        fold_size = len(data) // n_folds
        results = []

        for i in range(n_folds):
            train_start = 0
            train_end = (i + 1) * fold_size
            test_start = train_end
            test_end = min((i + 2) * fold_size, len(data))

            train_data = data.iloc[train_start:train_end]
            test_data = data.iloc[test_start:test_end]

            # 训练和测试
            train_result = await strategy(train_data, params)
            test_result = await strategy(test_data, params)

            results.append({
                "fold": i,
                "train_score": train_result["metrics"].get("sharpe_ratio", 0),
                "test_score": test_result["metrics"].get("sharpe_ratio", 0),
            })

        return {
            "mean_test_score": sum(r["test_score"] for r in results) / len(results),
            "std_test_score": (
                sum((r["test_score"] - sum(r["test_score"] for r in results) / len(results)) ** 2
                    for r in results) / len(results)
            ) ** 0.5,
            "fold_results": results,
        }
