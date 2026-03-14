"""
数据源基类
"""

from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime


class DataSource(ABC):
    """数据源基类"""

    @abstractmethod
    async def fetch(
        self,
        symbol: str,
        interval: str,
        start: datetime,
        end: datetime,
    ) -> pd.DataFrame:
        """
        获取市场数据

        Args:
            symbol: 股票代码
            interval: K线间隔
            start: 开始时间
            end: 结束时间

        Returns:
            DataFrame with columns: open, high, low, close, volume
            indexed by timestamp
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查数据源是否可用"""
        pass

    def normalize_interval(self, interval: str) -> str:
        """标准化间隔格式"""
        interval_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "1h": "1h",
            "1d": "1d",
        }
        return interval_map.get(interval, interval)
