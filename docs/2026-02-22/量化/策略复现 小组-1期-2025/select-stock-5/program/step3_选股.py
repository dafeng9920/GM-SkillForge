"""
邢不行™️选股框架
Python股票量化投资课程

版权所有 ©️ 邢不行
微信: xbx8662

未经授权，不得复制、修改、或使用本代码的全部或部分内容。仅限个人学习用途，禁止商业用途。

Author: 邢不行
"""

import time
import warnings
import pandas as pd

from core.model.backtest_config import load_config, BacktestConfig
from core.utils.path_kit import get_file_path
from core.market_essentials import save_latest_result, select_analysis
from core.figure import draw_equity_curve_plotly

# ====================================================================================================
# ** 配置与初始化 **
# 忽略警告并设定显示选项，以优化代码输出的可读性
# ====================================================================================================
warnings.filterwarnings("ignore")
pd.set_option("expand_frame_repr", False)
pd.set_option("display.unicode.ambiguous_as_wide", True)
pd.set_option("display.unicode.east_asian_width", True)

# 选股结果中需要的列
FACTOR_COLS = ["交易日期", "股票代码", "股票名称"]


def select_stocks(conf: BacktestConfig, show_plot=True):
    """
    选股流程：
    1. 初始化策略配置
    2. 加载并清洗选股数据
    3. 计算选股因子并进行筛选
    4. 缓存选股结果

    参数:
    conf (BacktestConfig): 回测配置
    返回:
    DataFrame: 选股结果
    """
    s_time = time.time()
    print("🌀 开始选股...")

    # ====================================================================================================
    # 1. 初始化策略配置
    # ====================================================================================================
    strategy = conf.strategy
    print(f"[{strategy.name}] 选股策略启动...")

    # ====================================================================================================
    # 2. 加载并清洗选股数据
    # ====================================================================================================
    s = time.time()
    period_df = pd.read_pickle(get_file_path("data", "运行缓存", "因子计算结果.pkl"))  # 加载带有因子计算结果的数据
    factor_columns_dict = pd.read_pickle(get_file_path("data", "运行缓存", "策略因子列信息.pkl"))  # 读取策略因子列信息
    factor_columns_dict = {k: v for k, v in factor_columns_dict.items() if k in conf.strategy.factor_columns}

    # 新增：计算市值分位数
    period_df['市值分位'] = period_df.groupby('交易日期')['总市值'].rank(pct=True)

    # 过滤掉每一个周期中，没有交易的股票
    period_df = period_df[period_df["是否交易"] == 1].dropna(subset=factor_columns_dict.keys()).copy()
    period_df.dropna(subset=["股票代码"], inplace=True)

    # 最后整理一下
    period_df.sort_values(by=["交易日期", "股票代码"], inplace=True)
    period_df.reset_index(drop=True, inplace=True)

    print(f"[{strategy.name}] 选股数据准备完成，耗时：{time.time() - s:.2f}s")

    # ====================================================================================================
    # 3. 因子计算和筛选流程
    # 3.1 前置筛选
    # 3.2 计算选股因子
    # 3.3 基于选股因子进行选股
    # ====================================================================================================

    # 3.1 前置筛选
    s = time.time()
    period_df = strategy.filter_before_select(period_df)
    print(f"[{strategy.name}] 前置筛选耗时：{time.time() - s:.2f}s")

    # 3.2 计算选股因子
    s = time.time()
    result_df = strategy.calc_select_factor(period_df)
    period_df = period_df.join(result_df)
    print(f"[{strategy.name}] 因子计算耗时：{time.time() - s:.2f}s")

    # 3.3 进行选股
    s = time.time()
    # 按照选股日期裁切一下，只保留需要选股的日期
    index_data = conf.read_index_with_trading_date()
    select_dates = index_data[index_data[f"{conf.strategy.hold_period_name}终止日"]]["交易日期"]
    period_df = period_df[period_df["交易日期"].isin(select_dates)]
    # 按照选股因子进行选股
    period_df = select_by_factor(period_df, strategy.select_num, strategy.factor_name)
    print(f"[{strategy.name}] 选股耗时：{time.time() - s:.2f}s")

    select_result_df = period_df[[*FACTOR_COLS, "目标资金占比"]].copy()

    # 若无选股结果则直接返回
    if select_result_df.empty:
        return

    # ====================================================================================================
    # 4. 缓存选股结果
    # ====================================================================================================
    file_path = conf.get_result_folder() / f"{strategy.name}选股结果.pkl"
    select_result_df.to_pickle(file_path)
    select_result_df.to_csv(conf.get_result_folder() / f"{strategy.name}选股结果.csv", encoding="utf-8-sig")

    print(f"[{strategy.name}] 选股结果已保存，耗时: {(time.time() - s):.2f}s")
    print(f"💾 选股结果数据大小：{select_result_df.memory_usage(deep=True).sum() / 1024 / 1024:.4f} MB\n")
    print(f"✅ 选股完成，总耗时：{time.time() - s_time:.3f}秒\n")

    # 保存最新的选股结果
    save_latest_result(conf, select_result_df)

    # ====================================================================================================
    # 5. 分析选股结果
    # ====================================================================================================
    select_analysis(conf, period_df, 10, show_plot=show_plot)

    return select_result_df


def select_by_factor(period_df, select_num: float | int, factor_name):
    """
    基于因子选择目标股票并计算资金权重。

    参数:
    period_df (DataFrame): 筛选后的数据
    select_num (float | int): 选股数量或比例
    factor_name (str): 选股因子名称

    返回:
    DataFrame: 带目标资金占比的选股结果
    """
    period_df = calc_select_factor_rank(period_df, factor_column=factor_name, ascending=True)

    # 基于排名筛选股票
    if int(select_num) == 0:  # 选股数量是百分比
        period_df = period_df[period_df["rank"] <= period_df["总股数"] * select_num].copy()
    else:  # 选股数量是固定的数字
        period_df = period_df[period_df["rank"] <= select_num].copy()

    # 根据选股数量分配目标资金
    period_df["目标资金占比"] = 1 / period_df.groupby("交易日期")["股票代码"].transform("size")

    period_df.sort_values(by="交易日期", inplace=True)
    period_df.reset_index(drop=True, inplace=True)

    # 清理无关列
    period_df.drop(columns=["总股数", "rank_max"], inplace=True)

    return period_df


def calc_select_factor_rank(df, factor_column="因子", ascending=True):
    """
    计算因子排名。

    参数:
    df (DataFrame): 原始数据
    factor_column (str): 因子列名
    ascending (bool): 排序顺序，True为升序

    返回:
    DataFrame: 包含排名的原数据
    """
    # 计算因子的分组排名
    df["rank"] = df.groupby("交易日期")[factor_column].rank(method="min", ascending=ascending)
    df["rank_max"] = df.groupby("交易日期")["rank"].transform("max")
    # 根据时间和因子排名排序
    df.sort_values(by=["交易日期", "rank"], inplace=True)
    # 重新计算一下总股数
    df["总股数"] = df.groupby("交易日期")["股票代码"].transform("size")
    return df


if __name__ == "__main__":
    backtest_config = load_config()
    select_stocks(backtest_config)
