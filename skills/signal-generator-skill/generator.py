"""
信号生成器
"""

import pandas as pd
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass


class SignalType(Enum):
    """信号类型"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class Signal:
    """交易信号"""
    symbol: str
    signal_type: SignalType
    strength: float  # 0-1
    confidence: float  # 0-1
    reasons: List[str]
    timestamp: pd.Timestamp
    price: float


class SignalGenerator:
    """
    交易信号生成器

    支持技术信号、基本面信号、因子信号
    """

    def __init__(self):
        self._rules = []

    async def generate(
        self,
        data: pd.DataFrame,
        symbol: str,
        rules: List[Dict],
    ) -> Optional[Signal]:
        """
        生成交易信号

        Args:
            data: 市场数据（包含价格和指标）
            symbol: 标的代码
            rules: 信号规则列表

        Returns:
            交易信号
        """
        latest = data.iloc[-1]
        current_price = latest["close"]

        buy_signals = []
        sell_signals = []
        reasons = []

        for rule in rules:
            signal = await self._apply_rule(data, rule)
            if signal == SignalType.BUY:
                buy_signals.append(signal)
                reasons.append(rule.get("reason", ""))
            elif signal == SignalType.SELL:
                sell_signals.append(signal)
                reasons.append(rule.get("reason", ""))

        # 综合判断
        if len(buy_signals) > len(sell_signals):
            return Signal(
                symbol=symbol,
                signal_type=SignalType.BUY,
                strength=min(len(buy_signals) * 0.2, 1.0),
                confidence=len(buy_signals) / (len(buy_signals) + len(sell_signals)),
                reasons=reasons,
                timestamp=data.index[-1],
                price=current_price,
            )
        elif len(sell_signals) > len(buy_signals):
            return Signal(
                symbol=symbol,
                signal_type=SignalType.SELL,
                strength=min(len(sell_signals) * 0.2, 1.0),
                confidence=len(sell_signals) / (len(buy_signals) + len(sell_signals)),
                reasons=reasons,
                timestamp=data.index[-1],
                price=current_price,
            )
        else:
            return Signal(
                symbol=symbol,
                signal_type=SignalType.HOLD,
                strength=0,
                confidence=0.5,
                reasons=["No clear signal"],
                timestamp=data.index[-1],
                price=current_price,
            )

    async def _apply_rule(self, data: pd.DataFrame, rule: Dict) -> Optional[SignalType]:
        """应用单个规则"""
        rule_type = rule["type"]

        if rule_type == "crossover":
            return await self._crossover_signal(data, rule)
        elif rule_type == "threshold":
            return await self._threshold_signal(data, rule)
        elif rule_type == "pattern":
            return await self._pattern_signal(data, rule)
        elif rule_type == "breakout":
            return await self._breakout_signal(data, rule)

        return None

    async def _crossover_signal(self, data: pd.DataFrame, rule: Dict) -> Optional[SignalType]:
        """交叉信号"""
        fast_col = rule["fast"]
        slow_col = rule["slow"]

        if fast_col not in data.columns or slow_col not in data.columns:
            return None

        latest = data.iloc[-1]
        previous = data.iloc[-2]

        # 金叉
        if previous[fast_col] <= previous[slow_col] and latest[fast_col] > latest[slow_col]:
            return SignalType.BUY
        # 死叉
        elif previous[fast_col] >= previous[slow_col] and latest[fast_col] < latest[slow_col]:
            return SignalType.SELL

        return None

    async def _threshold_signal(self, data: pd.DataFrame, rule: Dict) -> Optional[SignalType]:
        """阈值信号"""
        indicator = rule["indicator"]
        condition = rule["condition"]  # above, below
        value = rule["value"]

        if indicator not in data.columns:
            return None

        latest = data.iloc[-1][indicator]

        if condition == "below" and latest < value:
            return SignalType.BUY if rule.get("signal_when", "below") == "below" else SignalType.SELL
        elif condition == "above" and latest > value:
            return SignalType.SELL if rule.get("signal_when", "above") == "above" else SignalType.BUY

        return None

    async def _pattern_signal(self, data: pd.DataFrame, rule: Dict) -> Optional[SignalType]:
        """形态信号"""
        pattern = rule["pattern"]

        if pattern == "double_bottom":
            return await self._detect_double_bottom(data, rule)
        elif pattern == "double_top":
            return await self._detect_double_top(data, rule)
        elif pattern == "higher_highs":
            return await self._detect_higher_highs(data, rule)

        return None

    async def _detect_double_bottom(self, data: pd.DataFrame, rule: Dict) -> Optional[SignalType]:
        """检测双底"""
        lookback = rule.get("lookback", 20)

        recent_data = data.tail(lookback)
        lows = recent_data["low"]

        # 简化版：找两个相似的低点
        if len(lows) < 10:
            return None

        min1_idx = lows.argmin()
        min1_val = lows.iloc[min1_idx]

        # 在另一个区域找第二个低点
        if min1_idx < len(lows) // 2:
            remaining = lows.iloc[min1_idx + 5:]
        else:
            remaining = lows.iloc[:min1_idx - 5]

        if len(remaining) < 5:
            return None

        min2_val = remaining.min()

        # 检查两个低点是否接近
        tolerance = rule.get("tolerance", 0.02)
        if abs(min1_val - min2_val) / min1_val < tolerance:
            current_price = data.iloc[-1]["close"]
            neckline = data.iloc[min1_idx]["high"]

            # 突破颈线
            if current_price > neckline:
                return SignalType.BUY

        return None

    async def _detect_double_top(self, data: pd.DataFrame, rule: Dict) -> Optional[SignalType]:
        """检测双顶"""
        lookback = rule.get("lookback", 20)

        recent_data = data.tail(lookback)
        highs = recent_data["high"]

        if len(highs) < 10:
            return None

        max1_idx = highs.argmax()
        max1_val = highs.iloc[max1_idx]

        if max1_idx < len(highs) // 2:
            remaining = highs.iloc[max1_idx + 5:]
        else:
            remaining = highs.iloc[:max1_idx - 5]

        if len(remaining) < 5:
            return None

        max2_val = remaining.max()

        tolerance = rule.get("tolerance", 0.02)
        if abs(max1_val - max2_val) / max1_val < tolerance:
            current_price = data.iloc[-1]["close"]
            neckline = data.iloc[max1_idx]["low"]

            # 跌破颈线
            if current_price < neckline:
                return SignalType.SELL

        return None

    async def _detect_higher_highs(self, data: pd.DataFrame, rule: Dict) -> Optional[SignalType]:
        """检测更高的高点（上升趋势）"""
        lookback = rule.get("lookback", 10)

        recent_data = data.tail(lookback)
        highs = recent_data["high"]

        if len(highs) < 3:
            return None

        # 检查最近的高点是否在上升
        recent_highs = []
        for i in range(1, len(highs)):
            if i == 1 or highs.iloc[i] > highs.iloc[i-1]:
                recent_highs.append(highs.iloc[i])

        if len(recent_highs) >= 3:
            if recent_highs[-1] > recent_highs[-2] > recent_highs[-3]:
                return SignalType.BUY

        return None

    async def _breakout_signal(self, data: pd.DataFrame, rule: Dict) -> Optional[SignalType]:
        """突破信号"""
        direction = rule.get("direction", "up")  # up, down
        lookback = rule.get("lookback", 20)

        if direction == "up":
            resistance = data.tail(lookback)["high"].max()
            current_price = data.iloc[-1]["close"]

            if current_price > resistance:
                return SignalType.BUY
        else:
            support = data.tail(lookback)["low"].min()
            current_price = data.iloc[-1]["close"]

            if current_price < support:
                return SignalType.SELL

        return None

    async def generate_batch(
        self,
        data_dict: Dict[str, pd.DataFrame],
        rules: List[Dict],
    ) -> Dict[str, Signal]:
        """批量生成信号"""
        signals = {}

        for symbol, data in data_dict.items():
            signal = await self.generate(data, symbol, rules)
            if signal:
                signals[symbol] = signal

        return signals
