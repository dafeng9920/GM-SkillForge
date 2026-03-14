"""
A股量化交易系统 - 完整演示脚本

展示系统所有核心功能的演示

使用方法:
    python demo_trading_system.py
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from adapters.quant.trading.simulated_broker import SimulatedBroker, OrderSide, OrderType
from adapters.quant.trading.trade_journal import TradeJournal
from adapters.quant.trading.trading_dashboard import TradingDashboard
from adapters.quant.data.china_stock_fetcher import ChinaStockDataFetcher, get_popular_stocks


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def demo_broker():
    """演示模拟券商功能"""
    print_section("📊 模拟券商演示")

    # 创建模拟券商
    broker = SimulatedBroker(initial_capital=1000000)
    broker.connect_data_source()

    # 显示账户信息
    print("\n📋 账户信息:")
    account = broker.get_account_info()
    print(f"  总资产: ¥{account['total_asset']:,.2f}")
    print(f"  现金: ¥{account['cash']:,.2f}")
    print(f"  持仓数: {account['positions']}")

    # 模拟下单（使用测试价格）
    print("\n📝 测试下单:")
    print("  下单: 600519.SH 买入 100股 @ ¥1500.00")

    order = broker.place_order(
        symbol="600519.SH",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=100,
        price=1500.0
    )

    print(f"  订单状态: {order.status.value}")
    print(f"  订单ID: {order.order_id}")

    # 撤销订单
    if order.status.value == "pending":
        print("\n❌ 撤销订单:")
        broker.cancel_order(order.order_id)

    return broker


def demo_data_fetcher():
    """演示数据获取功能"""
    print_section("📡 数据获取演示")

    # 创建数据获取器
    fetcher = ChinaStockDataFetcher(preferred_source="akshare")

    # 测试股票
    test_symbol = "600519.SH"  # 贵州茅台

    print(f"\n获取 {test_symbol} 历史数据...")

    from datetime import datetime, timedelta
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    df = fetcher.get_daily_bars(test_symbol, start_date, end_date)

    if not df.empty:
        print(f"\n✓ 获取到 {len(df)} 条数据")
        print("\n最新数据:")
        print(df[["date", "open", "high", "low", "close", "volume"]].tail().to_string(index=False))
    else:
        print("\n✗ 未获取到数据")

    # 获取实时行情
    print(f"\n获取实时行情...")
    quotes = fetcher.get_realtime_quotes([test_symbol])

    if test_symbol in quotes:
        quote = quotes[test_symbol]
        print(f"\n✓ {quote.name} ({test_symbol})")
        print(f"  最新价: ¥{quote.close:.2f}")
        print(f"  涨跌: {(quote.close / quote.open - 1) * 100:+.2f}%")
        print(f"  成交量: {quote.volume:,.0f}")


def demo_trade_journal():
    """演示交易日志功能"""
    print_section("📔 交易日志演示")

    # 创建交易日志
    journal = TradeJournal(data_dir="demo_trading_data")

    # 创建测试快照
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
            },
            {
                'symbol': '000001.SZ',
                'quantity': 1000,
                'avg_price': 12,
                'current_price': 12.5,
                'market_value': 12500,
                'unrealized_pnl': 500,
                'unrealized_pnl_pct': 4.17
            }
        ],
        'pending_orders': 0,
        'today_trades': 2
    }

    # 保存快照
    print("\n💾 保存每日快照...")
    journal.save_daily_snapshot(test_snapshot)

    # 创建测试交易
    test_trade = {
        'trade_id': 'DEMO001',
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

    print("\n💾 保存交易记录...")
    journal.save_trade(test_trade)

    # 显示绩效摘要
    print("\n📊 绩效摘要:")
    journal.print_summary()

    # 导出报告
    print("\n📄 导出交易报告...")
    report_file = journal.export_trade_report()
    print(f"✓ 报告已保存: {report_file}")


def demo_dashboard():
    """演示监控仪表板功能"""
    print_section("🖥️ 监控仪表板演示")

    # 创建模拟券商
    broker = SimulatedBroker(initial_capital=1000000)
    broker.connect_data_source()

    # 创建交易日志
    journal = TradeJournal(data_dir="demo_dashboard_data")

    # 创建仪表板
    dashboard = TradingDashboard(broker, journal)

    print("\n📊 渲染仪表板...")
    dashboard.render()

    print("\n✓ 仪表板演示完成")


def demo_complete_workflow():
    """演示完整工作流程"""
    print_section("🚀 完整工作流程演示")

    from adapters.quant.trading.quant_trading_system import QuantTradingSystem

    print("\n📦 初始化交易系统...")

    # 创建交易系统
    system = QuantTradingSystem(
        initial_capital=1000000,
        symbols=get_popular_stocks()[:3],  # 只取前3只股票
        data_dir="demo_system_data"
    )

    print("\n📈 加载历史数据...")
    system.load_historical_data(days=60)  # 只加载60天数据

    print("\n🎯 运行一次交易周期...")
    signals = system.run_once()

    print("\n📊 系统报告:")
    report = system.get_report()

    print(f"\n  账户总资产: ¥{report['account']['total_asset']:,.2f}")
    print(f"  总盈亏: ¥{report['account']['total_pnl']:+,.2f} ({report['account']['total_pnl_pct']:+.2f}%)")
    print(f"  持仓数: {report['positions']}")
    print(f"  交易次数: {report['total_trades']}")

    print("\n✓ 完整工作流程演示完成")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("  🚀 A股量化交易系统 - 完整演示")
    print("=" * 80)

    demos = [
        ("数据获取", demo_data_fetcher),
        ("模拟券商", demo_broker),
        ("交易日志", demo_trade_journal),
        ("监控仪表板", demo_dashboard),
        ("完整工作流程", demo_complete_workflow),
    ]

    print("\n📋 演示列表:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")

    print("\n运行所有演示...\n")

    try:
        for name, demo_func in demos:
            try:
                demo_func()
            except Exception as e:
                print(f"\n⚠️ {name} 演示出错: {e}")
                continue

        print("\n" + "=" * 80)
        print("  ✅ 所有演示完成！")
        print("=" * 80)

        print("\n📚 下一步:")
        print("  1. 运行一次交易: python adapters/quant/trading/start_trading.py --once")
        print("  2. 启动Web界面: python adapters/quant/trading/start_trading.py --web")
        print("  3. 查看完整文档: adapters/quant/README_TRADING_SYSTEM.md")

    except KeyboardInterrupt:
        print("\n\n⚠️ 演示被中断")
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
