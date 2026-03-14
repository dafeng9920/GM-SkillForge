"""
多因子动量策略 - Multi-Factor Momentum Strategy

结合多个技术因子进行股票选择和交易信号生成
策略类型: 中长期趋势跟踪
风险等级: 中等

因子组成:
1. 价格动量因子 (Price Momentum) - 12个月收益率
2. 波动率因子 (Volatility) - 20日波动率
3. 成交量因子 (Volume) - 成交量变化率
4. 相对强弱因子 (Relative Strength) - RSI

版本: 1.0.0
创建日期: 2026-03-09
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


# ============================================
# 数据模型
# ============================================

@dataclass
class MarketData:
    """市场数据"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    # 历史数据用于计算因子
    historical_closes: List[float] = field(default_factory=list)
    historical_volumes: List[float] = field(default_factory=list)


@dataclass
class FactorScore:
    """因子得分"""
    symbol: str
    momentum_score: float      # 动量得分 (-1 到 1)
    volatility_score: float    # 波动率得分 (-1 到 1)
    volume_score: float        # 成交量得分 (-1 到 1)
    rsi_score: float           # RSI得分 (-1 到 1)
    composite_score: float     # 综合得分

    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "momentum_score": round(self.momentum_score, 3),
            "volatility_score": round(self.volatility_score, 3),
            "volume_score": round(self.volume_score, 3),
            "rsi_score": round(self.rsi_score, 3),
            "composite_score": round(self.composite_score, 3)
        }


@dataclass
class TradingSignal:
    """交易信号"""
    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float  # 0 到 1
    target_price: Optional[float]
    stop_loss: Optional[float]
    position_size: float  # 建议仓位比例 (0 到 1)
    reasoning: str
    factors: Dict[str, float]
    timestamp: datetime


# ============================================
# 策略配置
# ============================================

@dataclass
class StrategyConfig:
    """策略配置"""
    # 因子权重
    momentum_weight: float = 0.4
    volatility_weight: float = 0.2
    volume_weight: float = 0.2
    rsi_weight: float = 0.2

    # 阈值
    min_composite_score: float = 0.3    # 最小综合得分买入阈值
    max_composite_score: float = -0.3   # 最大综合得分卖出阈值
    min_confidence: float = 0.6         # 最小置信度

    # 仓位管理
    max_position_size: float = 0.3      # 单个股票最大仓位
    base_position_size: float = 0.1     # 基础仓位

    # 风险管理
    stop_loss_pct: float = 0.05         # 5% 止损
    take_profit_pct: float = 0.15       # 15% 止盈


# ============================================
# 多因子动量策略
# ============================================

