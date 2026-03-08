import os
from glob import glob
from itertools import combinations
import numpy as np
import pandas as pd
import warnings; warnings.filterwarnings("ignore")
import importlib
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.font_manager as fm


# -------------------------- 字体初始化（Windows优先） --------------------------
def init_chinese_font():
    mpl.rcParams.update(mpl.rcParamsDefault)
    plt.rcParams['axes.unicode_minus'] = False

    installed_fonts = set([f.name for f in fm.fontManager.ttflist])
    font_candidates = [
        "Microsoft YaHei", "SimHei", "SimSun", "Microsoft JhengHei",
        "WenQuanYi Micro Hei", "WenQuanYi Zen Hei", "Noto Sans CJK SC",
        "PingFang SC", "Heiti TC", "Arial Unicode MS", "DejaVu Sans"
    ]
    available_fonts = [font for font in font_candidates if font in installed_fonts]
    if not available_fonts:
        plt.rcParams['font.family'] = 'DejaVu Sans'
        return
    target_font = available_fonts[0]
    try:
        plt.rcParams['font.family'] = target_font
        fig, ax = plt.subplots(figsize=(1, 1))
        ax.text(0.5, 0.5, "中文测试：ETF轮动策略", ha='center', va='center')
        plt.close(fig)
    except Exception:
        plt.rcParams['font.family'] = 'DejaVu Sans'


# -------------------------- 工具函数 --------------------------
def get_ticker_name(fund_code: str) -> str:
    return str(fund_code).strip().replace(" ", "").replace("\t", "")


def get_all_etf_files(folder_path: str, file_suffix: str) -> list:
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹不存在：{folder_path}")
    file_pattern = os.path.join(folder_path, f"*{file_suffix}")
    etf_files = glob(file_pattern)
    if len(etf_files) == 0:
        raise ValueError(f"文件夹 {folder_path} 中无{file_suffix}文件")
    print(f"成功扫描到 {len(etf_files)} 个ETF文件：")
    for file in etf_files[:20]:
        print(f"  - {os.path.basename(file)}")
    if len(etf_files) > 20:
        print("  ... （仅展示前20个）")
    return etf_files


