"""
市场数据获取器 - 主入口
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Literal
import asyncio

from .config import MarketDataConfig
from .cache import DataCache
from .persistence import DataPersistence
from .sources.base import DataSource
from .sources.yahoo import YahooFinanceSource
from .sources.alpha_vantage import AlphaVantageSource


class MarketDataFetcher:
    """
    市场数据获取器 - 从多数据源获取市场数据

    功能：
    1. 支持多数据源（Yahoo Finance, Alpha Vantage, etc.）
    2. 自动缓存（Redis）
    3. 持久化存储（PostgreSQL + MinIO）
    4. 数据质量验证
    """

    def __init__(self, config: Optional[MarketDataConfig] = None):
        self.config = config or MarketDataConfig.from_env()
        self.cache = DataCache(self.config.cache)
        self.persistence = DataPersistence(self.config.storage)
        self._sources: Dict[str, DataSource] = {}
        self._init_sources()

    def _init_sources(self):
        """初始化数据源"""
        # Yahoo Finance（默认启用）
        if self.config.data_sources.get("yahoo", DataSourceConfig(enabled=False, priority=0, rate_limit=0)).enabled:
            self._sources["yahoo"] = YahooFinanceSource()

        # Alpha Vantage（需要 API Key）
        av_config = self.config.data_sources.get("alpha_vantage")
        if av_config and av_config.enabled and av_config.api_key:
            self._sources["alpha_vantage"] = AlphaVantageSource(api_key=av_config.api_key)

    async def initialize(self):
        """初始化连接"""
        await self.cache.connect()
        await self.persistence.connect()

    async def close(self):
        """关闭连接"""
        await self.cache.disconnect()
        await self.persistence.disconnect()

    async def fetch(
        self,
        symbols: List[str],
        interval: Literal["1m", "5m", "15m", "1h", "1d"],
        start: datetime,
        end: datetime,
        use_cache: bool = True,
        cache_ttl: int = 60,
        persist: bool = True,
    ) -> Dict[str, dict]:
        """
        获取市场数据

        Args:
            symbols: 股票代码列表
            interval: K线间隔
            start: 开始时间
            end: 结束时间
            use_cache: 是否使用缓存
            cache_ttl: 缓存过期时间（秒）
            persist: 是否持久化

        Returns:
            {
                "AAPL": {
                    "status": "SUCCESS",
                    "data": DataFrame,
                    "source": "yahoo",
                    "records": 390,
                    "cache_hit": False,
                },
                ...
            }
        """
        results = {}

        for symbol in symbols:
            try:
                # 1. 尝试从缓存获取
                cache_hit = False
                data = None

                if use_cache:
                    data = await self.cache.get(symbol, interval, start, end)
                    if data is not None and not data.empty:
                        cache_hit = True

                # 2. 缓存未命中，从数据源获取
                if data is None or data.empty:
                    data = await self._fetch_from_source(symbol, interval, start, end)

                # 3. 数据质量验证
                if data is not None and not data.empty:
                    data = self._validate_data(data, symbol)

                    # 4. 写入缓存
                    if use_cache and not cache_hit:
                        await self.cache.set(symbol, interval, start, end, data, cache_ttl)

                    # 5. 持久化
                    if persist:
                        await self.persistence.save_to_postgres(symbol, interval, data)

                        # 归档到 MinIO（按日期）
                        date_str = end.strftime("%Y-%m-%d")
                        await self.persistence.archive_to_minio(symbol, interval, data, date_str)

                    results[symbol] = {
                        "status": "SUCCESS",
                        "data": data,
                        "source": self._get_source_name(symbol),
                        "records": len(data),
                        "cache_hit": cache_hit,
                    }
                else:
                    results[symbol] = {
                        "status": "FAILED",
                        "error": "No data available",
                        "data": None,
                    }

            except Exception as e:
                results[symbol] = {
                    "status": "FAILED",
                    "error": str(e),
                    "data": None,
                }

        return results

    async def _fetch_from_source(
        self, symbol: str, interval: str,
        start: datetime, end: datetime
    ) -> Optional[pd.DataFrame]:
        """从配置的数据源获取数据（按优先级）"""
        # 按优先级排序数据源
        sorted_sources = sorted(
            self._sources.items(),
            key=lambda x: self.config.data_sources[x[0]].priority
        )

        for source_name, source in sorted_sources:
            try:
                data = await source.fetch(symbol, interval, start, end)
                if data is not None and not data.empty:
                    return data
            except Exception as e:
                print(f"Source {source_name} failed for {symbol}: {e}")
                continue

        return None

    def _validate_data(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """数据质量验证"""
        # 检查必需列
        required_cols = ["open", "high", "low", "close", "volume"]
        if not all(col in data.columns for col in required_cols):
            raise ValueError(f"Missing required columns for {symbol}")

        # 价格合理性检查
        invalid = (data["high"] < data["low"]) | \
                  (data["close"] > data["high"]) | \
                  (data["close"] < data["low"])

        if invalid.any():
            # 移除无效行
            data = data[~invalid]
            print(f"Removed {invalid.sum()} invalid rows for {symbol}")

        # 成交量非负检查
        data = data[data["volume"] >= 0]

        # 移除重复时间戳
        data = data[~data.index.duplicated(keep="first")]

        # 排序
        data = data.sort_index()

        return data

    def _get_source_name(self, symbol: str) -> str:
        """获取数据源名称"""
        for source_name in self._sources.keys():
            return source_name
        return "unknown"

    async def fetch_latest(
        self, symbols: List[str], interval: str, lookback_days: int = 30
    ) -> Dict[str, dict]:
        """获取最新数据（便捷方法）"""
        end = datetime.now()
        start = end - timedelta(days=lookback_days)
        return await self.fetch(symbols, interval, start, end)

    async def get_cache_stats(self) -> dict:
        """获取缓存统计信息"""
        return await self.cache.get_stats()


# 配置类导入
from dataclasses import dataclass


@dataclass
class DataSourceConfig:
    """数据源配置"""
    enabled: bool
    priority: int
    rate_limit: int
    api_key: str = ""
