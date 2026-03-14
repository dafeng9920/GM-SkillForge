"""
交易记录持久化模块 - Trade Journal

完整的交易日志系统，记录每一笔交易的详细信息，支持：
- 交易记录保存到JSON文件
- 每日快照保存
- 绩效分析
- 历史回溯

版本: 1.0.0
创建日期: 2026-03-09
"""

import json
import os
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
import pandas as pd


# ============================================
# 数据模型
# ============================================

@dataclass
class DailySnapshot:
    """每日快照"""
    date: str
    timestamp: str
    total_asset: float
    cash: float
    market_value: float
    positions_count: int
    total_pnl: float
    total_pnl_pct: float
    positions: List[dict] = field(default_factory=list)
    pending_orders: int = 0
    today_trades: int = 0


@dataclass
class TradeRecord:
    """交易记录"""
    trade_id: str
    order_id: str
    symbol: str
    side: str                    # BUY/SELL
    quantity: int
    price: float
    commission: float
    stamp_duty: float = 0
    trade_time: str = ""
    pnl: float = 0               # 已实现盈亏


@dataclass
class PerformanceMetrics:
    """绩效指标"""
    date: str
    total_return: float          # 总收益率
    daily_return: float          # 日收益率
    win_rate: float              # 胜率
    profit_factor: float         # 盈亏比
    max_drawdown: float          # 最大回撤
    sharpe_ratio: float = 0      # 夏普比率
    total_trades: int = 0        # 总交易次数
    winning_trades: int = 0      # 盈利交易次数
    losing_trades: int = 0       # 亏损交易次数


# ============================================
# 交易日志
# ============================================

