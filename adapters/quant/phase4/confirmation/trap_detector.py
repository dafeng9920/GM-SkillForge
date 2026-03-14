"""
诱多检测器 - 确认层核心组件

识别假突破、诱多陷阱，保护系统避免被套
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from collections import deque
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class TrapSignal:
    """诱多信号"""
    is_trap: bool                 # 是否是诱多
    trap_type: str = ""           # 诱多类型
    confidence: float = 0.0       # 置信度
    reason: str = ""              # 原因

    def to_dict(self) -> Dict[str, Any]:
        return {
            'is_trap': self.is_trap,
            'trap_type': self.trap_type,
            'confidence': self.confidence,
            'reason': self.reason,
        }


@dataclass
class TrapDetectorConfig:
    """诱多检测配置"""
    # 快速回落检测
    pullback_threshold: float = 0.01   # 回落阈值（1%）
    pullback_window: int = 3           # 回落检测窗口（tick数）

    # 放量滞涨检测
    stagnation_volume_ratio: float = 1.5  # 放量倍数
    stagnation_price_move: float = 0.005  # 价格变动阈值（0.5%）

    # 资金背离检测
    divergence_threshold: float = 0.3    # 背离阈值

    # 假突破检测
    fake_breakout_threshold: float = 0.02  # 假突破阈值（2%）


class TrapDetector:
    """
    诱多检测器 - 保护系统避免被套

    检测类型：
    1. 快速回落：突破后迅速回落
    2. 放量滞涨：放量不涨
    3. 资金背离：价格涨但资金流出
    4. 假突破：突破后立即跌破
    """

    def __init__(self, config: Optional[TrapDetectorConfig] = None):
        """
        初始化诱多检测器

        Args:
            config: 检测配置
        """
        self.config = config or TrapDetectorConfig()

        # 历史数据
        self.price_history: Dict[str, deque] = {}
        self.volume_history: Dict[str, deque] = {}
        self.money_flow_history: Dict[str, deque] = {}

        # 突破记录
        self.breakouts: Dict[str, Dict] = {}

    def detect(
        self,
        symbol: str,
        tick_data: Dict[str, Any],
        raw_signals: Dict[str, Any],
    ) -> TrapSignal:
        """
        检测是否是诱多

        Args:
            symbol: 标的代码
            tick_data: 当前tick数据
            raw_signals: 感知层原始信号

        Returns:
            TrapSignal: 诱多检测结果
        """
        # 更新历史数据
        self._update_history(symbol, tick_data)

        # 计算诱多分数
        trap_score = 0
        trap_reasons = []

        # 1. 快速回落检测
        if self._is_quick_pullback(symbol, tick_data):
            trap_score += 2
            trap_reasons.append("快速回落")

        # 2. 放量滞涨检测
        if self._is_volume_stagnation(symbol, raw_signals):
            trap_score += 1
            trap_reasons.append("放量滞涨")

        # 3. 资金背离检测
        if self._is_money_divergence(symbol, raw_signals):
            trap_score += 2
            trap_reasons.append("资金背离")

        # 4. 假突破检测
        if self._is_fake_breakout(symbol, tick_data):
            trap_score += 3
            trap_reasons.append("假突破")

        # 判断是否是诱多
        is_trap = trap_score >= 2
        confidence = min(trap_score / 6, 1.0)  # 最高6分

        # 确定诱多类型
        trap_type = self._classify_trap_type(trap_reasons)

        return TrapSignal(
            is_trap=is_trap,
            trap_type=trap_type,
            confidence=confidence,
            reason="; ".join(trap_reasons) if trap_reasons else "未检测到诱多",
        )

    def _update_history(self, symbol: str, tick_data: Dict[str, Any]):
        """更新历史数据"""
        price = tick_data.get('price', 0)
        volume = tick_data.get('volume', 0)

        # 价格历史
        if symbol not in self.price_history:
            self.price_history[symbol] = deque(maxlen=20)
        self.price_history[symbol].append(price)

        # 成交量历史
        if symbol not in self.volume_history:
            self.volume_history[symbol] = deque(maxlen=20)
        self.volume_history[symbol].append(volume)

    def _is_quick_pullback(self, symbol: str, tick_data: Dict[str, Any]) -> bool:
        """
        检测快速回落

        特征：突破后迅速回落到突破位以下
        """
        # 检查是否有突破记录
        if symbol not in self.breakouts:
            return False

        breakout = self.breakouts[symbol]
        if not breakout.get('is_breakout', False):
            return False

        # 检查是否在突破后快速回落
        current_price = tick_data.get('price', 0)
        breakout_price = breakout.get('price', 0)

        # 价格回落超过阈值
        if current_price < breakout_price * (1 - self.config.pullback_threshold):
            return True

        return False

    def _is_volume_stagnation(self, symbol: str, raw_signals: Dict[str, Any]) -> bool:
        """
        检测放量滞涨

        特征：成交量放大但价格不涨
        """
        # 检查是否有放量信号
        volume_signal = raw_signals.get('volume', {})
        if not volume_signal.get('is_volume_surge', False):
            return False

        # 检查价格变动
        price_signal = raw_signals.get('price', {})
        price_change_pct = price_signal.get('change_pct', 0)

        # 放量但价格变动小于阈值
        if abs(price_change_pct) < self.config.stagnation_price_move:
            return True

        return False

    def _is_money_divergence(self, symbol: str, raw_signals: Dict[str, Any]) -> bool:
        """
        检测资金背离

        特征：价格上涨但资金流出
        """
        # 检查是否有价格信号
        price_signal = raw_signals.get('price', {})
        if not price_signal.get('is_breakout_up', False):
            return False

        # 检查资金流
        money_signal = raw_signals.get('money', {})
        net_flow = money_signal.get('net_money_flow', 0)

        # 价格上涨但资金流出
        if net_flow < -self.config.divergence_threshold * 1000:  # 转换为手数
            return True

        return False

    def _is_fake_breakout(self, symbol: str, tick_data: Dict[str, Any]) -> bool:
        """
        检测假突破

        特征：突破后立即跌破突破位
        """
        # 检查是否有突破记录
        if symbol not in self.breakouts:
            return False

        breakout = self.breakouts[symbol]
        if not breakout.get('is_breakout', False):
            return False

        # 检查是否立即跌破
        current_price = tick_data.get('price', 0)
        breakout_price = breakout.get('price', 0)
        resistance_level = breakout.get('resistance_level', 0)

        # 跌破阻力位
        if current_price < resistance_level * (1 - self.config.fake_breakout_threshold):
            return True

        return False

    def _classify_trap_type(self, reasons: List[str]) -> str:
        """分类诱多类型"""
        if "假突破" in reasons:
            return "fake_breakout"
        elif "快速回落" in reasons and "资金背离" in reasons:
            return "pullback_divergence"
        elif "放量滞涨" in reasons:
            return "volume_stagnation"
        elif "资金背离" in reasons:
            return "money_divergence"
        else:
            return "unknown"

    def record_breakout(
        self,
        symbol: str,
        price: float,
        resistance_level: float,
        is_breakout: bool = True,
    ):
        """记录突破"""
        self.breakouts[symbol] = {
            'price': price,
            'resistance_level': resistance_level,
            'is_breakout': is_breakout,
            'timestamp': datetime.now(),
        }

    def clear_breakout(self, symbol: str):
        """清除突破记录"""
        self.breakouts.pop(symbol, None)

    def reset(self, symbol: Optional[str] = None):
        """重置历史数据"""
        if symbol:
            self.price_history.pop(symbol, None)
            self.volume_history.pop(symbol, None)
            self.money_flow_history.pop(symbol, None)
            self.breakouts.pop(symbol, None)
        else:
            self.price_history.clear()
            self.volume_history.clear()
            self.money_flow_history.clear()
            self.breakouts.clear()
