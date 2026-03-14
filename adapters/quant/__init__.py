"""
Quant Adapter Layer - 策略与数据适配器

职责: 翻译，不执行
- 把量化概念 → SkillForge 标准格式
- 把策略信号 → Core Skills 可理解的输入

不包含: 风控、执行（这些在 Core）
"""

# 导入 Phase 4 系统核心组件
from .phase4.engine import Phase4Engine
from .phase4.validation import ValidationPointManager, ValidationResult

# 导入回测系统
from .backtest.engine import BacktestEngine
from .backtest.events import TickEvent, SignalEvent, OrderEvent, FillEvent
from .backtest.metrics import PerformanceMetrics

# 导入标准合约
from .contracts import (
    AdapterOutput,
    TradingIntent,
    AdapterContext,
    SignalAction,
    AdapterStatus,
    create_buy_signal,
    create_sell_signal,
    create_hold_signal,
)

__all__ = [
    # Phase 4 系统
    "Phase4Engine",
    "ValidationPointManager",
    "ValidationResult",
    # 回测系统
    "BacktestEngine",
    "TickEvent",
    "SignalEvent",
    "OrderEvent",
    "FillEvent",
    "PerformanceMetrics",
    # 标准合约
    "AdapterOutput",
    "TradingIntent",
    "AdapterContext",
    "SignalAction",
    "AdapterStatus",
    "create_buy_signal",
    "create_sell_signal",
    "create_hold_signal",
]
