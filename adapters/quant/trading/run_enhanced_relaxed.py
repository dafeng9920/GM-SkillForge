"""
宽松版配置 - 更容易产生信号
"""

from adapters.quant.trading.quant_trading_system_enhanced import main
from adapters.quant.strategies.enhanced_multi_factor_strategy import EnhancedStrategyConfig

# 创建宽松配置
config = EnhancedStrategyConfig(
    # 技术面权重
    momentum_weight=0.35,
    volatility_weight=0.15,
    volume_weight=0.15,
    rsi_weight=0.10,

    # 机构面权重
    institution_holding_weight=0.10,
    dragon_tiger_weight=0.05,
    north_bound_weight=0.05,
    block_trade_weight=0.05,

    # 降低阈值
    min_composite_score=0.15,     # 从0.25降到0.15
    min_institution_score=0.1,    # 从0.3降到0.1
    institution_bonus=0.15,        # 从0.2降到0.15

    min_confidence=0.50,            # 从0.55降到0.50

    # 仓位
    max_position_size=0.25,
    base_position_size=0.10,
    stop_loss_pct=0.08,
    take_profit_pct=0.20
)

print("=" * 70)
print("  使用宽松配置运行增强版系统")
print("=" * 70)
print("\n配置调整:")
print(f"  综合得分阈值: 0.25 → 0.15")
print(f"  机构得分阈值: 0.3 → 0.1")
print(f"  置信度阈值: 0.55 → 0.50")
print("\n开始运行...\n")

# 导入系统类
import sys
from pathlib import Path

# 手动运行
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--capital', type=float, default=1000000)
    parser.add_argument('--symbols', type=str, nargs='+')
    parser.add_argument('--data-dir', type=str, default='trading_data')

    args = parser.parse_args()

    from adapters.quant.trading.quant_trading_system_enhanced import EnhancedQuantTradingSystem

    system = EnhancedQuantTradingSystem(
        initial_capital=args.capital,
        symbols=args.symbols,
        data_dir=args.data_dir,
        config=config
    )

    system.load_historical_data(days=120)
    system.run_once()