def adjust_price_by_factor(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["adj_open"] = df["开盘价"] * df["后复权因子"]
    df["adj_close"] = df["收盘价"] * df["后复权因子"]
    df["adj_high"] = df["最高价"] * df["后复权因子"]
    df["adj_low"] = df["最低价"] * df["后复权因子"]
    return df


def is_ticker_valid_on_day(row, ticker: str) -> bool:
    adj_close = row.get(f"{ticker}_adj_close")
    adj_factor = row.get(f"{ticker}_后复权因子")
    return pd.notna(adj_close) and pd.notna(adj_factor) and adj_close > 0 and adj_factor > 0


# -------------------------- 数据加载与合并 --------------------------
def load_adjust_and_merge_data(etf_files: list, required_cols: list, start_time: str, min_valid_tickers_per_day: int) -> tuple:
    if not etf_files:
        raise ValueError("无有效ETF文件可加载")

    merged_df = None
    valid_tickers = []
    loaded_files = set()

    for file in etf_files:
        file_basename = os.path.basename(file)
        if file_basename in loaded_files:
            print(f"警告：文件 {file_basename} 已加载，跳过重复文件")
            continue

        try:
            df_raw = pd.read_csv(
                file, skiprows=1, encoding="gbk",
                parse_dates=["交易日期"], usecols=required_cols, dtype={"基金代码": str}
            )

            missing_cols = [col for col in required_cols if col not in df_raw.columns]
            if missing_cols:
                print(f"警告：文件 {file_basename} 缺失列 {missing_cols}，跳过")
                continue

            df_adj = adjust_price_by_factor(df_raw)
            df_adj["adj_amp"] = df_adj["adj_close"].pct_change(fill_method=None)
            df_adj = df_adj[df_adj["交易日期"] >= pd.to_datetime(start_time)]
            if len(df_adj) < 10:
                print(f"警告：文件 {file_basename} 有效数据不足10条，跳过")
                continue

            fund_codes = df_adj["基金代码"].dropna().unique()
            if len(fund_codes) == 0:
                print(f"警告：文件 {file_basename} 基金代码为空，跳过")
                continue
            ticker = get_ticker_name(fund_codes[0])
            if ticker in valid_tickers:
                print(f"警告：标的 {ticker} 已存在，跳过重复文件")
                continue

            # 列名添加标的前缀（含扩展列如PE、PB、成交量）
            col_rename = {"交易日期": "交易日期", "后复权因子": f"{ticker}_后复权因子"}
            for col in ["adj_open", "adj_close", "adj_amp"]:
                col_rename[col] = f"{ticker}_{col}"
            for col in ["PE", "PB", "成交量"]:
                if col in df_adj.columns:
                    col_rename[col] = f"{ticker}_{col}"

            df_adj_renamed = df_adj.rename(columns=col_rename)[list(col_rename.values())]
            df_adj_renamed["交易日期"] = pd.to_datetime(df_adj_renamed["交易日期"])

            if merged_df is None:
                merged_df = df_adj_renamed
            else:
                merged_df = pd.merge(merged_df, df_adj_renamed, how="outer", on="交易日期")

            valid_tickers.append(ticker)
            loaded_files.add(file_basename)
            print(f"成功加载标的：{ticker}（文件：{file_basename}）")

        except Exception as e:
            print(f"警告：加载文件 {file_basename} 失败，错误：{str(e)}，跳过")
            continue

    if merged_df is None or len(valid_tickers) < min_valid_tickers_per_day:
        raise ValueError(f"有效标的不足{min_valid_tickers_per_day}个，无法轮动")
    merged_df = merged_df.sort_values("交易日期").reset_index(drop=True)

    valid_ticker_count = []
    for _, row in merged_df.iterrows():
        count = sum([1 for ticker in valid_tickers if is_ticker_valid_on_day(row, ticker)])
        valid_ticker_count.append(count)
    merged_df["valid_ticker_count"] = valid_ticker_count
    merged_df = merged_df[merged_df["valid_ticker_count"] >= min_valid_tickers_per_day].reset_index(drop=True)
    if len(merged_df) == 0:
        raise ValueError("所有交易日有效标的数不足，无法继续")

    print(f"\n数据加载完成：有效标的数 {len(valid_tickers)}，有效交易日数 {len(merged_df)}")
    return merged_df, valid_tickers


# -------------------------- 多因子加权信号 --------------------------
def generate_weighted_signals(df: pd.DataFrame, valid_tickers: list, factor_cols: list, target_factors: list,
                              weights: tuple, empty_threshold: float, min_valid_tickers_per_day: int) -> pd.DataFrame:
    df = df.copy()
    factor_num = len(target_factors)
    ticker_num = len(valid_tickers)

    if len(weights) != factor_num:
        print(f"警告：权重长度（{len(weights)}）与因子数量（{factor_num}）不匹配，跳过该权重组合")
        return df
    if not np.isclose(sum(weights), 1.0, rtol=1e-3):
        print(f"警告：权重总和（{sum(weights)}）不等于1，跳过该权重组合")
        return df
    if len(factor_cols) != ticker_num * factor_num:
        print(f"警告：因子列数（{len(factor_cols)}）与预期（{ticker_num}×{factor_num}）不匹配，跳过")
        return df

    for ticker in valid_tickers:
        ticker_factors = [f"{ticker}_{factor}" for factor in target_factors]
        if not all(col in df.columns for col in ticker_factors):
            print(f"警告：标的 {ticker} 缺少部分因子列，跳过")
            df[f"{ticker}_score"] = -np.inf
            continue
        df[f"{ticker}_score"] = sum([df[col] * w for col, w in zip(ticker_factors, weights)])

    score_cols = [f"{ticker}_score" for ticker in valid_tickers if f"{ticker}_score" in df.columns]

    if len(score_cols) < min_valid_tickers_per_day:
        df["target_ticker"] = "empty"
    else:
        df["max_score"] = df[score_cols].replace(-np.inf, np.nan).max(axis=1)
        df["target_ticker"] = df[score_cols].replace(-np.inf, np.nan).idxmax(axis=1, skipna=True).str.replace("_score", "")
        df.loc[df["max_score"] < empty_threshold, "target_ticker"] = "empty"
        df["target_ticker"] = df["target_ticker"].fillna("empty")

    df["pos"] = df["target_ticker"].shift(1).fillna("empty")
    df["is_rebalance"] = (df["pos"] != df["pos"].shift(1)).astype(int)

    return df


# -------------------------- 策略收益与绩效 --------------------------
def calculate_strategy_returns(df: pd.DataFrame, valid_tickers: list, buy_rate: float, sell_rate: float) -> pd.DataFrame:
    df = df.copy()
    df["base_return"] = 0.0
    for ticker in valid_tickers:
        col = f"{ticker}_adj_amp"
        if col in df.columns:
            df.loc[df["pos"] == ticker, "base_return"] = df[col]

    prev_pos = df["pos"].shift(1).fillna("empty")
    df["is_rebalance"] = (df["pos"] != prev_pos).astype(int)

    # 初始化策略收益为基础收益（非调仓日保持为收盘-收盘收益）
    df["strategy_return"] = df["base_return"]

    # 构造三类调仓掩码，避免卖出或买入成本被覆盖
    exit_to_empty = (df["is_rebalance"] == 1) & (prev_pos != "empty") & (df["pos"] == "empty")
    enter_from_empty = (df["is_rebalance"] == 1) & (prev_pos == "empty") & (df["pos"] != "empty")
    switch_asset = (df["is_rebalance"] == 1) & (prev_pos != "empty") & (df["pos"] != "empty")

    # 仅卖出转空：当日只计卖出成本
    df.loc[exit_to_empty, "strategy_return"] = -sell_rate

    # 买入或换标的：按开盘买入到收盘的收益，分别计入买入与卖出成本
    for ticker in valid_tickers:
        open_col = f"{ticker}_adj_open"
        close_col = f"{ticker}_adj_close"
        if open_col in df.columns and close_col in df.columns:
            mask_enter = enter_from_empty & (df["pos"] == ticker)
            mask_switch = switch_asset & (df["pos"] == ticker)
            # 从空仓进入持仓：仅计买入成本
            df.loc[mask_enter, "strategy_return"] = (df[close_col] / (df[open_col] * (1 + buy_rate))) - 1
            # 从A换到B：同时计卖出与买入成本
            df.loc[mask_switch, "strategy_return"] = ((df[close_col] / (df[open_col] * (1 + buy_rate))) * (1 - sell_rate)) - 1

    # 累计净值
    df["strategy_net"] = (1 + df["strategy_return"]).cumprod()

    # 计算各标的净值（用于绘图对比）
    for ticker in valid_tickers:
        close_col = f"{ticker}_adj_close"
        if close_col in df.columns:
            initial_close = df[close_col].dropna().iloc[0]
            df[f"{ticker}_net"] = df[close_col] / initial_close
    return df


def evaluate_performance(df: pd.DataFrame) -> dict:
    if "strategy_net" not in df.columns:
        return {"error": "无策略净值数据"}
    valid_net = df["strategy_net"].dropna()
    if len(valid_net) < 2:
        return {"error": "有效数据不足"}

    total_return = valid_net.iloc[-1] - 1
    years = (df["交易日期"].iloc[-1] - df["交易日期"].iloc[0]).days / 365.25
    daily_ret = valid_net.pct_change(fill_method=None).dropna()

    annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
    annual_vol = daily_ret.std() * np.sqrt(252) if len(daily_ret) > 0 else 0
    sharpe_ratio = (annual_return - 0.02) / annual_vol if annual_vol != 0 else np.nan
    max_drawdown = (valid_net / valid_net.cummax() - 1).min()
    win_rate = (daily_ret > 0).sum() / len(daily_ret) if len(daily_ret) > 0 else 0

    return {
        "累计收益率": f"{total_return:.2%}",
        "年化收益率": f"{annual_return:.2%}",
        "年化波动率": f"{annual_vol:.2%}",
        "夏普比率": f"{sharpe_ratio:.2f}" if not np.isnan(sharpe_ratio) else "无",
        "最大回撤": f"{max_drawdown:.2%}",
        "胜率": f"{win_rate:.2%}",
        "年化收益率_num": annual_return,
        "夏普比率_num": sharpe_ratio,
        "最大回撤_num": max_drawdown
    }


def load_factor_func(name: str):
    module = importlib.import_module(f"program.factor.{name}")
    if not hasattr(module, "factor"):
        raise AttributeError(f"因子模块 '{name}' 未定义 factor(df, ticker, params)")
    return getattr(module, "factor")


def calculate_factors(df: pd.DataFrame, valid_tickers: list, target_factors: list, factor_params: dict) -> tuple:
    df = df.copy()
    factor_cols = []

    for factor_name in target_factors:
        try:
            factor_func = load_factor_func(factor_name)
        except ModuleNotFoundError as e:
            raise ValueError(f"未找到因子模块：{factor_name}") from e
        except AttributeError as e:
            raise ValueError(f"因子模块 '{factor_name}' 未提供 factor(df, ticker, params) 函数") from e

        params = factor_params.get(factor_name, {})
        for ticker in valid_tickers:
            col = f"{ticker}_{factor_name}"
            df[col] = factor_func(df, ticker, params)
            factor_cols.append(col)

    if factor_cols:
        df[factor_cols] = df[factor_cols].fillna(-np.inf)
    return df, factor_cols


# -------------------------- 组合与权重生成 --------------------------
def generate_factor_combinations(all_factors: list, min_comb: int, max_comb: int) -> list:
    factor_combs = []
    for k in range(min_comb, max_comb + 1):
        comb_k = list(combinations(all_factors, k))
        factor_combs.extend(comb_k)
    return factor_combs


def generate_weight_combinations(factor_num: int, step: float = 0.2) -> list:
    weights = []

    def _recurse(current, remaining, start):
        if len(current) == factor_num - 1:
            current.append(round(remaining, 1))
            if all(w >= 0 for w in current):
                weights.append(tuple(current))
            current.pop()
            return
        for w in np.arange(start, remaining + step, step):
            w_rounded = round(w, 1)
            current.append(w_rounded)
            _recurse(current, remaining - w_rounded, w_rounded)
            current.pop()

    _recurse([], 1.0, step)
    return weights


# -------------------------- 绘图保存 --------------------------
def plot_and_save_equity_curve(df: pd.DataFrame, valid_tickers: list, title: str, output_png: str):
    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df["交易日期"], df["strategy_net"], label="策略净值", linewidth=1.5)
    for ticker in valid_tickers:
        net_col = f"{ticker}_net"
        if net_col in df.columns:
            ax.plot(df["交易日期"], df[net_col], label=f"{ticker}净值", linewidth=1, alpha=0.7)
    ax.set_title(title)
    ax.set_xlabel("交易日期")
    ax.set_ylabel("净值")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_png)
    plt.close(fig)