class MultiFactorMomentumStrategy:
    """
    多因子动量策略

    核心逻辑:
    1. 计算多个技术因子得分
    2. 加权综合得到因子得分
    3. 根据综合得分生成交易信号
    4. 动态调整仓位
    """

    def __init__(self, config: Optional[StrategyConfig] = None):
        self.config = config or StrategyConfig()
        self.historical_data: Dict[str, List[MarketData]] = {}

    def _calculate_momentum_score(self, data: MarketData) -> float:
        """
        计算动量因子得分

        使用12个月收益率作为动量指标
        得分归一化到 [-1, 1]
        """
        if len(data.historical_closes) < 20:
            return 0.0

        # 计算最近20日的收益率
        recent_closes = data.historical_closes[-20:]
        momentum = (recent_closes[-1] - recent_closes[0]) / recent_closes[0]

        # 归一化到 [-1, 1]
        # 假设正常范围是 -20% 到 +20%
        normalized = np.clip(momentum / 0.2, -1, 1)
        return float(normalized)

    def _calculate_volatility_score(self, data: MarketData) -> float:
        """
        计算波动率因子得分

        使用20日标准差作为波动率指标
        低波动率给予正分（稳定性好）
        """
        if len(data.historical_closes) < 20:
            return 0.0

        # 计算收益率
        returns = pd.Series(data.historical_closes[-20:]).pct_change().dropna()

        # 计算年化波动率
        volatility = returns.std() * np.sqrt(252)

        # 归一化到 [-1, 1]
        # 假设正常范围是 10% 到 60%
        # 低波动率得分高
        normalized = -np.clip((volatility - 0.1) / 0.5, -1, 1)
        return float(normalized)

    def _calculate_volume_score(self, data: MarketData) -> float:
        """
        计算成交量因子得分

        比较当前成交量与平均成交量
        放量且价格上涨给予正分
        """
        if len(data.historical_volumes) < 20:
            return 0.0

        # 计算平均成交量
        avg_volume = np.mean(data.historical_volumes[-20:])

        # 计算成交量比率
        volume_ratio = data.volume / avg_volume if avg_volume > 0 else 1

        # 计算价格变化
        if len(data.historical_closes) >= 2:
            price_change = (data.close - data.historical_closes[-2]) / data.historical_closes[-2]
        else:
            price_change = 0

        # 放量上涨得高分
        # 成交量比率 * 价格变化方向
        score = (volume_ratio - 1) * np.sign(price_change)

        # 归一化到 [-1, 1]
        normalized = np.clip(score / 2, -1, 1)
        return float(normalized)

    def _calculate_rsi_score(self, data: MarketData) -> float:
        """
        计算RSI因子得分

        RSI在40-60之间给予正分（中性区域）
        RSI > 70 给予负分（超买）
        RSI < 30 给予正分后逐步减分（超卖反弹）
        """
        if len(data.historical_closes) < 14:
            return 0.0

        # 计算RSI（使用标准方法）
        closes = np.array(data.historical_closes[-14:])
        deltas = np.diff(closes)

        # 分离涨跌
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        # 计算平均涨跌（使用简单平均）
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)

        # 避免除零
        if avg_loss == 0:
            rsi_value = 100
        else:
            rs = avg_gain / avg_loss
            rsi_value = 100 - (100 / (1 + rs))

        # 归一化到 [-1, 1]
        # RSI 50 得分 0（中性）
        # RSI 70+ 得分 -1（超买）
        # RSI 30- 得分 1（超卖）
        if rsi_value >= 50:
            normalized = -np.clip((rsi_value - 50) / 20, 0, 1)
        else:
            normalized = np.clip((50 - rsi_value) / 20, 0, 1)

        return float(normalized)

    def _calculate_composite_score(
        self,
        momentum: float,
        volatility: float,
        volume: float,
        rsi: float
    ) -> float:
        """计算综合得分"""
        composite = (
            momentum * self.config.momentum_weight +
            volatility * self.config.volatility_weight +
            volume * self.config.volume_weight +
            rsi * self.config.rsi_weight
        )
        return composite

    def _calculate_position_size(self, composite_score: float) -> float:
        """
        根据综合得分计算仓位大小

        得分越高，仓位越大
        """
        # 基础仓位 + 得分加成
        score_adjustment = abs(composite_score) * self.config.base_position_size

        if composite_score > 0:
            position_size = min(
                self.config.base_position_size + score_adjustment,
                self.config.max_position_size
            )
        else:
            position_size = self.config.base_position_size * 0.5

        return position_size

    def _calculate_confidence(self, score: FactorScore) -> float:
        """
        计算信号置信度

        基于因子的离散程度和综合得分
        """
        # 因子绝对值的平均值（离散程度）
        factor_values = [
            abs(score.momentum_score),
            abs(score.volatility_score),
            abs(score.volume_score),
            abs(score.rsi_score)
        ]

        avg_dispersion = np.mean(factor_values)

        # 综合得分越高，置信度越高
        confidence = min(0.9, 0.5 + abs(score.composite_score) * 0.3 + avg_dispersion * 0.2)

        return confidence

    def calculate_factor_score(self, data: MarketData) -> FactorScore:
        """计算因子得分"""
        momentum = self._calculate_momentum_score(data)
        volatility = self._calculate_volatility_score(data)
        volume = self._calculate_volume_score(data)
        rsi = self._calculate_rsi_score(data)
        composite = self._calculate_composite_score(momentum, volatility, volume, rsi)

        return FactorScore(
            symbol=data.symbol,
            momentum_score=momentum,
            volatility_score=volatility,
            volume_score=volume,
            rsi_score=rsi,
            composite_score=composite
        )

    def generate_signal(self, data: MarketData) -> TradingSignal:
        """生成交易信号"""
        # 1. 计算因子得分
        score = self.calculate_factor_score(data)

        # 2. 计算置信度
        confidence = self._calculate_confidence(score)

        # 3. 确定交易动作
        if score.composite_score >= self.config.min_composite_score and confidence >= self.config.min_confidence:
            action = "BUY"

            # 生成详细的买入理由
            strong_factors = []
            if score.momentum_score > 0.3:
                strong_factors.append(f"动量强劲({score.momentum_score:.2f})")
            if score.volume_score > 0.3:
                strong_factors.append(f"资金流入({score.volume_score:.2f})")
            if score.rsi_score > 0.2:
                strong_factors.append(f"RSI健康({score.rsi_score:.2f})")
            if score.volatility_score > 0:
                strong_factors.append(f"波动适度({score.volatility_score:.2f})")

            factors_desc = "、".join(strong_factors) if strong_factors else "多指标向好"
            reasoning = f"{factors_desc}，综合得分{score.composite_score:.2f}，置信度{confidence:.0%}"

            target_price = data.close * (1 + self.config.take_profit_pct)
            stop_loss = data.close * (1 - self.config.stop_loss_pct)
        elif score.composite_score <= self.config.max_composite_score:
            action = "SELL"

            # 生成详细的卖出理由
            weak_factors = []
            if score.momentum_score < -0.3:
                weak_factors.append(f"动量疲弱({score.momentum_score:.2f})")
            if score.volume_score < -0.2:
                weak_factors.append(f"资金流出({score.volume_score:.2f})")
            if score.rsi_score < -0.2:
                weak_factors.append(f"RSI超买回落({score.rsi_score:.2f})")

            factors_desc = "、".join(weak_factors) if weak_factors else "多指标转弱"
            reasoning = f"{factors_desc}，综合得分{score.composite_score:.2f}，触发卖出"

            target_price = None
            stop_loss = None
        else:
            action = "HOLD"
            reasoning = f"综合得分 {score.composite_score:.2f} 未达到交易阈值"
            target_price = None
            stop_loss = None

        # 4. 计算仓位大小
        position_size = self._calculate_position_size(score.composite_score)

        # 5. 构建信号
        return TradingSignal(
            symbol=data.symbol,
            action=action,
            confidence=confidence,
            target_price=target_price,
            stop_loss=stop_loss,
            position_size=position_size,
            reasoning=reasoning,
            factors={
                "momentum": score.momentum_score,
                "volatility": score.volatility_score,
                "volume": score.volume_score,
                "rsi": score.rsi_score,
                "composite": score.composite_score
            },
            timestamp=data.timestamp
        )

    def update_market_data(self, data: MarketData):
        """更新市场数据"""
        if data.symbol not in self.historical_data:
            self.historical_data[data.symbol] = []

        self.historical_data[data.symbol].append(data)

        # 保持历史数据长度
        max_length = 300  # 保留约300个数据点
        if len(self.historical_data[data.symbol]) > max_length:
            self.historical_data[data.symbol] = self.historical_data[data.symbol][-max_length:]

    def get_enriched_data(self, symbol: str, current_data: MarketData) -> MarketData:
        """获取包含历史数据的市场数据"""
        if symbol in self.historical_data and len(self.historical_data[symbol]) > 0:
            historical = self.historical_data[symbol]
            closes = [d.close for d in historical]
            volumes = [d.volume for d in historical]

            enriched = MarketData(
                symbol=current_data.symbol,
                timestamp=current_data.timestamp,
                open=current_data.open,
                high=current_data.high,
                low=current_data.low,
                close=current_data.close,
                volume=current_data.volume,
                historical_closes=closes + [current_data.close],
                historical_volumes=volumes + [current_data.volume]
            )
            return enriched
        else:
            return current_data

    def process_tick(self, tick_data: MarketData) -> TradingSignal:
        """处理实时tick数据"""
        # 更新历史数据
        self.update_market_data(tick_data)

        # 获取 enriched 数据
        enriched = self.get_enriched_data(tick_data.symbol, tick_data)

        # 生成信号
        return self.generate_signal(enriched)