class TradeJournal:
    """
    交易日志系统

    记录所有交易信息，提供查询和分析功能
    """

    def __init__(self, data_dir: str = "trading_data"):
        """
        初始化交易日志

        Args:
            data_dir: 数据保存目录
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 子目录
        self.snapshots_dir = self.data_dir / "snapshots"
        self.trades_dir = self.data_dir / "trades"
        self.reports_dir = self.data_dir / "reports"

        for dir_path in [self.snapshots_dir, self.trades_dir, self.reports_dir]:
            dir_path.mkdir(exist_ok=True)

        # 内存缓存
        self.daily_snapshots: List[DailySnapshot] = []
        self.trade_records: List[TradeRecord] = []

        # 加载历史数据
        self._load_historical_data()

        print(f"✓ 交易日志系统初始化完成")
        print(f"  数据目录: {self.data_dir.absolute()}")

    def _load_historical_data(self):
        """加载历史数据"""
        # 加载最近的快照
        snapshot_file = self._get_snapshot_file()
        if snapshot_file.exists():
            try:
                with open(snapshot_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.daily_snapshots = [
                        DailySnapshot(**s) for s in data.get('snapshots', [])
                    ]
                print(f"  ✓ 已加载 {len(self.daily_snapshots)} 条历史快照")
            except Exception as e:
                print(f"  ⚠ 加载快照失败: {e}")

        # 加载交易记录
        trades_file = self._get_trades_file()
        if trades_file.exists():
            try:
                with open(trades_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.trade_records = [
                        TradeRecord(**t) for t in data.get('trades', [])
                    ]
                print(f"  ✓ 已加载 {len(self.trade_records)} 条交易记录")
            except Exception as e:
                print(f"  ⚠ 加载交易记录失败: {e}")

    def _get_snapshot_file(self) -> Path:
        """获取快照文件路径"""
        today = date.today().strftime("%Y-%m")
        return self.snapshots_dir / f"snapshots_{today}.json"

    def _get_trades_file(self) -> Path:
        """获取交易记录文件路径"""
        today = date.today().strftime("%Y-%m")
        return self.trades_dir / f"trades_{today}.json"

    def save_daily_snapshot(self, snapshot: dict):
        """
        保存每日快照

        Args:
            snapshot: 快照数据（从broker.get_daily_snapshot()获取）
        """
        daily_snapshot = DailySnapshot(
            date=snapshot['date'],
            timestamp=snapshot['time'],
            total_asset=snapshot['account']['total_asset'],
            cash=snapshot['account']['cash'],
            market_value=snapshot['account']['market_value'],
            positions_count=snapshot['account']['positions'],
            total_pnl=snapshot['account']['total_pnl'],
            total_pnl_pct=snapshot['account']['total_pnl_pct'],
            positions=snapshot.get('positions', []),
            pending_orders=snapshot.get('pending_orders', 0),
            today_trades=snapshot.get('today_trades', 0)
        )

        # 添加到内存
        self.daily_snapshots.append(daily_snapshot)

        # 保存到文件
        snapshot_file = self._get_snapshot_file()
        data = {
            'last_update': datetime.now().isoformat(),
            'snapshots': [asdict(s) for s in self.daily_snapshots]
        }

        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ 快照已保存: {daily_snapshot.date}")

    def save_trade(self, trade: dict):
        """
        保存交易记录

        Args:
            trade: 交易数据
        """
        trade_record = TradeRecord(
            trade_id=trade.get('trade_id', ''),
            order_id=trade.get('order_id', ''),
            symbol=trade.get('symbol', ''),
            side=trade.get('side', ''),
            quantity=trade.get('quantity', 0),
            price=trade.get('price', 0),
            commission=trade.get('commission', 0),
            stamp_duty=trade.get('stamp_duty', 0),
            trade_time=trade.get('trade_time', datetime.now().isoformat()),
            pnl=trade.get('pnl', 0)
        )

        # 添加到内存
        self.trade_records.append(trade_record)

        # 保存到文件
        trades_file = self._get_trades_file()
        data = {
            'last_update': datetime.now().isoformat(),
            'trades': [asdict(t) for t in self.trade_records]
        }

        with open(trades_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ 交易已保存: {trade_record.symbol} {trade_record.side} {trade_record.quantity}股")

    def get_performance_summary(self) -> dict:
        """获取绩效摘要"""
        if not self.daily_snapshots:
            return {
                'total_snapshots': 0,
                'total_trades': len(self.trade_records),
                'latest_equity': 0,
                'total_return': 0,
                'max_drawdown': 0,
                'win_rate': 0,
                'sharpe_ratio': 0
            }

        # 转换为DataFrame进行分析
        df = pd.DataFrame([asdict(s) for s in self.daily_snapshots])

        # 计算绩效指标
        if len(df) > 0:
            initial_equity = df.iloc[0]['total_asset']
            latest_equity = df.iloc[-1]['total_asset']
            total_return = (latest_equity / initial_equity - 1) * 100

            # 计算最大回撤
            df['cummax'] = df['total_asset'].cummax()
            df['drawdown'] = (df['total_asset'] / df['cummax'] - 1) * 100
            max_drawdown = df['drawdown'].min()

            # 计算日收益率
            df['daily_return'] = df['total_asset'].pct_change() * 100
            avg_daily_return = df['daily_return'].mean()
            std_daily_return = df['daily_return'].std()

            # 夏普比率（年化）
            sharpe_ratio = 0
            if std_daily_return > 0:
                sharpe_ratio = (avg_daily_return / std_daily_return) * (252 ** 0.5)
        else:
            latest_equity = 0
            total_return = 0
            max_drawdown = 0
            sharpe_ratio = 0

        # 交易统计
        if self.trade_records:
            # 计算胜率
            winning_trades = [t for t in self.trade_records if t.pnl > 0]
            losing_trades = [t for t in self.trade_records if t.pnl < 0]
            win_rate = len(winning_trades) / len(self.trade_records) * 100

            # 盈亏比
            total_profit = sum(t.pnl for t in winning_trades) if winning_trades else 0
            total_loss = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 1
            profit_factor = total_profit / total_loss if total_loss > 0 else 0
        else:
            win_rate = 0
            profit_factor = 0

        return {
            'total_snapshots': len(self.daily_snapshots),
            'total_trades': len(self.trade_records),
            'latest_equity': latest_equity,
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio
        }

    def export_trade_report(self, output_file: Optional[str] = None) -> str:
        """
        导出交易报告

        Args:
            output_file: 输出文件路径

        Returns:
            报告文件路径
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.reports_dir / f"trade_report_{timestamp}.json"

        # 生成完整报告
        report = {
            'generated_at': datetime.now().isoformat(),
            'performance': self.get_performance_summary(),
            'daily_snapshots': [asdict(s) for s in self.daily_snapshots[-30:]],  # 最近30天
            'trade_records': [asdict(t) for t in self.trade_records[-100:]],     # 最近100笔
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"✓ 交易报告已导出: {output_file}")
        return str(output_file)

    def get_equity_curve(self) -> pd.DataFrame:
        """获取资金曲线"""
        if not self.daily_snapshots:
            return pd.DataFrame()

        df = pd.DataFrame([asdict(s) for s in self.daily_snapshots])
        df['date'] = pd.to_datetime(df['date'])
        return df[['date', 'total_asset', 'cash', 'market_value', 'total_pnl']]

    def get_trades_dataframe(self) -> pd.DataFrame:
        """获取交易记录DataFrame"""
        if not self.trade_records:
            return pd.DataFrame()

        df = pd.DataFrame([asdict(t) for t in self.trade_records])
        df['trade_time'] = pd.to_datetime(df['trade_time'])
        return df

    def print_summary(self):
        """打印摘要信息"""
        print("\n" + "=" * 70)
        print("  交易日志摘要")
        print("=" * 70)

        perf = self.get_performance_summary()

        print(f"\n📊 绩效指标:")
        print(f"  总收益率: {perf['total_return']:+.2f}%")
        print(f"  最大回撤: {perf['max_drawdown']:.2f}%")
        print(f"  夏普比率: {perf['sharpe_ratio']:.2f}")
        print(f"  最新净值: ¥{perf['latest_equity']:,.2f}")

        print(f"\n📈 交易统计:")
        print(f"  总交易次数: {perf['total_trades']}")
        print(f"  胜率: {perf['win_rate']:.1f}%")
        print(f"  盈亏比: {perf['profit_factor']:.2f}")

        print(f"\n📁 数据文件:")
        print(f"  快照目录: {self.snapshots_dir}")
        print(f"  交易记录: {self.trades_dir}")
        print(f"  报告目录: {self.reports_dir}")

        print("=" * 70)


