"""
Yahoo Finance 数据源适配器
"""

import pandas as pd
from datetime import datetime
from typing import Optional
import asyncio


class YahooFinanceSource:
    """
    Yahoo Finance 数据源

    免费数据源，支持全球市场
    延迟: 实时（有15分钟延迟）
    限制: 无官方限制，建议每小时不超过 2000 次请求
    """

    def __init__(self):
        self._yf = None
        self._init_yfinance()

    def _init_yfinance(self):
        """延迟导入 yfinance"""
        try:
            import yfinance as yf
            self._yf = yf
        except ImportError:
            print("Warning: yfinance not installed. Install with: pip install yfinance")
            self._yf = None

    async def fetch(
        self,
        symbol: str,
        interval: str,
        start: datetime,
        end: datetime,
    ) -> Optional[pd.DataFrame]:
        """从 Yahoo Finance 获取数据"""
        if not self.is_available():
            raise RuntimeError("yfinance not available")

        loop = asyncio.get_event_loop()

        def _fetch_sync():
            ticker = self._yf.Ticker(symbol)

            # Yahoo interval 映射
            interval_map = {
                "1m": "1m",
                "5m": "5m",
                "15m": "15m",
                "1h": "1h",
                "1d": "1d",
            }

            yf_interval = interval_map.get(interval, "1d")

            # 限制 1m 数据范围（Yahoo 只提供最近 7 天的 1m 数据）
            if interval == "1m":
                max_start = datetime.now() - pd.Timedelta(days=7)
                if start < max_start:
                    start = max_start

            data = ticker.history(
                start=start,
                end=end,
                interval=yf_interval,
                auto_adjust=False,  # 保留调整后的价格信息
                prepost=False,       # 不包含盘前盘后
            )

            if data.empty:
                return None

            # 标准化列名
            data.columns = [col.lower() for col in data.columns]

            # 确保有必需列
            required_cols = ["open", "high", "low", "close", "volume"]
            if not all(col in data.columns for col in required_cols):
                return None

            return data[required_cols]

        return await loop.run_in_executor(None, _fetch_sync)

    def is_available(self) -> bool:
        """检查数据源是否可用"""
        return self._yf is not None
