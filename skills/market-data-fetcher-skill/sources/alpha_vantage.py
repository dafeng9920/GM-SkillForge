"""
Alpha Vantage 数据源适配器
"""

import pandas as pd
from datetime import datetime
from typing import Optional
import asyncio


class AlphaVantageSource:
    """
    Alpha Vantage 数据源

    免费数据源，提供股票、外汇、加密货币数据
    延迟: 实时
    限制: 免费版每分钟 5 次请求，每天 500 次
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._base_url = "https://www.alphavantage.co/query"
        self._session = None

    async def fetch(
        self,
        symbol: str,
        interval: str,
        start: datetime,
        end: datetime,
    ) -> Optional[pd.DataFrame]:
        """从 Alpha Vantage 获取数据"""
        if not self.is_available():
            raise RuntimeError("Alpha Vantage not available")

        # Alpha Vantage interval 映射
        interval_map = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "1h": "60min",
            "1d": "daily",
        }

        av_interval = interval_map.get(interval, "daily")

        # 构建请求参数
        params = {
            "function": "TIME_SERIES_INTRADAY" if interval != "1d" else "TIME_SERIES_DAILY",
            "symbol": symbol,
            "interval": av_interval,
            "apikey": self.api_key,
            "outputsize": "full",
        }

        try:
            data = await self._make_request(params)

            if data is None:
                return None

            # 解析响应
            if interval != "1d":
                time_key = f"Time Series ({av_interval})"
            else:
                time_key = "Time Series (Daily)"

            if time_key not in data:
                return None

            # 转换为 DataFrame
            df_data = []
            for timestamp, values in data[time_key].items():
                df_data.append({
                    "timestamp": pd.to_datetime(timestamp),
                    "open": float(values["1. open"]),
                    "high": float(values["2. high"]),
                    "low": float(values["3. low"]),
                    "close": float(values["4. close"]),
                    "volume": int(values["5. volume"]),
                })

            df = pd.DataFrame(df_data)
            df = df.set_index("timestamp")
            df = df.sort_index()

            # 过滤时间范围
            df = df[(df.index >= start) & (df.index <= end)]

            return df

        except Exception as e:
            print(f"Alpha Vantage fetch error: {e}")
            return None

    async def _make_request(self, params: dict) -> Optional[dict]:
        """发起 HTTP 请求"""
        import aiohttp

        timeout = aiohttp.ClientTimeout(total=30)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(self._base_url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Alpha Vantage API error: {response.status}")
                        return None

        except asyncio.TimeoutError:
            print("Alpha Vantage request timeout")
            return None
        except Exception as e:
            print(f"Alpha Vantage request error: {e}")
            return None

    def is_available(self) -> bool:
        """检查数据源是否可用"""
        return bool(self.api_key)
