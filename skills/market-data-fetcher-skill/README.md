# Market Data Fetcher Skill

市场数据获取技能 - 从多数据源获取实时/历史市场数据

## 功能

- ✅ 多数据源支持（Yahoo Finance, Alpha Vantage）
- ✅ 自动缓存（Redis）
- ✅ 数据持久化（PostgreSQL + MinIO）
- ✅ 数据质量验证
- ✅ 异步高性能

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

```python
import asyncio
from datetime import datetime, timedelta
from market_data_fetcher_skill import MarketDataFetcher

async def main():
    fetcher = MarketDataFetcher()
    await fetcher.initialize()

    # 获取最新 30 天数据
    results = await fetcher.fetch_latest(
        symbols=["AAPL", "MSFT", "SPY"],
        interval="1d",
        lookback_days=30
    )

    for symbol, result in results.items():
        if result["status"] == "SUCCESS":
            print(f"{symbol}: {result['records']} 条记录")

    await fetcher.close()

asyncio.run(main())
```

## 配置

通过环境变量配置：

```bash
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
CACHE_TTL=60

# PostgreSQL
DATABASE_URL=postgresql://quant_admin:password@localhost:5432/quant_meta

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin_change_me
MINIO_BUCKET=market-data

# Alpha Vantage (可选)
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

## 数据源

### Yahoo Finance

- **费用**: 免费
- **延迟**: 15分钟
- **限制**: 建议每小时不超过 2000 次请求
- **市场**: 全球

### Alpha Vantage

- **费用**: 免费版 / 付费版
- **延迟**: 实时
- **限制**: 免费版每分钟 5 次请求
- **市场**: 美股、外汇、加密货币

## DoD

- [x] 支持至少 2 个数据源
- [x] Redis 缓存正常工作
- [x] PostgreSQL 持久化成功
- [x] 数据质量检查通过
- [x] 返回标准化的输出格式
- [x] 错误处理和重试机制