# -------------------------- 主程序与遍历流程（迁移自脚本） --------------------------
def _ensure_output_paths(config: dict, need_equity_curve: bool = False):
    os.makedirs(config["output_dir"], exist_ok=True)
    config["output_file_path"] = os.path.join(config["output_dir"], config["output_file"])
    if need_equity_curve:
        config["equity_curve_path"] = os.path.join(config["output_dir"], config["equity_curve_file"])


def optimize_main(merged_df: pd.DataFrame, valid_tickers: list, config: dict):
    factor_cfg = config["factor_config"]
    target_factors = factor_cfg["target_factors"]
    factor_weights_list = factor_cfg["factor_weights_list"]
    factor_params_space = factor_cfg["factor_params_space"]

    # 生成因子参数组合（笛卡尔积）
    from itertools import product
    param_spaces = []
    param_names = []
    for factor in target_factors:
        factor_params = factor_params_space[factor]
        param_spaces.append(list(product(*factor_params.values())))
        param_names.extend([f"{factor}_{k}" for k in factor_params.keys()])

    flat_param_combs = []
    for combo in product(*param_spaces):
        flat = []
        for p in combo:
            flat.extend(p if isinstance(p, tuple) else [p])
        flat_param_combs.append(flat)

    total_comb_count = len(flat_param_combs) * len(factor_weights_list)
    print(f"\n参数寻优总览：参数组合{len(flat_param_combs)}×权重组合{len(factor_weights_list)}=总{total_comb_count}")

    results = []
    completed_count = 0

    for param_idx, flat_params in enumerate(flat_param_combs):
        current_factor_params = {}
        ptr = 0
        for factor in target_factors:
            keys = list(factor_params_space[factor].keys())
            current_factor_params[factor] = {}
            for key in keys:
                current_factor_params[factor][key] = flat_params[ptr]
                ptr += 1

        for weights in factor_weights_list:
            try:
                df_temp = merged_df.copy()
                # 计算因子
                df_temp, factor_cols = calculate_factors(
                    df=df_temp,
                    valid_tickers=valid_tickers,
                    target_factors=target_factors,
                    factor_params=current_factor_params
                )
                if len(factor_cols) == 0:
                    print(f"警告：参数组合{param_idx + 1}无有效因子列，跳过")
                    continue

                # 生成信号→计算收益→评估绩效
                df_temp = generate_weighted_signals(
                    df=df_temp,
                    valid_tickers=valid_tickers,
                    factor_cols=factor_cols,
                    target_factors=target_factors,
                    weights=weights,
                    empty_threshold=factor_cfg["empty_threshold"],
                    min_valid_tickers_per_day=config["min_valid_tickers_per_day"]
                )
                df_temp = calculate_strategy_returns(
                    df_temp, valid_tickers,
                    config["transaction_cost"]["buy_rate"],
                    config["transaction_cost"]["sell_rate"]
                )
                perf = evaluate_performance(df_temp)
                if "error" in perf:
                    continue

                result_row = {
                    "使用因子": str(target_factors),
                    **{param_names[i]: flat_params[i] for i in range(len(param_names))},
                    "因子权重": weights,
                    **{k: v for k, v in perf.items() if not k.endswith("_num")}
                }
                results.append((result_row, df_temp))
                completed_count += 1
                print(f"完成组合 {completed_count}/{total_comb_count}：{result_row}")

            except Exception as e:
                print(f"组合测试失败（参数：{flat_params}，权重：{weights}）：{str(e)}，跳过")
                completed_count += 1
                continue

    if not results:
        raise ValueError("所有参数组合测试失败（请检查数据质量或参数范围）")

    # 排序：按夏普比率、年化收益率、最大回撤
    def sort_key(item):
        row, _ = item
        return (
            float(row.get("夏普比率", 0) if row.get("夏普比率") != "无" else 0),
            float(row.get("年化收益率", "0%" ).strip('%')),
            -float(row.get("最大回撤", "0%" ).strip('%'))
        )

    results_sorted = sorted(results, key=sort_key, reverse=True)
    best_row, best_df = results_sorted[0]

    # 保存结果CSV与资金曲线图
    os.makedirs(config["output_dir"], exist_ok=True)
    pd.DataFrame([best_row]).to_csv(config["output_file_path"], index=False, encoding="utf-8-sig")
    print(f"最优结果已保存：{config['output_file_path']}")

    title = f"ETF轮动策略（最优组合）"
    plot_and_save_equity_curve(best_df, valid_tickers, title, config["equity_curve_path"])
    print(f"资金曲线已保存：{config['equity_curve_path']}")

    return best_row, best_df


