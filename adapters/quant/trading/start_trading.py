"""
A股量化交易系统 - 快速启动脚本

使用方法:
    python start_trading.py --help

示例:
    # 使用默认配置运行一次
    python start_trading.py --once

    # 自动交易模式（每60秒刷新一次）
    python start_trading.py

    # 自定义初始资金和股票
    python start_trading.py --capital 500000 --symbols 600519.SH 000001.SZ

    # Web监控模式
    python start_trading.py --web
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from adapters.quant.trading.quant_trading_system import QuantTradingSystem


def run_cli_mode(args):
    """命令行模式"""
    print("\n" + "=" * 80)
    print("  🚀 A股量化交易系统 - CLI模式")
    print("=" * 80)

    # 创建交易系统
    system = QuantTradingSystem(
        initial_capital=args.capital,
        symbols=args.symbols,
        data_dir=args.data_dir
    )

    # 加载历史数据
    system.load_historical_data(days=120)

    # 运行
    if args.once:
        system.run_once()
    else:
        system.run_auto(interval_seconds=args.interval)


def run_web_mode():
    """Web监控模式"""
    print("\n" + "=" * 80)
    print("  🚀 A股量化交易系统 - Web监控模式")
    print("=" * 80)
    print("\n正在启动Web界面...")
    print("浏览器将自动打开，或手动访问 http://localhost:8501\n")

    try:
        import streamlit.web.cli as stcli
    except ImportError:
        print("❌ 错误: streamlit 未安装")
        print("\n请安装以下依赖:")
        print("  pip install streamlit plotly")
        return

    # 获取web_monitor.py的路径
    web_monitor_path = Path(__file__).parent / "web_monitor.py"

    # 设置streamlit参数
    sys.argv = [
        "streamlit",
        "run",
        str(web_monitor_path),
        "--server.port=8501",
        "--server.address=localhost"
    ]

    stcli.main()


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='A股量化交易系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python start_trading.py --once                      # 运行一次
  python start_trading.py                             # 自动交易模式
  python start_trading.py --web                       # Web监控模式
  python start_trading.py --capital 500000            # 自定义初始资金
  python start_trading.py --symbols 600519.SH 000001.SZ  # 自定义股票
        """
    )

    # 模式选择
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--web',
        action='store_true',
        help='启动Web监控界面'
    )
    mode_group.add_argument(
        '--once',
        action='store_true',
        help='只运行一次后退出'
    )

    # 交易参数
    parser.add_argument(
        '--capital',
        type=float,
        default=1000000,
        help='初始资金（默认: 1000000）'
    )
    parser.add_argument(
        '--symbols',
        type=str,
        nargs='+',
        help='监控股票代码列表（默认: 热门股票）'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='自动刷新间隔/秒（默认: 60）'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='trading_data',
        help='数据保存目录（默认: trading_data）'
    )

    args = parser.parse_args()

    # Web模式
    if args.web:
        run_web_mode()
    else:
        run_cli_mode(args)


if __name__ == "__main__":
    main()
