"""
资金流监听器 - 感知层核心组件

只记录资金流行为，不做任何判断
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class MoneyFlowSignal:
    """资金流信号 - 只记录资金行为"""
    signal_type = "money"

    # 大单统计（不做判断，只记录事实）
    big_buy_orders: int           # 大买单数量
    big_sell_orders: int          # 大卖单数量
    net_money_flow: float         # 净资金流（买入-卖出）

    # 资金流状态
    is_big_inflow: bool           # 是否大单流入
    is_big_outflow: bool          # 是否大单流出
    is_continuous_inflow: bool    # 是否持续流入
    is_continuous_outflow: bool   # 是否持续流出

    # 主动买卖比例
    active_buy_ratio: float       # 主动买占比
    active_sell_ratio: float      # 主动卖占比

    # 资金流强度
    flow_strength: str = "neutral"  # 资金流强度：strong_in, weak_in, neutral, weak_out, strong_out

    # 资金流趋势
    flow_trend: str = "neutral"    # 资金流趋势：inflow, outflow, neutral

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'signal_type': self.signal_type,
            'big_buy_orders': self.big_buy_orders,
            'big_sell_orders': self.big_sell_orders,
            'net_money_flow': self.net_money_flow,
            'is_big_inflow': self.is_big_inflow,
            'is_big_outflow': self.is_big_outflow,
            'is_continuous_inflow': self.is_continuous_inflow,
            'is_continuous_outflow': self.is_continuous_outflow,
            'active_buy_ratio': self.active_buy_ratio,
            'active_sell_ratio': self.active_sell_ratio,
            'flow_strength': self.flow_strength,
            'flow_trend': self.flow_trend,
        }


class MoneyListener:
    """
    资金流监听器 - 只听不说

    职责：
    1. 记录资金流行为
    2. 检测大单流入/流出
    3. 计算净资金流
    4. 不做任何交易决策

    注意：
    - 实际使用时需要对接实时的盘口数据（Level-2行情）
    - 这里提供框架和模拟实现
    """

    def __init__(
        self,
        big_order_threshold: int = 100,    # 大单阈值（手数）
        flow_window: int = 5,               # 资金流判断窗口
    ):
        """
        初始化资金流监听器

        Args:
            big_order_threshold: 大单阈值（手数）
            flow_window: 资金流判断窗口（tick数）
        """
        self.big_order_threshold = big_order_threshold
        self.flow_window = flow_window

        # 历史数据
        self.flow_history: Dict[str, deque] = {}

    def listen(self, tick_data: Dict[str, Any]) -> MoneyFlowSignal:
        """
        听市场资金流信号

        Args:
            tick_data: Tick数据
                {
                    "symbol": str,
                    "price": float,
                    "volume": int,
                    "bid": float,
                    "ask": float,
                    "bid_size": int,     # 买盘量
                    "ask_size": int,     # 卖盘量
                    # 可选（如果有Level-2数据）
                    "big_orders": List[Dict],  # 大单数据
                    "active_buy_volume": int,   # 主动买量
                    "active_sell_volume": int,  # 主动卖量
                }

        Returns:
            MoneyFlowSignal: 资金流信号（只记录，不判断）
        """
        symbol = tick_data['symbol']

        # 计算当前资金流
        current_flow = self._calculate_current_flow(tick_data)

        # 更新历史数据
        self._update_history(symbol, current_flow)

        # 获取历史数据
        history = list(self.flow_history.get(symbol, deque(maxlen=self.flow_window)))

        # 构建资金流信号
        signal = MoneyFlowSignal(
            big_buy_orders=current_flow.get('big_buy', 0),
            big_sell_orders=current_flow.get('big_sell', 0),
            net_money_flow=current_flow.get('net_flow', 0),
            is_big_inflow=current_flow.get('net_flow', 0) > 0,
            is_big_outflow=current_flow.get('net_flow', 0) < 0,
            is_continuous_inflow=self._is_continuous_inflow(history),
            is_continuous_outflow=self._is_continuous_outflow(history),
            active_buy_ratio=current_flow.get('active_buy_ratio', 0.5),
            active_sell_ratio=current_flow.get('active_sell_ratio', 0.5),
            flow_strength=self._classify_flow_strength(current_flow.get('net_flow', 0)),
            flow_trend=self._detect_flow_trend(history),
        )

        return signal

    def _calculate_current_flow(self, tick_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算当前资金流

        这里使用简化版计算方法：
        1. 根据买卖盘变化推断资金流
        2. 如果有大单数据，直接使用
        """
        # 如果有大单数据（Level-2）
        if 'big_orders' in tick_data:
            return self._calculate_from_big_orders(tick_data['big_orders'])

        # 如果有主动买卖数据
        if 'active_buy_volume' in tick_data and 'active_sell_volume' in tick_data:
            buy_vol = tick_data['active_buy_volume']
            sell_vol = tick_data['active_sell_volume']
            net_flow = buy_vol - sell_vol
            total = buy_vol + sell_vol

            return {
                'big_buy': buy_vol // self.big_order_threshold,
                'big_sell': sell_vol // self.big_order_threshold,
                'net_flow': net_flow,
                'active_buy_ratio': buy_vol / total if total > 0 else 0.5,
                'active_sell_ratio': sell_vol / total if total > 0 else 0.5,
            }

        # 简化版：根据买卖盘变化推断
        bid_size = tick_data.get('bid_size', 0)
        ask_size = tick_data.get('ask_size', 0)

        # 买卖盘不平衡度
        total_size = bid_size + ask_size
        if total_size > 0:
            bid_ratio = bid_size / total_size
            ask_ratio = ask_size / total_size
        else:
            bid_ratio = 0.5
            ask_ratio = 0.5

        # 估算资金流（简化版）
        volume = tick_data.get('volume', 0)
        estimated_flow = (bid_ratio - ask_ratio) * volume

        return {
            'big_buy': int(bid_size // self.big_order_threshold),
            'big_sell': int(ask_size // self.big_order_threshold),
            'net_flow': estimated_flow,
            'active_buy_ratio': bid_ratio,
            'active_sell_ratio': ask_ratio,
        }

    def _calculate_from_big_orders(self, big_orders: List[Dict]) -> Dict[str, Any]:
        """从大单数据计算资金流"""
        big_buy = 0
        big_sell = 0
        active_buy_vol = 0
        active_sell_vol = 0

        for order in big_orders:
            volume = order.get('volume', 0)
            direction = order.get('direction', 'unknown')

            if direction == 'buy':
                big_buy += 1
                active_buy_vol += volume
            elif direction == 'sell':
                big_sell += 1
                active_sell_vol += volume

        net_flow = active_buy_vol - active_sell_vol
        total = active_buy_vol + active_sell_vol

        return {
            'big_buy': big_buy,
            'big_sell': big_sell,
            'net_flow': net_flow,
            'active_buy_ratio': active_buy_vol / total if total > 0 else 0.5,
            'active_sell_ratio': active_sell_vol / total if total > 0 else 0.5,
        }

    def _update_history(self, symbol: str, flow: Dict[str, Any]):
        """更新历史数据"""
        if symbol not in self.flow_history:
            self.flow_history[symbol] = deque(maxlen=self.flow_window)

        self.flow_history[symbol].append(flow)

    def _is_continuous_inflow(self, history: List[Dict]) -> bool:
        """判断是否持续流入"""
        if len(history) < 3:
            return False

        # 检查最近3个tick是否都是流入
        recent = history[-3:]
        return all(flow.get('net_flow', 0) > 0 for flow in recent)

    def _is_continuous_outflow(self, history: List[Dict]) -> bool:
        """判断是否持续流出"""
        if len(history) < 3:
            return False

        # 检查最近3个tick是否都是流出
        recent = history[-3:]
        return all(flow.get('net_flow', 0) < 0 for flow in recent)

    def _classify_flow_strength(self, net_flow: float) -> str:
        """分类资金流强度"""
        if net_flow > 1000:  # 强流入
            return "strong_in"
        elif net_flow > 0:   # 弱流入
            return "weak_in"
        elif net_flow < -1000:  # 强流出
            return "strong_out"
        elif net_flow < 0:   # 弱流出
            return "weak_out"
        else:
            return "neutral"

    def _detect_flow_trend(self, history: List[Dict]) -> str:
        """检测资金流趋势"""
        if len(history) < 5:
            return "neutral"

        # 计算最近5个tick的平均资金流
        avg_flow = sum(flow.get('net_flow', 0) for flow in history[-5:]) / 5

        if avg_flow > 500:
            return "inflow"
        elif avg_flow < -500:
            return "outflow"
        else:
            return "neutral"

    def reset(self, symbol: Optional[str] = None):
        """
        重置历史数据

        Args:
            symbol: 如果指定，只重置该股票；否则重置所有
        """
        if symbol:
            self.flow_history.pop(symbol, None)
        else:
            self.flow_history.clear()

    def get_history_length(self, symbol: str) -> int:
        """获取某股票的历史数据长度"""
        return len(self.flow_history.get(symbol, []))