# ============================================
# 辅助函数
# ============================================

def create_mock_data(
    symbol: str,
    days: int = 100,
    start_price: float = 100.0,
    trend: float = 0.0001,
    volatility: float = 0.02,
    seed: int = 42
) -> List[MarketData]:
    """创建模拟数据"""
    import random
    np.random.seed(seed)
    random.seed(seed)

    data = []
    current_price = start_price
    start_date = datetime.now() - timedelta(days=days)

    for i in range(days):
        # 随机游走
        change = random.gauss(trend, volatility / np.sqrt(252)) * current_price
        current_price = max(current_price + change, 1.0)

        # 生成日内数据
        high = current_price * random.uniform(1.0, 1.02)
        low = current_price * random.uniform(0.98, 1.0)
        open_price = random.uniform(low, high)
        close = current_price
        volume = random.gauss(1000000, 200000)

        data.append(MarketData(
            symbol=symbol,
            timestamp=start_date + timedelta(days=i),
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=max(volume, 0)
        ))

    return data


# ============================================
# CLI 入口
# ============================================

def print_signal_card(signal: TradingSignal, price: float, width: int = 60):
    """打印精美的信号卡片"""
    # 根据动作选择图标
    icons = {"BUY": "🟢", "SELL": "🔴", "HOLD": "⚪"}
    icon = icons.get(signal.action, "❓")

    print(f"\n{icon} {signal.symbol}")
    print("─" * width)
    print(f"价格: ${price:.2f} | 信号: {signal.action:4} | 置信度: {signal.confidence:.0%}")
    print("─" * width)

    # 因子条形图
    factors = [
        ("动量", signal.factors['momentum']),
        ("波动", signal.factors['volatility']),
        ("成交", signal.factors['volume']),
        ("RSI", signal.factors['rsi']),
    ]
    for name, score in factors:
        bar_len = int(abs(score) * 20)
        bar = "█" * bar_len
        sign = "+" if score > 0 else ""
        print(f"  {name:4} │{sign}{score:.2f}│ {bar}")

    print("─" * width)
    print(f"综合: {signal.factors['composite']:+.2f} │ 仓位: {signal.position_size:.0%}")

    if signal.action != "HOLD":
        if signal.target_price:
            print(f"目标: ${signal.target_price:.2f} │ ", end="")
        if signal.stop_loss:
            print(f"止损: ${signal.stop_loss:.2f}")
    print(f"理由: {signal.reasoning}")


