"""
Financial Data Fetcher Skill - 使用示例
"""

import asyncio
from financial_data_fetcher_skill import FinancialDataFetcher


async def main():
    """示例：获取财务数据"""

    fetcher = FinancialDataFetcher()

    # 获取 AAPL 的财务数据
    results = await fetcher.fetch(
        symbols=["AAPL"],
        data_types=["income_statement", "ratios", "metrics"],
        period="quarterly"
    )

    for symbol, result in results.items():
        if result["status"] == "SUCCESS":
            print(f"\n{symbol} 财务数据:")
            data = result["data"]

            if "income_statement" in data:
                inc = data["income_statement"]
                print(f"\n  利润表 ({inc['period']}):")
                print(f"    收入: ${inc['revenue']:,.0f}")
                print(f"    净利润: ${inc['net_income']:,.0f}")
                print(f"    EPS: ${inc['eps']:.2f}")

            if "ratios" in data:
                ratios = data["ratios"]
                print(f"\n  财务比率:")
                print(f"    P/E: {ratios['pe_ratio']:.2f}")
                print(f"    P/B: {ratios['pb_ratio']:.2f}")
                print(f"    ROE: {ratios['roe']:.2%}")
                print(f"    负债/权益: {ratios['debt_to_equity']:.2f}")

            if "metrics" in data:
                metrics = data["metrics"]
                print(f"\n  估值指标:")
                print(f"    市值: ${metrics['market_cap']:,.0f}")
                print(f"    Beta: {metrics['beta']:.2f}")
                print(f"    股息收益率: {metrics['dividend_yield']:.2%}")
        else:
            print(f"\n{symbol}: 失败 - {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    asyncio.run(main())
