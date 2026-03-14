"""
价格监听器 - 感知层核心组件

只记录价格行为，不做任何判断
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class PriceSignal:
    """价格信号 - 只记录价格行为，不做判断"""
    signal_type = "price"

    # 当前状态
    current_price: float          # 当前价格
    price_change: float           # 价格变动
    change_pct: float             # 价格变动百分比

    # 突破信号（不做判断，只记录事实）
    is_breakout_up: bool          # 是否向上突破阻力位
    is_breakout_down: bool        # 是否向下突破支撑位
    is_new_high: bool             # 是否创新高
    is_new_low: bool              # 是否创新低

    # 关键位置
    resistance_level: Optional[float] = None  # 阻力位
    support_level: Optional[float] = None     # 支撑位
    recent_high: Optional[float] = None       # 最近高点
    recent_low: Optional[float] = None        # 最近低点

    # 波动率
    volatility: float = 0.0       # 波动率

    # 趋势
    trend: str = "neutral"        # 趋势：up, down, neutral

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'signal_type': self.signal_type,
            'current_price': self.current_price,
            'price_change': self.price_change,
            'change_pct': self.change_pct,
            'is_breakout_up': self.is_breakout_up,
            'is_breakout_down': self.is_breakout_down,
            'is_new_high': self.is_new_high,
            'is_new_low': self.is_new_low,
            'resistance_level': self.resistance_level,
            'support_level': self.support_level,
            'recent_high': self.recent_high,
            'recent_low': self.recent_low,
            'volatility': self.volatility,
            'trend': self.trend,
        }


class PriceListener:
    """
    价格监听器 - 只听不说

    职责：
    1. 记录价格行为
    2. 检测突破/跌破
    3. 计算波动率
    4. 不做任何交易决策
    """

    def __init__(
        self,
        lookback_period: int = 20,    # 回看周期
        volatility_window: int = 20,  # 波动率计算窗口
    ):
        """
        初始化价格监听器

        Args:
            lookback_period: 回看周期（用于计算支撑阻力位）
            volatility_window: 波动率计算窗口
        """
        self.lookback_period = lookback_period
        self.volatility_window = volatility_window

        # 历史数据
        self.price_history: Dict[str, List[float]] = {}

    def listen(self, tick_data: Dict[str, Any]) -> PriceSignal:
        """
        听市场价格信号

        Args:
            tick_data: Tick数据
                {
                    "symbol": str,
                    "price": float,
                    "timestamp": datetime,
                }

        Returns:
            PriceSignal: 价格信号（只记录，不判断）
        """
        symbol = tick_data['symbol']
        price = tick_data['price']

        # 更新历史数据
        self._update_history(symbol, price)

        # 获取历史数据
        history = self.price_history.get(symbol, [])

        # 构建价格信号
        signal = PriceSignal(
            current_price=price,
            price_change=self._calc_price_change(history),
            change_pct=self._calc_change_pct(history),
            is_breakout_up=False,
            is_breakout_down=False,
            is_new_high=False,
            is_new_low=False,
            volatility=self._calc_volatility(history),
            trend=self._detect_trend(history),
        )

        # 如果有足够历史数据，检测突破
        if len(history) >= self.lookback_period:
            # 计算关键位置
            lookback_prices = history[-self.lookback_period:]
            signal.recent_high = max(lookback_prices)
            signal.recent_low = min(lookback_prices)

            # 检测突破
            signal.is_breakout_up = price > signal.recent_high
            signal.is_breakout_down = price < signal.recent_low

            # 检测新高新低
            signal.is_new_high = price == max(history)
            signal.is_new_low = price == min(history)

        return signal

    def _update_history(self, symbol: str, price: float):
        """更新历史数据"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []

        self.price_history[symbol].append(price)

        # 保持历史长度合理（避免内存无限增长）
        max_history = max(self.lookback_period, self.volatility_window) * 2
        if len(self.price_history[symbol]) > max_history:
            self.price_history[symbol] = self.price_history[symbol][-max_history:]

    def _calc_price_change(self, history: List[float]) -> float:
        """计算价格变动"""
        if len(history) < 2:
            return 0.0
        return history[-1] - history[-2]

    def _calc_change_pct(self, history: List[float]) -> float:
        """计算价格变动百分比"""
        if len(history) < 2:
            return 0.0
        if history[-2] == 0:
            return 0.0
        return (history[-1] - history[-2]) / history[-2]

    def _calc_volatility(self, history: List[float]) -> float:
        """计算波动率（标准差）"""
        if len(history) < self.volatility_window:
            return 0.0

        window = min(len(history), self.volatility_window)
        recent_prices = history[-window:]

        # 计算收益率
        returns = []
        for i in range(1, len(recent_prices)):
            if recent_prices[i-1] > 0:
                ret = (recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1]
                returns.append(ret)

        if not returns:
            return 0.0

        # 计算标准差
        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / len(returns)
        return variance ** 0.5

    def _detect_trend(self, history: List[float]) -> str:
        """
        检测趋势（不做判断，只记录）

        Returns:
            "up", "down", or "neutral"
        """
        if len(history) < 5:
            return "neutral"

        # 使用简单移动平均判断趋势
        short_ma = sum(history[-5:]) / 5
        long_ma = sum(history[-min(20, len(history)):]) / min(20, len(history))

        diff_pct = (short_ma - long_ma) / long_ma if long_ma > 0 else 0

        if diff_pct > 0.01:  # 短期MA比长期MA高1%以上
            return "up"
        elif diff_pct < -0.01:  # 短期MA比长期MA低1%以上
            return "down"
        else:
            return "neutral"

    def reset(self, symbol: Optional[str] = None):
        """
        重置历史数据

        Args:
            symbol: 如果指定，只重置该股票；否则重置所有
        """
        if symbol:
            self.price_history.pop(symbol, None)
        else:
            self.price_history.clear()

    def get_history_length(self, symbol: str) -> int:
        """获取某股票的历史数据长度"""
        return len(self.price_history.get(symbol, []))
