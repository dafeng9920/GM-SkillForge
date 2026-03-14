"""
ETF Rotation Adapter - ETF轮动策略适配器

职责: 将ETF轮动信号翻译为 Core 可理解的标准格式
原则: 只翻译，不执行

策略说明:
- 基于动量轮动在不同ETF之间切换
- 常见轮动标的: SPY (美股), VEA (发达国际), VWO (新兴市场), AGG (债券)
- 版本: 2.0.0
"""

from __future__ import annotations
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# 导入标准接口契约
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from contracts import (
    SignalAction,
    TradingIntent,
    AdapterContext,
    AdapterOutput,
    Evidence,
    create_hold_signal,
    create_buy_signal,
    create_sell_signal,
    create_error
)


# ============================================
# ETF 定义
# ============================================

ETF_UNIVERSE = {
    "SPY": {
        "name": "SPDR S&P 500 ETF",
        "asset_class": "equity",
        "region": "US"
    },
    "VEA": {
        "name": "Vanguard FTSE Developed Markets ETF",
        "asset_class": "equity",
        "region": "Developed International"
    },
    "VWO": {
        "name": "Vanguard Emerging Markets Stock Index ETF",
        "asset_class": "equity",
        "region": "Emerging Markets"
    },
    "AGG": {
        "name": "iShares Core U.S. Aggregate Bond ETF",
        "asset_class": "fixed_income",
        "region": "US"
    },
    "GLD": {
        "name": "SPDR Gold Shares",
        "asset_class": "commodity",
        "region": "Global"
    }
}


# ============================================
# 输入数据模型
# ============================================

@dataclass
class ETFRotationInput:
    """ETF轮动策略输入"""
    # 轮动标的池
    universe: List[str] = None

    # 回顾周期 (用于计算动量)
    lookback_period: int = 126  # 约6个月

    # 动量阈值
    momentum_threshold: float = 0.0

    # 资金配置
    available_capital: float = 100000

    # 可选 - 当前持仓
    current_position: Optional[str] = None
    current_quantity: Optional[int] = None

    def __post_init__(self):
        if self.universe is None:
            self.universe = ["SPY", "VEA", "VWO", "AGG"]

    def validate(self) -> List[str]:
        """验证输入"""
        errors = []

        if not self.universe:
            errors.append("universe 不能为空")

        invalid_etfs = [etf for etf in self.universe if etf not in ETF_UNIVERSE]
        if invalid_etfs:
            errors.append(f"无效的ETF代码: {invalid_etfs}")

        if self.lookback_period <= 0:
            errors.append("lookback_period 必须大于 0")

        return errors


# ============================================
# 动量计算模型
# ============================================

@dataclass
class ETFScore:
    """ETF评分"""
    symbol: str
    momentum_score: float  # 动量得分
    volatility: float      # 波动率
    sharpe_ratio: float    # 夏普比率
    price: float           # 当前价格
    signal: str            # BUY/SELL/HOLD

    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "momentum_score": round(self.momentum_score, 4),
            "volatility": round(self.volatility, 4),
            "sharpe_ratio": round(self.sharpe_ratio, 2),
            "price": round(self.price, 2),
            "signal": self.signal
        }


# ============================================
# Adapter 实现
# ============================================

