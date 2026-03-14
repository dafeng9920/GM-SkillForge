"""
财务数据获取器
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Literal
import asyncio


class FinancialDataFetcher:
    """
    财务数据获取器

    功能：
    1. 获取财报数据（利润表、资产负债表、现金流量表）
    2. 计算财务比率
    3. 获取估值指标
    4. 分析师预期
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
            print("Warning: yfinance not installed")

    async def fetch(
        self,
        symbols: List[str],
        data_types: List[Literal["income_statement", "balance_sheet", "cash_flow", "ratios", "metrics", "estimates"]],
        period: Literal["quarterly", "annual"] = "quarterly",
    ) -> Dict[str, dict]:
        """
        获取财务数据

        Args:
            symbols: 股票代码列表
            data_types: 需要的数据类型
            period: 季度/年度

        Returns:
            {
                "AAPL": {
                    "status": "SUCCESS",
                    "data": {...},
                },
                ...
            }
        """
        results = {}

        for symbol in symbols:
            try:
                ticker = self._yf.Ticker(symbol)
                company_data = {}

                # 获取各类财务数据
                if "income_statement" in data_types:
                    company_data["income_statement"] = await self._fetch_income_statement(ticker, period)

                if "balance_sheet" in data_types:
                    company_data["balance_sheet"] = await self._fetch_balance_sheet(ticker, period)

                if "cash_flow" in data_types:
                    company_data["cash_flow"] = await self._fetch_cash_flow(ticker, period)

                if "ratios" in data_types:
                    company_data["ratios"] = await self._fetch_ratios(ticker)

                if "metrics" in data_types:
                    company_data["metrics"] = await self._fetch_metrics(ticker)

                if "estimates" in data_types:
                    company_data["estimates"] = await self._fetch_estimates(ticker)

                results[symbol] = {
                    "status": "SUCCESS",
                    "data": company_data,
                }

            except Exception as e:
                results[symbol] = {
                    "status": "FAILED",
                    "error": str(e),
                }

        return results

    async def _fetch_income_statement(self, ticker, period: str) -> dict:
        """获取利润表"""
        loop = asyncio.get_event_loop()

        def _get():
            if period == "quarterly":
                df = ticker.financials
            else:
                df = ticker.quarterly_financials

            if df.empty:
                return {}

            # 获取最近一期的数据
            latest = df.iloc[:, 0]
            return {
                "period": df.columns[0].strftime("%Y-%m-%d"),
                "revenue": float(latest.get("Total Revenue", 0)),
                "cost_of_revenue": float(latest.get("Cost Of Revenue", 0)),
                "gross_profit": float(latest.get("Gross Profit", 0)),
                "operating_income": float(latest.get("Operating Income", 0)),
                "net_income": float(latest.get("Net Income", 0)),
                "eps": float(latest.get("Basic EPS", 0)),
            }

        return await loop.run_in_executor(None, _get)

    async def _fetch_balance_sheet(self, ticker, period: str) -> dict:
        """获取资产负债表"""
        loop = asyncio.get_event_loop()

        def _get():
            if period == "quarterly":
                df = ticker.balance_sheet
            else:
                df = ticker.quarterly_balance_sheet

            if df.empty:
                return {}

            latest = df.iloc[:, 0]
            return {
                "period": df.columns[0].strftime("%Y-%m-%d"),
                "total_assets": float(latest.get("Total Assets", 0)),
                "total_liab": float(latest.get("Total Liab", 0)),
                "total_stockholder_equity": float(latest.get("Total Stockholder Equity", 0)),
                "cash": float(latest.get("Cash And Cash Equivalents", 0)),
                "net_receivables": float(latest.get("Net Receivables", 0)),
                "inventory": float(latest.get("Inventory", 0)),
                "total_debt": float(latest.get("Total Debt", 0)),
            }

        return await loop.run_in_executor(None, _get)

    async def _fetch_cash_flow(self, ticker, period: str) -> dict:
        """获取现金流量表"""
        loop = asyncio.get_event_loop()

        def _get():
            if period == "quarterly":
                df = ticker.cashflow
            else:
                df = ticker.quarterly_cashflow

            if df.empty:
                return {}

            latest = df.iloc[:, 0]
            return {
                "period": df.columns[0].strftime("%Y-%m-%d"),
                "operating_cashflow": float(latest.get("Operating Cash Flow", 0)),
                "capital_expenditure": float(latest.get("Capital Expenditure", 0)),
                "free_cashflow": float(latest.get("Free Cash Flow", 0)),
                "dividends_paid": float(latest.get("Dividends Paid", 0)),
            }

        return await loop.run_in_executor(None, _get)

    async def _fetch_ratios(self, ticker) -> dict:
        """获取财务比率"""
        loop = asyncio.get_event_loop()

        def _get():
            info = ticker.info

            return {
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "pb_ratio": info.get("priceToBook"),
                "ps_ratio": info.get("priceToSalesTrailing12Months"),
                "ev_to_ebitda": info.get("enterpriseToEbitda"),
                "profit_margin": info.get("profitMargins"),
                "operating_margin": info.get("operatingMargins"),
                "roe": info.get("returnOnEquity"),
                "roa": info.get("returnOnAssets"),
                "debt_to_equity": info.get("debtToEquity"),
                "current_ratio": info.get("currentRatio"),
                "quick_ratio": info.get("quickRatio"),
            }

        return await loop.run_in_executor(None, _get)

    async def _fetch_metrics(self, ticker) -> dict:
        """获取估值指标"""
        loop = asyncio.get_event_loop()

        def _get():
            info = ticker.info

            return {
                "market_cap": info.get("marketCap"),
                "enterprise_value": info.get("enterpriseValue"),
                "trailing_eps": info.get("trailingEps"),
                "forward_eps": info.get("forwardEps"),
                "peg_ratio": info.get("pegRatio"),
                "beta": info.get("beta"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "avg_volume": info.get("averageVolume"),
                "shares_outstanding": info.get("sharesOutstanding"),
                "dividend_yield": info.get("dividendYield"),
                "dividend_rate": info.get("dividendRate"),
            }

        return await loop.run_in_executor(None, _get)

    async def _fetch_estimates(self, ticker) -> dict:
        """获取分析师预期"""
        loop = asyncio.get_event_loop()

        def _get():
            info = ticker.info

            return {
                "target_high_price": info.get("targetHighPrice"),
                "target_low_price": info.get("targetLowPrice"),
                "target_mean_price": info.get("targetMeanPrice"),
                "target_median_price": info.get("targetMedianPrice"),
                "recommendation": info.get("recommendationKey"),
                "number_of_analysts": info.get("numberOfAnalystOpinions"),
                "current_price": info.get("currentPrice"),
            }

        return await loop.run_in_executor(None, _get)

    async def fetch_latest(self, symbols: List[str]) -> Dict[str, dict]:
        """获取最新财务数据（便捷方法）"""
        return await self.fetch(
            symbols,
            data_types=["income_statement", "balance_sheet", "cash_flow", "ratios", "metrics"],
            period="quarterly",
        )