def main():
    """命令行入口"""
    print("=" * 70)
    print("  多因子动量策略演示 - Multi-Factor Momentum Strategy")
    print("=" * 70)

    # 创建策略配置（激进模式，更容易产生信号）
    config = StrategyConfig(
        momentum_weight=0.5,      # 提高动量权重
        volatility_weight=0.2,
        volume_weight=0.15,
        rsi_weight=0.15,          # 降低RSI权重（避免超买信号抵消动量）
        min_composite_score=0.15, # 降低买入阈值
        max_composite_score=-0.15,
        min_confidence=0.55,      # 降低置信度阈值
        max_position_size=0.25,
        base_position_size=0.12,
        stop_loss_pct=0.08,
        take_profit_pct=0.20
    )

    strategy = MultiFactorMomentumStrategy(config=config)

    # 创建多个场景
    print("\n📊 生成4种市场场景...")

    scenarios = []

    # 场景1: 强势上涨（应该买入）
    print("\n  场景1: 强势上涨趋势")
    bull_data = create_mock_data("NVDA", days=120, start_price=100.0, trend=0.008, volatility=0.02, seed=888)
    for data in bull_data[:-1]:
        strategy.update_market_data(data)
    signal1 = strategy.process_tick(bull_data[-1])
    scenarios.append((bull_data[-1], signal1, "强势上涨"))

    # 重置策略
    strategy = MultiFactorMomentumStrategy(config=config)

    # 场景2: 弱势下跌（应该卖出）
    print("  场景2: 持续下跌")
    bear_data = create_mock_data("MSTR", days=120, start_price=100.0, trend=-0.005, volatility=0.03, seed=999)
    for data in bear_data[:-1]:
        strategy.update_market_data(data)
    signal2 = strategy.process_tick(bear_data[-1])
    scenarios.append((bear_data[-1], signal2, "持续下跌"))

    # 重置策略
    strategy = MultiFactorMomentumStrategy(config=config)

    # 场景3: 震荡后突破（应该买入）
    print("  场景3: 震荡后突破")
    break_data = create_mock_data("TSLA", days=120, start_price=100.0, trend=0.005, volatility=0.012, seed=777)
    for data in break_data[:-1]:
        strategy.update_market_data(data)
    signal3 = strategy.process_tick(break_data[-1])
    scenarios.append((break_data[-1], signal3, "震荡突破"))

    # 重置策略
    strategy = MultiFactorMomentumStrategy(config=config)

    # 场景4: 震荡盘整（应该观望）
    print("  场景4: 震荡盘整")
    chop_data = create_mock_data("AAPL", days=120, start_price=100.0, trend=0.001, volatility=0.008, seed=666)
    for data in chop_data[:-1]:
        strategy.update_market_data(data)
    signal4 = strategy.process_tick(chop_data[-1])
    scenarios.append((chop_data[-1], signal4, "震荡盘整"))

    # 打印结果
    print("\n" + "=" * 70)
    print("  策略分析结果")
    print("=" * 70)

    for data, signal, desc in scenarios:
        print_signal_card(signal, data.close)

    # 统计汇总
    print("\n" + "=" * 70)
    print("  信号汇总")
    print("=" * 70)

    actions = [s.action for _, s, _ in scenarios]
    buy_count = actions.count("BUY")
    sell_count = actions.count("SELL")
    hold_count = actions.count("HOLD")

    print(f"  买入信号: {buy_count} │ 卖出信号: {sell_count} │ 观望: {hold_count}")

    avg_confidence = sum(s.confidence for _, s, _ in scenarios) / len(scenarios)
    print(f"  平均置信度: {avg_confidence:.1%}")

    # 策略逻辑说明
    print("\n" + "=" * 70)
    print("  策略逻辑说明")
    print("=" * 70)
    print("""
  📈 综合得分 = 0.5×动量 + 0.2×波动率 + 0.15×成交量 + 0.15×RSI

  买入条件:
    • 综合得分 ≥ 0.15
    • 置信度 ≥ 55%

  卖出条件:
    • 综合得分 ≤ -0.15

  风险控制:
    • 止损: -8%
    • 止盈: +20%
    • 单股最大仓位: 25%
    """)

    print("=" * 70)


if __name__ == "__main__":
    main()
