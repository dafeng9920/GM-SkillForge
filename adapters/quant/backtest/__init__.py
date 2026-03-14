"""
Quant System Backtest Engine

事件驱动的回测引擎，支持 Phase 4 盘中同步系统验证
"""

from .engine import BacktestEngine
from .events import TickEvent, SignalEvent, OrderEvent, FillEvent
from .metrics import PerformanceMetrics

__all__ = [
    'BacktestEngine',
    'TickEvent',
    'SignalEvent',
    'OrderEvent',
    'FillEvent',
    'PerformanceMetrics',
]
