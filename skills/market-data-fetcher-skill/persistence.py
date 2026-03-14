"""
持久化层 - PostgreSQL 和 MinIO 持久化实现
"""

import pandas as pd
from datetime import datetime
from typing import Optional
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import minio
from io import BytesIO

from .config import StorageConfig


class DataPersistence:
    """数据持久化层 - PostgreSQL + MinIO"""

    def __init__(self, config: StorageConfig):
        self.config = config
        self._engine = None
        self._session_factory = None
        self._minio_client: Optional[minio.Minio] = None

    async def connect(self):
        """连接数据库和 MinIO"""
        # 连接 PostgreSQL
        self._engine = create_async_engine(
            self.config.postgres_url.replace("postgresql://", "postgresql+asyncpg://"),
            echo=False,
        )
        self._session_factory = sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

        # 连接 MinIO
        self._minio_client = minio.Minio(
            self.config.minio_endpoint,
            access_key=self.config.minio_access_key,
            secret_key=self.config.minio_secret_key,
            secure=False,
        )

        # 确保桶存在
        await self._ensure_bucket()

        # 初始化数据库表
        await self._init_tables()

    async def disconnect(self):
        """断开连接"""
        if self._engine:
            await self._engine.dispose()

    async def _ensure_bucket(self):
        """确保 MinIO 桶存在"""
        loop = asyncio.get_event_loop()
        try:
            if not await loop.run_in_executor(
                None, self._minio_client.bucket_exists, self.config.minio_bucket
            ):
                await loop.run_in_executor(
                    None, self._minio_client.make_bucket, self.config.minio_bucket
                )
        except Exception as e:
            print(f"MinIO bucket setup warning: {e}")

    async def _init_tables(self):
        """初始化数据库表"""
        async with self._engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS market_data (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(50) NOT NULL,
                    interval VARCHAR(10) NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    open DECIMAL(20, 8),
                    high DECIMAL(20, 8),
                    low DECIMAL(20, 8),
                    close DECIMAL(20, 8),
                    volume BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, interval, timestamp)
                );

                CREATE INDEX IF NOT EXISTS idx_market_data_symbol_time
                    ON market_data(symbol, timestamp DESC);

                CREATE INDEX IF NOT EXISTS idx_market_data_interval
                    ON market_data(interval);
            """))

    async def save_to_postgres(self, symbol: str, interval: str, df: pd.DataFrame):
        """保存数据到 PostgreSQL"""
        async with self._session_factory() as session:
            df_to_save = df.reset_index()
            df_to_save["symbol"] = symbol
            df_to_save["interval"] = interval

            # 批量插入（使用 ON CONFLICT 进行 upsert）
            for _, row in df_to_save.iterrows():
                await session.execute(text("""
                    INSERT INTO market_data
                        (symbol, interval, timestamp, open, high, low, close, volume)
                    VALUES
                        (:symbol, :interval, :timestamp, :open, :high, :low, :close, :volume)
                    ON CONFLICT (symbol, interval, timestamp)
                    DO UPDATE SET
                        open = EXCLUDED.open,
                        high = EXCLUDED.high,
                        low = EXCLUDED.low,
                        close = EXCLUDED.close,
                        volume = EXCLUDED.volume
                """), {
                    "symbol": symbol,
                    "interval": interval,
                    "timestamp": row["timestamp"],
                    "open": row["open"],
                    "high": row["high"],
                    "low": row["low"],
                    "close": row["close"],
                    "volume": row["volume"],
                })

            await session.commit()

    async def load_from_postgres(
        self, symbol: str, interval: str,
        start: datetime, end: datetime
    ) -> Optional[pd.DataFrame]:
        """从 PostgreSQL 加载数据"""
        async with self._session_factory() as session:
            result = await session.execute(text("""
                SELECT timestamp, open, high, low, close, volume
                FROM market_data
                WHERE symbol = :symbol
                    AND interval = :interval
                    AND timestamp BETWEEN :start AND :end
                ORDER BY timestamp ASC
            """), {
                "symbol": symbol,
                "interval": interval,
                "start": start,
                "end": end,
            })

            rows = result.fetchall()
            if rows:
                df = pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close", "volume"])
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                return df.set_index("timestamp")

            return None

    async def archive_to_minio(
        self, symbol: str, interval: str,
        df: pd.DataFrame, date_str: str
    ):
        """归档数据到 MinIO（Parquet 格式）"""
        loop = asyncio.get_event_loop()

        # 转换为 Parquet
        buffer = BytesIO()
        df.reset_index().to_parquet(buffer, index=False)
        buffer.seek(0)

        # 生成对象键
        object_name = f"{symbol}/{interval}/{date_str}.parquet"

        # 上传到 MinIO
        await loop.run_in_executor(
            None,
            self._minio_client.put_object,
            self.config.minio_bucket,
            object_name,
            buffer,
            len(buffer.getvalue()),
        )

    async def load_from_minio(
        self, symbol: str, interval: str, date_str: str
    ) -> Optional[pd.DataFrame]:
        """从 MinIO 加载归档数据"""
        loop = asyncio.get_event_loop()

        object_name = f"{symbol}/{interval}/{date_str}.parquet"

        try:
            response = await loop.run_in_executor(
                None,
                self._minio_client.get_object,
                self.config.minio_bucket,
                object_name,
            )

            data = response.read()
            df = pd.read_parquet(BytesIO(data))
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            return df.set_index("timestamp")

        except Exception as e:
            print(f"MinIO load error: {e}")
            return None
