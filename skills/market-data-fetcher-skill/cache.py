"""
缓存层 - Redis 缓存实现
"""

import json
import hashlib
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
import redis.asyncio as aioredis
from .config import CacheConfig


class DataCache:
    """数据缓存层 - 使用 Redis 缓存市场数据"""

    def __init__(self, config: CacheConfig):
        self.config = config
        self._redis: Optional[aioredis.Redis] = None

    async def connect(self):
        """连接 Redis"""
        self._redis = await aioredis.from_url(
            f"redis://{self.config.redis_host}:{self.config.redis_port}/{self.config.redis_db}",
            encoding="utf-8",
            decode_responses=False,
        )

    async def disconnect(self):
        """断开连接"""
        if self._redis:
            await self._redis.close()

    def _make_cache_key(self, symbol: str, interval: str,
                        start: datetime, end: datetime) -> str:
        """生成缓存键"""
        key_str = f"{symbol}:{interval}:{start.isoformat()}:{end.isoformat()}"
        return f"market_data:{hashlib.md5(key_str.encode()).hexdigest()}"

    async def get(self, symbol: str, interval: str,
                  start: datetime, end: datetime) -> Optional[pd.DataFrame]:
        """从缓存获取数据"""
        if not self._redis:
            return None

        cache_key = self._make_cache_key(symbol, interval, start, end)
        cached_data = await self._redis.get(cache_key)

        if cached_data:
            # 从 JSON 恢复 DataFrame
            data = json.loads(cached_data)
            df = pd.DataFrame(data["data"])
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            return df.set_index("timestamp")

        return None

    async def set(self, symbol: str, interval: str,
                  start: datetime, end: datetime,
                  data: pd.DataFrame, ttl: Optional[int] = None):
        """写入缓存"""
        if not self._redis:
            return

        cache_key = self._make_cache_key(symbol, interval, start, end)

        # 将 DataFrame 转换为 JSON
        df_to_cache = data.reset_index()
        serialized_data = {
            "symbol": symbol,
            "interval": interval,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "data": df_to_cache.to_dict(orient="records"),
        }

        await self._redis.setex(
            cache_key,
            ttl or self.config.default_ttl,
            json.dumps(serialized_data),
        )

    async def invalidate(self, symbol: str, interval: Optional[str] = None):
        """失效缓存"""
        if not self._redis:
            return

        pattern = f"market_data:*{symbol}*"
        if interval:
            pattern = f"market_data:*{symbol}:{interval}*"

        keys = await self._redis.keys(pattern)
        if keys:
            await self._redis.delete(*keys)

    async def get_stats(self) -> dict:
        """获取缓存统计信息"""
        if not self._redis:
            return {}

        info = await self._redis.info("stats")
        keys = await self._redis.keys("market_data:*")

        return {
            "total_keys": len(keys),
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "hit_rate": info.get("keyspace_hits", 0) / max(
                info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1
            ) * 100,
        }
