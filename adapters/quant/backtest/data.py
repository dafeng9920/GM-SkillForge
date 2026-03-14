"""
历史数据适配器

支持的数据源：
- yfinance: 免费美股数据
- 本地CSV文件
- 未来可扩展：Alpha Vantage, Polygon.io 等
"""

from datetime import datetime, timedelta
from typing import List, Optional
import logging

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

from ..backtest.events import TickEvent

logger = logging.getLogger(__name__)


class HistoricalDataAdapter:
    """
    历史数据适配器

    功能：
    1. 从数据源获取历史K线数据
    2. 转换为Tick事件
    3. 支持多个数据源
    """

    def __init__(self, source: str = "yfinance"):
        """
        初始化数据适配器

        Args:
            source: 数据源 (yfinance, csv)
        """
        self.source = source

        if source == "yfinance" and not YFINANCE_AVAILABLE:
            raise ImportError("yfinance 未安装，请运行: pip install yfinance")

        logger.info(f"数据适配器初始化: source={source}")

    def fetch_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1h",  # 1m, 5m, 15m, 1h, 1d
    ) -> List[TickEvent]:
        """
        获取历史数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            interval: K线周期

        Returns:
            TickEvent列表
        """
        if self.source == "yfinance":
            return self._fetch_yfinance(symbol, start_date, end_date, interval)
        else:
            raise ValueError(f"不支持的数据源: {self.source}")

    def _fetch_yfinance(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str,
    ) -> List[TickEvent]:
        """从 yfinance 获取数据"""
        logger.info(f"获取 {symbol} 数据: {start_date.date()} 至 {end_date.date()}, interval={interval}")

        # 下载历史数据
        ticker = yf.Ticker(symbol)
        df = ticker.history(
            start=start_date,
            end=end_date,
            interval=interval,
            prepost=False,  # 不包含盘前盘后
        )

        if df.empty:
            logger.warning(f"未获取到数据: {symbol}")
            return []

        # 转换为Tick事件
        events = []
        for timestamp, row in df.iterrows():
            # 使用收盘价作为价格
            price = row['Close']
            volume = int(row['Volume']) if 'Volume' in row else 0

            event = TickEvent(
                symbol=symbol,
                timestamp=timestamp.to_pydatetime(),
                price=price,
                volume=volume,
                bid=row['Low'],   # 简化：使用最低价作为买价
                ask=row['High'],   # 简化：使用最高价作为卖价
            )
            events.append(event)

        logger.info(f"获取到 {len(events)} 条数据")
        return events

    def fetch_multiple_symbols(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        interval: str = "1h",
    ) -> List[TickEvent]:
        """
        获取多个股票的数据

        Returns:
            合并并排序的Tick事件列表
        """
        all_events = []

        for symbol in symbols:
            try:
                events = self.fetch_data(symbol, start_date, end_date, interval)
                all_events.extend(events)
            except Exception as e:
                logger.error(f"获取 {symbol} 数据失败: {e}")

        # 按时间排序
        all_events.sort(key=lambda x: x.timestamp)

        return all_events


def get_test_data(symbol: str = "AAPL", days: int = 30) -> List[TickEvent]:
    """
    获取测试数据（快捷方法）

    Args:
        symbol: 股票代码
        days: 天数

    Returns:
        TickEvent列表
    """
    if not YFINANCE_AVAILABLE:
        logger.error("yfinance 未安装，无法获取测试数据")
        return []

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    adapter = HistoricalDataAdapter(source="yfinance")
    return adapter.fetch_data(symbol, start_date, end_date, interval="1h")
