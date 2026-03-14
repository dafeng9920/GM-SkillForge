"""
Phase 4 回测脚本

运行 Phase 4 盘中同步系统的回测
"""

import logging
from datetime import datetime, timedelta

from .engine import BacktestEngine
from .data import get_test_data, HistoricalDataAdapter
from ..phase4.engine import Phase4Engine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_phase4_backtest(
    symbol: str = "AAPL",
    days: int = 30,
    initial_capital: float = 100000,
    config: dict = None,
) -> None:
    """
    运行 Phase 4 回测

    Args:
        symbol: 股票代码
        days: 回测天数
        initial_capital: 初始资金
        config: Phase 4 配置参数
    """
    logger.info("=" * 60)
    logger.info("Phase 4 盘中同步系统 - 回测")
    logger.info("=" * 60)

    # 1. 初始化 Phase 4 引擎
    phase4_config = config or {
        'min_breakout_amp': 0.02,      # 最小突破幅度 2%
        'min_volume_ratio': 1.5,       # 最小放量倍数 1.5x
        'min_resonance': 2,            # 最小共振信号数（降低以便更容易触发）
        'validation_target_gain': 0.01, # 验证点目标涨幅 1%
        'validation_time_window': 30,   # 验证点时间窗口 30分钟
    }

    phase4 = Phase4Engine(config=phase4_config)
    logger.info(f"Phase 4 配置: {phase4_config}")

    # 2. 获取历史数据
    logger.info(f"获取 {symbol} 历史数据（最近 {days} 天）...")
    data = get_test_data(symbol=symbol, days=days)

    if not data:
        logger.error("未获取到数据，回测终止")
        return

    logger.info(f"获取到 {len(data)} 条Tick数据")

    # 3. 初始化回测引擎
    engine = BacktestEngine(
        initial_capital=initial_capital,
        commission=0.001,  # 0.1% 手续费
        signal_handler=phase4.on_tick,
    )

    # 4. 运行回测
    logger.info("开始回测...")
    metrics = engine.run(data)

    # 5. 打印报告
    metrics.print_report()

    # 6. 打印交易明细
    if metrics.trades:
        logger.info("\n【交易明细】")
        for i, trade in enumerate(metrics.trades[:10], 1):  # 只显示前10笔
            logger.info(
                f"  {i}. {trade.symbol} | "
                f"{trade.entry_time.strftime('%Y-%m-%d %H:%M')} → "
                f"{trade.exit_time.strftime('%Y-%m-%d %H:%M')} | "
                f"入场 ${trade.entry_price:.2f} | "
                f"出场 ${trade.exit_price:.2f} | "
                f"盈亏 ${trade.pnl:.2f}"
            )

        if len(metrics.trades) > 10:
            logger.info(f"  ... 还有 {len(metrics.trades) - 10} 笔交易")

    # 7. 验证点统计
    if phase4.validation_manager.validation_points:
        logger.info("\n【验证点统计】")
        passed = sum(1 for vp in phase4.validation_manager.validation_points.values() if vp.status == 'passed')
        failed = sum(1 for vp in phase4.validation_manager.validation_points.values() if vp.status == 'failed')
        pending = sum(1 for vp in phase4.validation_manager.validation_points.values() if vp.status == 'pending')

        logger.info(f"  通过: {passed}")
        logger.info(f"  失败: {failed}")
        logger.info(f"  进行中: {pending}")
        logger.info(f"  通过率: {passed / (passed + failed) * 100:.1f}% (不含进行中)")

    return metrics


def run_parameter_sweep():
    """
    参数优化测试

    测试不同的验证点参数组合
    """
    logger.info("=" * 60)
    logger.info("参数优化测试")
    logger.info("=" * 60)

    symbol = "AAPL"
    days = 30

    # 测试不同的验证点参数
    test_configs = [
        {'name': '基础', 'target_gain': 0.01, 'time_window': 30},
        {'name': '严格', 'target_gain': 0.02, 'time_window': 15},
        {'name': '宽松', 'target_gain': 0.005, 'time_window': 60},
    ]

    results = []

    for config in test_configs:
        logger.info(f"\n测试配置: {config['name']}")
        logger.info(f"  目标涨幅: {config['target_gain']:.1%}")
        logger.info(f"  时间窗口: {config['time_window']} 分钟")

        phase4_config = {
            'min_breakout_amp': 0.02,
            'min_volume_ratio': 1.5,
            'min_resonance': 2,
            'validation_target_gain': config['target_gain'],
            'validation_time_window': config['time_window'],
        }

        metrics = run_phase4_backtest(
            symbol=symbol,
            days=days,
            config=phase4_config,
        )

        results.append({
            'config': config['name'],
            'total_return': metrics.total_return,
            'sharpe_ratio': metrics.sharpe_ratio,
            'max_drawdown': metrics.max_drawdown,
            'win_rate': metrics.win_rate,
            'total_trades': metrics.total_trades,
        })

    # 打印对比结果
    logger.info("\n" + "=" * 60)
    logger.info("参数对比结果")
    logger.info("=" * 60)

    logger.info(f"{'配置':<10} {'总收益':<12} {'夏普':<10} {'最大回撤':<12} {'胜率':<10} {'交易数':<10}")
    logger.info("-" * 70)

    for r in results:
        logger.info(
            f"{r['config']:<10} "
            f"{r['total_return']:>10.2%}  "
            f"{r['sharpe_ratio']:>8.2f}  "
            f"{r['max_drawdown']:>10.2%}  "
            f"{r['win_rate']:>8.2%}  "
            f"{r['total_trades']:>8}"
        )


if __name__ == "__main__":
    # 运行单个回测
    run_phase4_backtest(
        symbol="AAPL",
        days=30,
        initial_capital=100000,
    )

    # 运行参数优化
    # run_parameter_sweep()
