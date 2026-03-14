---
name: market-data-fetcher-skill
description: 从多数据源获取实时/历史市场数据（K线、Tick），支持缓存和持久化
---

# market-data-fetcher-skill

## 触发条件

- 策略需要市场数据时
- 定时数据更新任务
- 回测需要历史数据时

## 输入

```yaml
input:
  symbols: ["AAPL", "MSFT", "SPY"]
  interval: "1m"  # 1m, 5m, 15m, 1h, 1d
  start_date: "2024-01-01"
  end_date: "2024-03-09"
  data_sources: ["yahoo", "alpha_vantage"]
  use_cache: true
  cache_ttl_seconds: 60
```

## 输出

```yaml
output:
  status: "SUCCESS|PARTIAL|FAILED"
  data:
    - symbol: "AAPL"
      interval: "1m"
      records: 390
      fields: ["timestamp", "open", "high", "low", "close", "volume"]
      data_path: "s3://market-data/AAPL_1m_20240309.parquet"
  metadata:
    fetch_time: "2024-03-09T10:30:00Z"
    source: "yahoo"
    cache_hit: false
  errors: []
```

## 核心功能

### 数据源支持

- **Yahoo Finance**: 免费实时延迟数据
- **Alpha Vantage**: 免费 API，每日限额
- **Polygon.io**: 高频实时数据（付费）
- **Wind/Bloomberg**: 企业级数据源（需授权）

### 数据类型

| 类型 | 说明 | 更新频率 |
|------|------|----------|
| Tick | 逐笔成交 | 实时 |
| 1min K线 | 1分钟OHLCV | 实时 |
| 5min K线 | 5分钟OHLCV | 实时 |
| 1hour K线 | 1小时OHLCV | 每小时 |
| Daily K线 | 日线OHLCV | 每日 |

### 缓存策略

- Redis 缓存热数据（TTL: 60s）
- PostgreSQL 持久化历史数据
- MinIO 归档原始数据（Parquet格式）

## 实现细节

### 1. 数据获取接口

```python
class MarketDataFetcher:
    async def fetch(self, symbols: List[str], interval: str,
                    start: datetime, end: datetime) -> Dict[str, pd.DataFrame]:
        """从配置的数据源获取市场数据"""
```

### 2. 缓存层

```python
class DataCache:
    async def get(self, key: str) -> Optional[pd.DataFrame]:
        """从 Redis 获取缓存数据"""

    async def set(self, key: str, data: pd.DataFrame, ttl: int):
        """写入缓存"""
```

### 3. 持久化层

```python
class DataPersistence:
    async def save_to_postgres(self, symbol: str, interval: str, df: pd.DataFrame):
        """保存到 PostgreSQL 时序表"""

    async def archive_to_minio(self, symbol: str, interval: str, df: pd.DataFrame):
        """归档到 MinIO"""
```

## 数据质量检查

- 时间戳连续性检查
- 价格合理性检查（如 low <= close <= high）
- 成交量非负检查
- 缺失值处理

## DoD

- [ ] 支持至少 2 个数据源
- [ ] Redis 缓存正常工作
- [ ] PostgreSQL 持久化成功
- [ ] 数据质量检查通过
- [ ] 返回标准化的输出格式
- [ ] 错误处理和重试机制

## 依赖服务

- Redis: `localhost:6379`
- PostgreSQL: `localhost:5432`
- MinIO: `localhost:9000`

## 配置示例

```yaml
# config/market_data_config.yaml
data_sources:
  yahoo:
    enabled: true
    priority: 1
    rate_limit: 2000  # requests/hour
  alpha_vantage:
    enabled: true
    api_key: "${ALPHA_VANTAGE_API_KEY}"
    priority: 2
    rate_limit: 5  # requests/minute

cache:
  redis_host: "localhost"
  redis_port: 6379
  default_ttl: 60

storage:
  postgres_url: "postgresql://quant_admin:quant_secure_change_me@localhost:5432/quant_meta"
  minio_endpoint: "localhost:9000"
  minio_access_key: "minioadmin"
  minio_secret_key: "minioadmin_change_me"
  minio_bucket: "market-data"
```