class ETFRotationAdapter:
    """
    ETF轮动策略适配器

    基于动量在不同ETF之间进行轮动
    """

    ADAPTER_ID = "etf-rotation"
    VERSION = "2.0.0"

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

    def _calculate_momentum_scores(
        self,
        input_data: ETFRotationInput
    ) -> List[ETFScore]:
        """
        计算各ETF的动量评分

        实际实现应从数据源获取历史价格并计算
        这里使用模拟数据
        """
        import random

        scores = []

        for etf in input_data.universe:
            # 模拟动量计算
            base_return = random.uniform(-0.1, 0.2)  # -10% 到 +20%
            momentum_score = base_return
            volatility = random.uniform(0.1, 0.25)
            sharpe_ratio = momentum_score / volatility if volatility > 0 else 0
            price = random.uniform(80, 200)

            # 生成信号
            if momentum_score > input_data.momentum_threshold:
                signal = "BUY"
            elif momentum_score < -input_data.momentum_threshold:
                signal = "SELL"
            else:
                signal = "HOLD"

            scores.append(ETFScore(
                symbol=etf,
                momentum_score=momentum_score,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                price=price,
                signal=signal
            ))

        # 按动量排序
        scores.sort(key=lambda x: x.momentum_score, reverse=True)
        return scores

    def _select_target_etf(
        self,
        scores: List[ETFScore],
        current_position: Optional[str]
    ) -> tuple[Optional[str], str]:
        """
        选择目标ETF

        Returns:
            (目标ETF, 信号类型)
        """
        if not scores:
            return None, "HOLD"

        best_etf = scores[0]

        # 如果没有持仓
        if current_position is None:
            if best_etf.signal == "BUY":
                return best_etf.symbol, "BUY"
            return None, "HOLD"

        # 如果有持仓，检查是否需要切换
        current_score = next((s for s in scores if s.symbol == current_position), None)

        if current_score is None:
            # 当前持仓不在池中，卖出
            return current_position, "SELL"

        # 如果最佳ETF不是当前持仓，且动量显著更高
        if best_etf.symbol != current_position:
            momentum_diff = best_etf.momentum_score - current_score.momentum_score
            if momentum_diff > 0.05:  # 动量差异超过 5%
                return current_position, "SELL"  # 先卖出当前持仓
                # 下次会买入最佳ETF

        # 检查是否需要卖出当前持仓
        if current_score.signal == "SELL":
            return current_position, "SELL"

        return None, "HOLD"

    def execute(
        self,
        input_data: ETFRotationInput,
        context: Optional[Dict] = None
    ) -> AdapterOutput:
        """
        执行ETF轮动策略

        Args:
            input_data: ETF轮动输入
            context: 上下文 {job_id, trace_id, ...}

        Returns:
            AdapterOutput: 交易信号
        """
        start_time = time.time()
        context = context or {}

        # 1. 输入验证
        errors = input_data.validate()
        if errors:
            return create_error(
                error_code="INPUT_VALIDATION_FAILED",
                error_message="; ".join(errors)
            )

        # 2. 计算动量评分
        scores = self._calculate_momentum_scores(input_data)

        # 3. 选择目标ETF
        target_etf, signal_type = self._select_target_etf(
            scores,
            input_data.current_position
        )

        # 4. 生成交易信号
        if signal_type == "HOLD" or target_etf is None:
            output = create_hold_signal(
                symbol=input_data.current_position or "ETF_PORTFOLIO",
                reasoning=f"无轮动信号，当前持仓: {input_data.current_position or '无'}"
            )
        elif signal_type == "BUY":
            target_score = next(s for s in scores if s.symbol == target_etf)
            quantity = int(input_data.available_capital * 0.95 / target_score.price)

            output = create_buy_signal(
                symbol=target_etf,
                quantity=quantity,
                confidence=min(0.9, 0.5 + target_score.momentum_score),
                reasoning=f"动量轮动: {target_etf} 动量得分 {target_score.momentum_score:.2%} 最高",
                price=target_score.price
            )
            output.metadata["target_etf_info"] = ETF_UNIVERSE.get(target_etf, {})
        else:  # SELL
            current_score = next(
                (s for s in scores if s.symbol == target_etf),
                None
            )
            quantity = input_data.current_quantity or 100

            reasoning = "轮动切换" if current_score and current_score.momentum_score < 0 else "动量转负"
            output = create_sell_signal(
                symbol=target_etf,
                quantity=quantity,
                confidence=0.7,
                reasoning=f"{reasoning}: {target_etf} 动量得分 {current_score.momentum_score if current_score else 0:.2%}",
                price=current_score.price if current_score else 100.0
            )

        # 5. 添加上下文
        output.context = AdapterContext(
            strategy_id=self.ADAPTER_ID,
            strategy_version=self.VERSION,
            job_id=context.get("job_id"),
            trace_id=context.get("trace_id"),
            total_capital=input_data.available_capital
        )

        # 6. 添加证据
        output.evidence = [
            Evidence(
                source=self.ADAPTER_ID,
                timestamp=datetime.now(timezone.utc).isoformat(),
                metadata={
                    "all_scores": [s.to_dict() for s in scores],
                    "current_position": input_data.current_position,
                    "target_etf": target_etf,
                    "signal_type": signal_type,
                    "lookback_period": input_data.lookback_period,
                    "latency_ms": int((time.time() - start_time) * 1000)
                }
            )
        ]

        # 7. 添加元数据
        output.metadata["universe"] = input_data.universe
        output.metadata["etf_info"] = {etf: ETF_UNIVERSE[etf] for etf in input_data.universe}

        return output

    def run(self, input_dict: Dict, context: Optional[Dict] = None) -> Dict:
        """标准运行接口"""
        input_data = ETFRotationInput(
            universe=input_dict.get("universe"),
            lookback_period=input_dict.get("lookback_period", 126),
            momentum_threshold=input_dict.get("momentum_threshold", 0.0),
            available_capital=input_dict.get("available_capital", 100000),
            current_position=input_dict.get("current_position"),
            current_quantity=input_dict.get("current_quantity")
        )

        output = self.execute(input_data, context)
        return output.to_dict()


# ============================================
# 便捷函数
# ============================================

def run_etf_rotation(
    universe: List[str] = None,
    current_position: str = None,
    available_capital: float = 100000
) -> Dict:
    """
    运行ETF轮动策略的便捷函数

    Example:
        result = run_etf_rotation(
            universe=["SPY", "VEA", "AGG"],
            current_position="SPY",
            available_capital=50000
        )
    """
    adapter = ETFRotationAdapter()

    return adapter.run({
        "universe": universe,
        "current_position": current_position,
        "available_capital": available_capital
    })


# ============================================
# CLI 入口
# ============================================

def main():
    """命令行入口"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="ETF轮动策略适配器")
    parser.add_argument("--universe", nargs="+", default=["SPY", "VEA", "VWO", "AGG"],
                       help="轮动ETF池")
    parser.add_argument("--current", help="当前持仓ETF")
    parser.add_argument("--capital", type=float, default=100000,
                       help="可用资金")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    result = run_etf_rotation(
        universe=args.universe,
        current_position=args.current,
        available_capital=args.capital
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"结果已保存到: {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
