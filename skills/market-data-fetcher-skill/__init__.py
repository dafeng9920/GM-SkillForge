"""
Market Data Fetcher Skill - 市场数据获取技能

从多数据源获取实时/历史市场数据（K线、Tick），支持缓存和持久化
"""

from .fetcher import MarketDataFetcher
from .cache import DataCache
from .persistence import DataPersistence

__version__ = "0.1.0"
__all__ = [
    "MarketDataFetcher",
    "DataCache",
    "DataPersistence",
]
