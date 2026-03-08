import os
from program.function.core import run_grid_flow


# -------------------------- 遍历配置（全因子参数寻优） --------------------------
CONFIG = {
    "data_folder": r"C:\data-center-pro\stock-etf-trading-data\主题ETF",
    "file_suffix": ".csv",
    "required_cols": [
        "交易日期", "基金代码", "开盘价", "收盘价", "最高价", "最低价", "后复权因子"
    ],
    "start_time": "20100101",
    "min_valid_tickers_per_day": 2,

    "transaction_cost": {
        "buy_rate": 0.86 / 10000,
        "sell_rate": 0.86 / 10000,
        "stamp_duty": 0
    },

    "factor_config": {
        "all_factors": ['momentum', 'volatility'],
        # "all_factors": ['momentum', 'volatility', 'ma_strength', 'volume_surge', 'max_drawdown_neg', 'reversal'],
        "factor_params_space": {
            "momentum": {"window": [5,20]},
            "volatility": {"window": [3,20]},
            # "ma_strength": {"short_window": [5, 10, 15], "long_window": [20, 30, 40]},
            # "volume_surge": {"window": [5, 10, 20], "history_window": [15, 30, 45]},
            # "max_drawdown_neg": {"window": [5, 10, 30]},
            # "reversal": {"window": [3, 5, 10]}
        },
        "factor_comb_min": 2,
        "factor_comb_max": 3,
        "weight_step": 0.4,
        "empty_threshold": 0
    },

    "optimization_metric": "sharpe_ratio",
    "output_dir": os.path.join("data", "遍历结果"),
    "output_file": "ETF轮动策略_全因子参数寻优结果.csv"
}

if __name__ == "__main__":
    run_grid_flow(CONFIG)