"""
盘口情绪监听器 - 感知层核心组件

只记录盘口情绪状态，不做任何判断
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class SentimentSignal:
    """盘口情绪信号 - 只记录盘口状态"""
    signal_type = "sentiment"

    # 盘口数据（不做判断，只记录事实）
    bid_volume: int               # 买盘量
    ask_volume: int               # 卖盘量
    bid_ask_ratio: float          # 买卖比
    spread: float                 # 买卖价差（元）
    spread_pct: float             # 买卖价差（百分比）

    # 盘口状态
    is_bid_dominant: bool         # 买盘占优
    is_ask_dominant: bool         # 卖盘占优
    is_balanced: bool             # 买卖平衡

    # 订单簿不平衡度
    order_book_imbalance: float   # -1(完全卖) 到 +1(完全买)

    # 盘口情绪
    sentiment: str = "neutral"    # 盘口情绪：bullish, bearish, neutral

    # 压力状态
    pressure_side: str = "neutral"  # 压力方向：buy, sell, neutral

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'signal_type': self.signal_type,
            'bid_volume': self.bid_volume,
            'ask_volume': self.ask_volume,
            'bid_ask_ratio': self.bid_ask_ratio,
            'spread': self.spread,
            'spread_pct': self.spread_pct,
            'is_bid_dominant': self.is_bid_dominant,
            'is_ask_dominant': self.is_ask_dominant,
            'is_balanced': self.is_balanced,
            'order_book_imbalance': self.order_book_imbalance,
            'sentiment': self.sentiment,
            'pressure_side': self.pressure_side,
        }


class SentimentListener:
    """
    盘口情绪监听器 - 只听不说

    职责：
    1. 记录盘口情绪状态
    2. 检测买卖盘力量对比
    3. 计算订单簿不平衡度
    4. 不做任何交易决策
    """

    def __init__(
        self,
        imbalance_threshold: float = 0.3,   # 不平衡阈值
        balanced_range: float = 0.2,         # 平衡范围（±20%）
    ):
        """
        初始化盘口情绪监听器

        Args:
            imbalance_threshold: 不平衡阈值（超出此值视为明显不平衡）
            balanced_range: 平衡范围（买卖比在此范围内视为平衡）
        """
        self.imbalance_threshold = imbalance_threshold
        self.balanced_range = balanced_range

        # 历史数据
        self.sentiment_history: Dict[str, deque] = {}

    def listen(self, tick_data: Dict[str, Any]) -> SentimentSignal:
        """
        听市场盘口情绪信号

        Args:
            tick_data: Tick数据
                {
                    "symbol": str,
                    "bid": float,          # 买一价
                    "ask": float,          # 卖一价
                    "bid_size": int,       # 买一量
                    "ask_size": int,       # 卖一量
                    # 可选（五档盘口）
                    "bid_levels": List[float],    # 买档价格
                    "ask_levels": List[float],    # 卖档价格
                    "bid_sizes": List[int],       # 买档量
                    "ask_sizes": List[int],       # 卖档量
                }

        Returns:
            SentimentSignal: 盘口情绪信号（只记录，不判断）
        """
        symbol = tick_data['symbol']

        # 提取盘口数据
        bid_price = tick_data.get('bid', 0)
        ask_price = tick_data.get('ask', 0)
        bid_size = tick_data.get('bid_size', 0)
        ask_size = tick_data.get('ask_size', 0)

        # 计算买卖盘总量（如果有五档数据）
        if 'bid_sizes' in tick_data and 'ask_sizes' in tick_data:
            total_bid = sum(tick_data['bid_sizes'])
            total_ask = sum(tick_data['ask_sizes'])
        else:
            total_bid = bid_size
            total_ask = ask_size

        # 计算买卖比
        total_size = total_bid + total_ask
        if total_size > 0:
            bid_ask_ratio = total_bid / total_ask if total_ask > 0 else 1.0
        else:
            bid_ask_ratio = 1.0

        # 计算价差
        spread = ask_price - bid_price
        spread_pct = spread / bid_price if bid_price > 0 else 0

        # 计算订单簿不平衡度
        imbalance = self._calculate_imbalance(total_bid, total_ask)

        # 更新历史数据
        self._update_history(symbol, imbalance)

        # 获取历史数据
        history = list(self.sentiment_history.get(symbol, deque(maxlen=10)))

        # 构建盘口情绪信号
        signal = SentimentSignal(
            bid_volume=total_bid,
            ask_volume=total_ask,
            bid_ask_ratio=bid_ask_ratio,
            spread=spread,
            spread_pct=spread_pct,
            is_bid_dominant=bid_ask_ratio > (1 + self.balanced_range),
            is_ask_dominant=bid_ask_ratio < (1 - self.balanced_range),
            is_balanced=abs(bid_ask_ratio - 1) <= self.balanced_range,
            order_book_imbalance=imbalance,
            sentiment=self._classify_sentiment(bid_ask_ratio, imbalance),
            pressure_side=self._detect_pressure_side(history),
        )

        return signal

    def _calculate_imbalance(self, bid: int, ask: int) -> float:
        """
        计算订单簿不平衡度

        Returns:
            -1 (完全卖) 到 +1 (完全买)
            0 表示完全平衡
        """
        total = bid + ask
        if total == 0:
            return 0.0

        # 不平衡度：(买 - 卖) / 总量
        imbalance = (bid - ask) / total
        return round(imbalance, 4)

    def _classify_sentiment(self, ratio: float, imbalance: float) -> str:
        """
        分类盘口情绪（不做判断，只记录）

        Args:
            ratio: 买卖比
            imbalance: 不平衡度

        Returns:
            "bullish", "bearish", or "neutral"
        """
        # 根据不平衡度判断
        if imbalance > self.imbalance_threshold:
            return "bullish"
        elif imbalance < -self.imbalance_threshold:
            return "bearish"
        else:
            return "neutral"

    def _detect_pressure_side(self, history: List[float]) -> str:
        """
        检测压力方向

        Returns:
            "buy", "sell", or "neutral"
        """
        if len(history) < 5:
            return "neutral"

        # 计算最近的不平衡度平均值
        avg_imbalance = sum(history[-5:]) / 5

        if avg_imbalance > 0.2:
            return "buy"
        elif avg_imbalance < -0.2:
            return "sell"
        else:
            return "neutral"

    def _update_history(self, symbol: str, imbalance: float):
        """更新历史数据"""
        if symbol not in self.sentiment_history:
            self.sentiment_history[symbol] = deque(maxlen=10)

        self.sentiment_history[symbol].append(imbalance)

    def reset(self, symbol: Optional[str] = None):
        """
        重置历史数据

        Args:
            symbol: 如果指定，只重置该股票；否则重置所有
        """
        if symbol:
            self.sentiment_history.pop(symbol, None)
        else:
            self.sentiment_history.clear()

    def get_history_length(self, symbol: str) -> int:
        """获取某股票的历史数据长度"""
        return len(self.sentiment_history.get(symbol, []))