# ============================================
# CLI 测试
# ============================================

def main():
    """测试交易日志"""
    print("=" * 70)
    print("  交易日志系统测试")
    print("=" * 70)

    # 创建交易日志
    journal = TradeJournal(data_dir="test_trading_data")

    # 模拟快照
    test_snapshot = {
        'date': '2026-03-09',
        'time': '15:00:00',
        'account': {
            'total_asset': 1050000,
            'cash': 500000,
            'market_value': 550000,
            'positions': 2,
            'total_pnl': 50000,
            'total_pnl_pct': 5.0
        },
        'positions': [
            {
                'symbol': '600519.SH',
                'quantity': 100,
                'avg_price': 1500,
                'current_price': 1550,
                'market_value': 155000,
                'unrealized_pnl': 5000,
                'unrealized_pnl_pct': 3.33
            }
        ],
        'pending_orders': 0,
        'today_trades': 2
    }

    journal.save_daily_snapshot(test_snapshot)

    # 模拟交易
    test_trade = {
        'trade_id': 'TRADE000001',
        'order_id': 'ORDER001',
        'symbol': '600519.SH',
        'side': 'BUY',
        'quantity': 100,
        'price': 1500,
        'commission': 45,
        'stamp_duty': 0,
        'trade_time': '2026-03-09T10:30:00',
        'pnl': 0
    }

    journal.save_trade(test_trade)

    # 打印摘要
    journal.print_summary()

    # 导出报告
    journal.export_trade_report()


if __name__ == "__main__":
    main()
