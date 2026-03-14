"""
A股数据获取模块 - China Stock Data Fetcher

支持多个数据源：
1. Tushare (推荐，需要token)
2. AKShare (免费，无需注册)
3. Baostock (免费，需要注册)

版本: 1.0.0
创建日期: 2026-03-09
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Union
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


# ============================================
# 数据模型
# ============================================

@dataclass
class StockQuote:
    """股票报价"""
    symbol: str           # 股票代码 (e.g., "600519.SH")
    name: str             # 股票名称
    timestamp: datetime   # 时间戳
    open: float           # 开盘价
    high: float           # 最高价
    low: float            # 最低价
    close: float          # 收盘价
    volume: float         # 成交量
    amount: float         # 成交额
    turnover: float = 0   # 换手率
    pe_ratio: float = 0   # 市盈率
    market_cap: float = 0 # 总市值


@dataclass
class StockInfo:
    """股票基本信息"""
    symbol: str
    name: str
    industry: str = ""
    market: str = ""       # SH/SZ
    list_date: str = ""
    is_active: bool = True


@dataclass
class MarketSnapshot:
    """市场快照"""
    timestamp: datetime
    index_data: Dict[str, StockQuote]  # 指数数据
    stock_data: Dict[str, StockQuote]  # 个股数据
    market_sentiment: Dict             # 市场情绪


# ============================================
# 数据源接口
# ============================================

class DataSource:
    """数据源基类"""

    def get_stock_list(self) -> List[StockInfo]:
        """获取股票列表"""
        raise NotImplementedError

    def get_daily_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        adjust: str = "qfq"  # qfq-前复权, hfq-后复权, ""-不复权
    ) -> pd.DataFrame:
        """获取日线数据"""
        raise NotImplementedError

    def get_realtime_quote(self, symbols: List[str]) -> Dict[str, StockQuote]:
        """获取实时行情"""
        raise NotImplementedError


# ============================================
# AKShare 数据源（免费，推荐）
# ============================================

class AKShareSource(DataSource):
    """AKShare 数据源 - 免费，无需注册"""

    def __init__(self):
        try:
            import akshare as ak
            self.ak = ak
            logger.info("AKShare 数据源初始化成功")
        except ImportError:
            logger.warning("AKShare 未安装，请运行: pip install akshare")
            self.ak = None

    def get_stock_list(self) -> List[StockInfo]:
        """获取A股股票列表"""
        if not self.ak:
            raise ImportError("AKShare 未安装")

        try:
            # 获取沪深A股列表
            sh_stocks = self.ak.stock_info_sh_name_code(indicator="主板A股")
            sz_stocks = self.ak.stock_info_sz_name_code(indicator="A股列表")

            stocks = []

            # 处理上交所股票
            for _, row in sh_stocks.iterrows():
                stocks.append(StockInfo(
                    symbol=f"{row['证券代码']}.SH",
                    name=row['证券简称'],
                    market="SH",
                    is_active=True
                ))

            # 处理深交所股票
            for _, row in sz_stocks.iterrows():
                if not pd.isna(row.get('A股代码', '')):
                    stocks.append(StockInfo(
                        symbol=f"{row['A股代码']}.SZ",
                        name=row['A股简称'],
                        market="SZ",
                        is_active=True
                    ))

            logger.info(f"获取到 {len(stocks)} 只A股股票")
            return stocks

        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return []

    def get_daily_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        adjust: str = "qfq"
    ) -> pd.DataFrame:
        """获取日线数据"""
        if not self.ak:
            raise ImportError("AKShare 未安装")

        try:
            # 解析股票代码
            code, market = self._parse_symbol(symbol)

            # AKShare 获取历史数据
            if adjust == "qfq":
                df = self.ak.stock_zh_a_hist(
                    symbol=code,
                    period="daily",
                    start_date=start_date.replace("-", ""),
                    end_date=end_date.replace("-", ""),
                    adjust="qfq"
                )
            else:
                df = self.ak.stock_zh_a_hist(
                    symbol=code,
                    period="daily",
                    start_date=start_date.replace("-", ""),
                    end_date=end_date.replace("-", ""),
                    adjust=""
                )

            if df.empty:
                return pd.DataFrame()

            # 标准化列名
            df = df.rename(columns={
                "日期": "date",
                "开盘": "open",
                "最高": "high",
                "最低": "low",
                "收盘": "close",
                "成交量": "volume",
                "成交额": "amount",
                "换手率": "turnover"
            })

            df["symbol"] = symbol
            df["date"] = pd.to_datetime(df["date"])

            return df[["symbol", "date", "open", "high", "low", "close", "volume", "amount", "turnover"]]

        except Exception as e:
            logger.error(f"获取 {symbol} 数据失败: {e}")
            return pd.DataFrame()

    def get_realtime_quote(self, symbols: List[str]) -> Dict[str, StockQuote]:
        """获取实时行情"""
        if not self.ak:
            raise ImportError("AKShare 未安装")

        try:
            # 获取实时行情
            df = self.ak.stock_zh_a_spot_em()

            quotes = {}
            for symbol in symbols:
                code, _ = self._parse_symbol(symbol)

                # 查找对应股票
                stock_data = df[df["代码"] == code]

                if not stock_data.empty:
                    row = stock_data.iloc[0]
                    quotes[symbol] = StockQuote(
                        symbol=symbol,
                        name=row["名称"],
                        timestamp=datetime.now(),
                        open=float(row["今开"]),
                        high=float(row["最高"]),
                        low=float(row["最低"]),
                        close=float(row["最新价"]),
                        volume=float(row["成交量"]),
                        amount=float(row["成交额"]),
                        turnover=float(row.get("换手率", 0)),
                        pe_ratio=float(row.get("市盈率-动态", 0)),
                        market_cap=float(row.get("总市值", 0))
                    )

            return quotes

        except Exception as e:
            logger.error(f"获取实时行情失败: {e}")
            return {}

    def _parse_symbol(self, symbol: str) -> tuple:
        """解析股票代码"""
        if "." in symbol:
            code, market = symbol.split(".")
            return code, market
        else:
            return symbol, "SH"


# ============================================
# Tushare 数据源（需要token）
# ============================================

class TushareSource(DataSource):
    """Tushare 数据源 - 需要token，数据质量高"""

    def __init__(self, token: Optional[str] = None):
        try:
            import tushare as ts
            self.ts = ts
            self.token = token
            if token:
                ts.set_token(token)
                self.pro = ts.pro_api()
                logger.info("Tushare 数据源初始化成功")
            else:
                logger.warning("Tushare token 未设置")
                self.pro = None
        except ImportError:
            logger.warning("Tushare 未安装，请运行: pip install tushare")
            self.ts = None
            self.pro = None

    def get_daily_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        adjust: str = "qfq"
    ) -> pd.DataFrame:
        """获取日线数据"""
        if not self.pro:
            raise ImportError("Tushare 未初始化")

        try:
            # Tushare 使用 ts_code 格式 (e.g., "600519.SH")
            ts_code = symbol

            # 获取日线数据
            df = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", "")
            )

            if df.empty:
                return pd.DataFrame()

            # 如果需要复权数据
            if adjust == "qfq":
                adj_df = self.pro.daily_basic(
                    ts_code=ts_code,
                    start_date=start_date.replace("-", ""),
                    end_date=end_date.replace("-", ""),
                    fields='ts_code,trade_date,turnover_rate,volume_ratio,pe,pb'
                )
                # 这里可以添加复权计算逻辑
                # 简化处理：直接返回原数据
            elif adjust == "hfq":
                # 后复权处理
                pass

            # 标准化列名
            df = df.rename(columns={
                "trade_date": "date",
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close",
                "vol": "volume",
                "amount": "amount"
            })

            df["symbol"] = symbol
            df["date"] = pd.to_datetime(df["date"])

            return df[["symbol", "date", "open", "high", "low", "close", "volume", "amount"]]

        except Exception as e:
            logger.error(f"获取 {symbol} 数据失败: {e}")
            return pd.DataFrame()


# ============================================
# A股数据管理器
# ============================================

class ChinaStockDataFetcher:
    """
    A股数据管理器

    支持多数据源自动切换，优先使用可用的数据源
    """

    def __init__(self, preferred_source: str = "akshare"):
        """
        初始化数据管理器

        Args:
            preferred_source: 首选数据源 ("akshare", "tushare", "baostock")
        """
        self.sources = []
        self.preferred_source = preferred_source

        # 初始化数据源
        self._init_sources()

    def _init_sources(self):
        """初始化可用数据源"""
        # 优先使用 AKShare（免费）
        try:
            akshare_source = AKShareSource()
            # 测试是否可用
            if akshare_source.ak is not None:
                self.sources.append(("akshare", akshare_source))
                logger.info("AKShare 数据源已就绪")
        except Exception as e:
            logger.warning(f"AKShare 不可用: {e}")

        # 如果设置了 Tushare token
        # tushare_token = os.getenv("TUSHARE_TOKEN")
        # if tushare_token:
        #     try:
        #         tushare_source = TushareSource(token=tushare_token)
        #         self.sources.append(("tushare", tushare_source))
        #         logger.info("Tushare 数据源已就绪")
        #     except Exception as e:
        #         logger.warning(f"Tushare 不可用: {e}")

        if not self.sources:
            raise RuntimeError("没有可用的数据源，请安装 akshare: pip install akshare")

    def _get_source(self, source_name: Optional[str] = None) -> DataSource:
        """获取指定数据源"""
        if source_name:
            for name, source in self.sources:
                if name == source_name:
                    return source
            raise ValueError(f"数据源 {source_name} 不可用")

        # 使用首选数据源
        for name, source in self.sources:
            if name == self.preferred_source:
                return source

        # 使用第一个可用数据源
        return self.sources[0][1]

    def get_stock_list(self, source: Optional[str] = None) -> List[StockInfo]:
        """获取股票列表"""
        src = self._get_source(source)
        return src.get_stock_list()

    def get_daily_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: Optional[str] = None,
        adjust: str = "qfq",
        source: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取日线数据

        Args:
            symbol: 股票代码 (e.g., "600519.SH", "000001.SZ")
            start_date: 开始日期 (e.g., "2024-01-01")
            end_date: 结束日期，默认为今天
            adjust: 复权类型 ("qfq"-前复权, "hfq"-后复权, ""-不复权)
            source: 数据源名称

        Returns:
            包含日线数据的DataFrame
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        src = self._get_source(source)
        return src.get_daily_bars(symbol, start_date, end_date, adjust)

    def get_realtime_quotes(
        self,
        symbols: List[str],
        source: Optional[str] = None
    ) -> Dict[str, StockQuote]:
        """获取实时行情"""
        src = self._get_source(source)
        return src.get_realtime_quote(symbols)

    def get_historical_data_for_strategy(
        self,
        symbol: str,
        days: int = 252,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取策略所需的历史数据

        Args:
            symbol: 股票代码
            days: 历史天数（默认252个交易日，约1年）
            end_date: 结束日期

        Returns:
            包含历史数据的DataFrame
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        start_date = (datetime.now() - timedelta(days=days*2)).strftime("%Y-%m-%d")

        df = self.get_daily_bars(symbol, start_date, end_date, adjust="qfq")

        if not df.empty:
            # 只返回最近 days 天的数据
            df = df.tail(days).reset_index(drop=True)

        return df


# ============================================
# 便捷函数
# ============================================

def get_popular_stocks() -> List[str]:
    """获取热门股票代码"""
    return [
        "600519.SH",  # 贵州茅台
        "000001.SZ",  # 平安银行
        "000002.SZ",  # 万科A
        "600030.SH",  # 中信证券
        "600036.SH",  # 招商银行
        "601318.SH",  # 中国平安
        "600276.SH",  # 恒瑞医药
        "300750.SZ",  # 宁德时代
        "002594.SZ",  # 比亚迪
        "600900.SH",  # 长江电力
    ]


# ============================================
# CLI 测试
# ============================================

def main():
    """测试数据获取"""
    print("=" * 70)
    print("  A股数据获取测试")
    print("=" * 70)

    # 创建数据管理器
    fetcher = ChinaStockDataFetcher(preferred_source="akshare")

    # 测试股票代码
    test_symbol = "600519.SH"  # 贵州茅台

    print(f"\n获取 {test_symbol} 历史数据...")

    # 获取最近30天数据
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")

    df = fetcher.get_daily_bars(test_symbol, start_date, end_date)

    if not df.empty:
        print(f"\n获取到 {len(df)} 条数据")
        print("\n最新5条数据:")
        print(df[["date", "open", "high", "low", "close", "volume"]].tail().to_string(index=False))

        print("\n数据统计:")
        print(f"  时间范围: {df['date'].min()} 至 {df['date'].max()}")
        print(f"  收盘价范围: {df['close'].min():.2f} - {df['close'].max():.2f}")
        print(f"  平均成交量: {df['volume'].mean():.0f}")
    else:
        print("未获取到数据")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