def run_main_flow(config: dict):
    init_chinese_font()
    _ensure_output_paths(config, need_equity_curve=True)

    # 加载数据
    etf_files = get_all_etf_files(config["data_folder"], config["file_suffix"])
    merged_df, valid_tickers = load_adjust_and_merge_data(
        etf_files,
        config["required_cols"],
        config["start_time"],
        config["min_valid_tickers_per_day"]
    )

    print(f"\n已指定使用因子：{config['factor_config']['target_factors']}")
    print(f"手动设置权重组合：{config['factor_config']['factor_weights_list']}")

    best_row, _ = optimize_main(merged_df, valid_tickers, config)
    print("\n最优回测结果：")
    for k, v in best_row.items():
        print(f"  {k}: {v}")
    return best_row


def optimize_grid(merged_df: pd.DataFrame, valid_tickers: list, config: dict) -> pd.DataFrame:
    factor_cfg = config["factor_config"]
    factor_combs = generate_factor_combinations(
        factor_cfg["all_factors"],
        factor_cfg["factor_comb_min"],
        factor_cfg["factor_comb_max"]
    )

    print(f"\n生成因子组合完成：共 {len(factor_combs)} 个组合")

    from itertools import product
    # 预估总组合数
    total_comb_count = 0
    comb_info = []
    for factor_comb in factor_combs:
        param_spaces = []
        for factor in factor_comb:
            params_space = factor_cfg["factor_params_space"][factor]
            param_spaces.append(list(product(*params_space.values())))
        param_comb_num = 1
        for space in param_spaces:
            param_comb_num *= len(space)
        weight_comb_num = len(generate_weight_combinations(len(factor_comb), step=factor_cfg["weight_step"]))
        comb_total = param_comb_num * weight_comb_num
        total_comb_count += comb_total
        comb_info.append({
            "factor_comb": factor_comb,
            "param_comb_num": param_comb_num,
            "weight_comb_num": weight_comb_num,
            "total": comb_total
        })

    print(f"\n参数寻优总览：总组合数约 {total_comb_count}")
    for info in comb_info[:5]:
        print(f"  {info['factor_comb']}：参数{info['param_comb_num']}×权重{info['weight_comb_num']}={info['total']}")
    if len(comb_info) > 5:
        print("  ... （省略后续）")

    # 遍历所有组合
    results = []
    completed_count = 0

    for factor_comb in factor_combs:
        factor_num = len(factor_comb)

        # 生成该组合的参数组合（扁平化）
        param_spaces = []
        param_names = []
        for factor in factor_comb:
            params_space = factor_cfg["factor_params_space"][factor]
            param_spaces.append(list(product(*params_space.values())))
            param_names.extend([f"{factor}_{k}" for k in params_space.keys()])

        flat_param_combs = []
        for combo in product(*param_spaces):
            flat = []
            for p in combo:
                flat.extend(p if isinstance(p, tuple) else [p])
            flat_param_combs.append(flat)

        # 权重组合
        weight_combs = generate_weight_combinations(factor_num, step=factor_cfg["weight_step"])
        if len(weight_combs) == 0:
            print(f"警告：因子组合{factor_comb}无有效权重组合，跳过")
            continue

        for flat_params in flat_param_combs:
            # 构造当前因子参数字典
            current_factor_params = {}
            ptr = 0
            for factor in factor_comb:
                keys = list(factor_cfg["factor_params_space"][factor].keys())
                current_factor_params[factor] = {}
                for key in keys:
                    current_factor_params[factor][key] = flat_params[ptr]
                    ptr += 1

            for weights in weight_combs:
                try:
                    df_temp = merged_df.copy()
                    df_temp, factor_cols = calculate_factors(
                        df=df_temp,
                        valid_tickers=valid_tickers,
                        target_factors=factor_comb,
                        factor_params=current_factor_params
                    )
                    if len(factor_cols) == 0:
                        continue

                    df_temp = generate_weighted_signals(
                        df=df_temp,
                        valid_tickers=valid_tickers,
                        factor_cols=factor_cols,
                        target_factors=factor_comb,
                        weights=weights,
                        empty_threshold=factor_cfg["empty_threshold"],
                        min_valid_tickers_per_day=config["min_valid_tickers_per_day"]
                    )
                    df_temp = calculate_strategy_returns(
                        df_temp, valid_tickers,
                        config["transaction_cost"]["buy_rate"],
                        config["transaction_cost"]["sell_rate"]
                    )
                    perf = evaluate_performance(df_temp)
                    if "error" in perf:
                        continue

                    result_row = {
                        "使用因子": str(factor_comb),
                        **{param_names[i]: flat_params[i] for i in range(len(param_names))},
                        "因子权重": weights,
                        **{k: v for k, v in perf.items() if not k.endswith("_num")}
                    }
                    results.append(result_row)
                    completed_count += 1
                    if completed_count % 100 == 0:
                        print(f"已完成 {completed_count} 个组合")

                except Exception:
                    completed_count += 1
                    continue

    if not results:
        raise ValueError("所有参数组合测试失败（请检查数据质量或参数范围）")

    results_df = pd.DataFrame(results)
    results_df.to_csv(config["output_file_path"], index=False, encoding="utf-8-sig")
    print(f"遍历结果已保存：{config['output_file_path']}")
    return results_df


def run_grid_flow(config: dict):
    init_chinese_font()
    _ensure_output_paths(config, need_equity_curve=False)

    etf_files = get_all_etf_files(config["data_folder"], config["file_suffix"])
    merged_df, valid_tickers = load_adjust_and_merge_data(
        etf_files,
        config["required_cols"],
        config["start_time"],
        config["min_valid_tickers_per_day"]
    )

    results_df = optimize_grid(merged_df, valid_tickers, config)
    print("\n前5条结果示例：")
    print(results_df.head())
    return results_df