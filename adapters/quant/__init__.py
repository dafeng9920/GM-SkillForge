"""
Quant Adapter Layer - 策略与数据适配器

职责: 翻译，不执行
- 把量化概念 → SkillForge 标准格式
- 把策略信号 → Core Skills 可理解的输入

不包含: 风控、执行（这些在 Core）
"""

from .data.openbb_fetch import OpenBBAdapter
from .strategies.signal_generator import SignalAdapter

__all__ = [
    "OpenBBAdapter",
    "SignalAdapter",
]
