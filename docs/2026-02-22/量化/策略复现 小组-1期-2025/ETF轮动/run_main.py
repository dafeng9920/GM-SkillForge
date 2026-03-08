import os
from program.function.core import run_main_flow


# -------------------------- 回测配置（主程序） --------------------------
CONFIG = {
    "data_folder": r"C:\data-center-pro\stock-etf-trading-data\主题ETF",
    "file_suffix": ".csv",
    "required_cols": [
        "交易日期", "基金代码", "开盘价", "收盘价", "最高价", "最低价", "后复权因子"
    ],
    "start_time": "20240101",
    "min_valid_tickers_per_day": 2,

    "transaction_cost": {
        "buy_rate": 0.86 / 10000,
        "sell_rate": 0.86 / 10000,
        "stamp_duty": 0
    },

    "factor_config": {
        # 指定因子与参数
        "target_factors": ['momentum', 'reversal'],
        "factor_params_space": {
            "momentum": {"window": [5]},
            "reversal": {"window": [3]}
        },
        # 指定权重组合（和因子数量一致，且求和为1）
        "factor_weights_list": [
            (0.4, 0.6)
        ],
        "empty_threshold": 0
    },

    # 输出目录
    "output_dir": os.path.join("data", "回测结果"),
    "output_file": "ETF轮动策略_指定因子权重寻优结果.csv",
    "equity_curve_file": "ETF轮动策略_最优资金曲线.png"
}

if __name__ == "__main__":
    run_main_flow(CONFIG)