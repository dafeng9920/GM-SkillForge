"""
Market Data Fetcher Skill - 使用示例
"""

import asyncio
from datetime import datetime, timedelta
from market_data_fetcher_skill import MarketDataFetcher


async def main():
    """示例：获取市场数据"""

    # 初始化数据获取器
    fetcher = MarketDataFetcher()
    await fetcher.initialize()

    try:
        # 获取最新数据
        symbols = ["AAPL", "MSFT", "SPY"]
        results = await fetcher.fetch_latest(
            symbols=symbols,
            interval="1d",
            lookback_days=30
        )

        # 打印结果
        for symbol, result in results.items():
            if result["status"] == "SUCCESS":
                print(f"\n{symbol}:")
                print(f"  来源: {result['source']}")
                print(f"  记录数: {result['records']}")
                print(f"  缓存命中: {result['cache_hit']}")
                print(f"  最新价格: {result['data']['close'].iloc[-1]:.2f}")
                print(f"  数据预览:\n{result['data'].tail()}")
            else:
                print(f"\n{symbol}: 失败 - {result.get('error', 'Unknown error')}")

        # 获取缓存统计
        stats = await fetcher.get_cache_stats()
        print(f"\n缓存统计: {stats}")

    finally:
        await fetcher.close()


if __name__ == "__main__":
    asyncio.run(main())
