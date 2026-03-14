"""
配置管理 - Market Data Fetcher Skill
"""

import os
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class DataSourceConfig:
    """数据源配置"""
    enabled: bool
    priority: int
    rate_limit: int
    api_key: str = ""


@dataclass
class CacheConfig:
    """缓存配置"""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    default_ttl: int = 60


@dataclass
class StorageConfig:
    """存储配置"""
    postgres_url: str = ""
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin_change_me"
    minio_bucket: str = "market-data"


@dataclass
class MarketDataConfig:
    """市场数据获取配置"""
    data_sources: Dict[str, DataSourceConfig]
    cache: CacheConfig
    storage: StorageConfig

    @classmethod
    def from_env(cls) -> "MarketDataConfig":
        """从环境变量加载配置"""
        return cls(
            data_sources={
                "yahoo": DataSourceConfig(
                    enabled=True,
                    priority=1,
                    rate_limit=2000,
                ),
                "alpha_vantage": DataSourceConfig(
                    enabled=bool(os.getenv("ALPHA_VANTAGE_API_KEY")),
                    priority=2,
                    rate_limit=5,
                    api_key=os.getenv("ALPHA_VANTAGE_API_KEY", ""),
                ),
            },
            cache=CacheConfig(
                redis_host=os.getenv("REDIS_HOST", "localhost"),
                redis_port=int(os.getenv("REDIS_PORT", "6379")),
                default_ttl=int(os.getenv("CACHE_TTL", "60")),
            ),
            storage=StorageConfig(
                postgres_url=os.getenv(
                    "DATABASE_URL",
                    "postgresql://quant_admin:quant_secure_change_me@localhost:5432/quant_meta"
                ),
                minio_endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
                minio_access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
                minio_secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin_change_me"),
                minio_bucket=os.getenv("MINIO_BUCKET", "market-data"),
            ),
        )
