"""
成交量监听器 - 感知层核心组件

只记录成交量行为，不做任何判断
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class VolumeSignal:
    """成交量信号 - 只记录成交量行为"""
    signal_type = "volume"

    # 当前状态
    current_volume: int           # 当前成交量
    volume_ratio: float           # 量比（当前量/平均量）

    # 量能状态（不做判断，只记录事实）
    is_volume_surge: bool         # 是否放量
    is_volume_shrink: bool        # 是否缩量
    is_extreme_surge: bool        # 是否极端放量（2倍以上）

    # 平均成交量
    avg_volume_5: int = 0         # 5周期均量
    avg_volume_20: int = 0        # 20周期均量
    avg_volume_60: int = 0        # 60周期均量

    # 成交量趋势
    volume_trend: str = "neutral"  # 成交量趋势：increasing, decreasing, neutral

    # 量能位置
    volume_percentile: float = 0.0  # 成交量百分位（0-100）

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'signal_type': self.signal_type,
            'current_volume': self.current_volume,
            'volume_ratio': self.volume_ratio,
            'is_volume_surge': self.is_volume_surge,
            'is_volume_shrink': self.is_volume_shrink,
            'is_extreme_surge': self.is_extreme_surge,
            'avg_volume_5': self.avg_volume_5,
            'avg_volume_20': self.avg_volume_20,
            'avg_volume_60': self.avg_volume_60,
            'volume_trend': self.volume_trend,
            'volume_percentile': self.volume_percentile,
        }


class VolumeListener:
    """
    成交量监听器 - 只听不说

    职责：
    1. 记录成交量行为
    2. 检测放量/缩量
    3. 计算量比
    4. 不做任何交易决策
    """

    def __init__(
        self,
        surge_threshold: float = 1.5,    # 放量阈值（1.5倍）
        shrink_threshold: float = 0.7,   # 缩量阈值（0.7倍）
        extreme_threshold: float = 2.0,  # 极端放量阈值（2倍）
    ):
        """
        初始化成交量监听器

        Args:
            surge_threshold: 放量阈值（倍数）
            shrink_threshold: 缩量阈值（倍数）
            extreme_threshold: 极端放量阈值（倍数）
        """
        self.surge_threshold = surge_threshold
        self.shrink_threshold = shrink_threshold
        self.extreme_threshold = extreme_threshold

        # 历史数据
        self.volume_history: Dict[str, List[int]] = {}

    def listen(self, tick_data: Dict[str, Any]) -> VolumeSignal:
        """
        听市场成交量信号

        Args:
            tick_data: Tick数据
                {
                    "symbol": str,
                    "volume": int,
                    "timestamp": datetime,
                }

        Returns:
            VolumeSignal: 成交量信号（只记录，不判断）
        """
        symbol = tick_data['symbol']
        volume = tick_data.get('volume', 0)

        # 更新历史数据
        self._update_history(symbol, volume)

        # 获取历史数据
        history = self.volume_history.get(symbol, [])

        # 计算平均成交量
        avg_5 = self._calc_avg_volume(history, 5)
        avg_20 = self._calc_avg_volume(history, 20)
        avg_60 = self._calc_avg_volume(history, 60)

        # 计算量比（使用20周期平均作为基准）
        base_volume = avg_20 if avg_20 > 0 else volume
        volume_ratio = volume / base_volume if base_volume > 0 else 1.0

        # 构建成交量信号
        signal = VolumeSignal(
            current_volume=volume,
            volume_ratio=volume_ratio,
            is_volume_surge=volume_ratio >= self.surge_threshold,
            is_volume_shrink=volume_ratio <= self.shrink_threshold,
            is_extreme_surge=volume_ratio >= self.extreme_threshold,
            avg_volume_5=avg_5,
            avg_volume_20=avg_20,
            avg_volume_60=avg_60,
            volume_trend=self._detect_volume_trend(history),
            volume_percentile=self._calc_percentile(history, volume),
        )

        return signal

    def _update_history(self, symbol: str, volume: int):
        """更新历史数据"""
        if symbol not in self.volume_history:
            self.volume_history[symbol] = []

        self.volume_history[symbol].append(volume)

        # 保持历史长度合理（避免内存无限增长）
        max_history = 200  # 保留200个数据点
        if len(self.volume_history[symbol]) > max_history:
            self.volume_history[symbol] = self.volume_history[symbol][-max_history:]

    def _calc_avg_volume(self, history: List[int], period: int) -> int:
        """计算平均成交量"""
        if len(history) < 2:
            return 0

        window = min(period, len(history))
        recent_volumes = history[-window:]
        return int(sum(recent_volumes) / window)

    def _detect_volume_trend(self, history: List[int]) -> str:
        """
        检测量能趋势（不做判断，只记录）

        Returns:
            "increasing", "decreasing", or "neutral"
        """
        if len(history) < 10:
            return "neutral"

        # 比较近期和远期平均成交量
        recent_avg = self._calc_avg_volume(history, 5)
        distant_avg = self._calc_avg_volume(history, 10)

        if distant_avg == 0:
            return "neutral"

        diff_pct = (recent_avg - distant_avg) / distant_avg

        if diff_pct > 0.2:  # 近期比远期高20%以上
            return "increasing"
        elif diff_pct < -0.2:  # 近期比远期低20%以上
            return "decreasing"
        else:
            return "neutral"

    def _calc_percentile(self, history: List[int], current_volume: int) -> float:
        """
        计算当前成交量在历史中的百分位

        Returns:
            0-100之间的数值
        """
        if len(history) < 2:
            return 50.0

        # 统计比当前成交量小的数量
        smaller_count = sum(1 for v in history if v < current_volume)
        percentile = (smaller_count / len(history)) * 100

        return round(percentile, 2)

    def reset(self, symbol: Optional[str] = None):
        """
        重置历史数据

        Args:
            symbol: 如果指定，只重置该股票；否则重置所有
        """
        if symbol:
            self.volume_history.pop(symbol, None)
        else:
            self.volume_history.clear()

    def get_history_length(self, symbol: str) -> int:
        """获取某股票的历史数据长度"""
        return len(self.volume_history.get(symbol, []))
