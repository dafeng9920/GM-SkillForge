#!/usr/bin/env python3
"""
查询A股机构持仓数据工具

使用 AKShare 获取指定股票的机构持仓数据，包括基金持仓和北向资金持股。

用法:
    python check_institution.py              # 使用默认参数（比亚迪 002594）
    python check_institution.py 600519       # 查询贵州茅台
    python check_institution.py 000001 -n 5  # 查询平安银行，显示5条记录
    python check_institution.py 002594 -o json  # 输出JSON格式

参数:
    symbol: 股票代码（6位数字），默认为 002594（比亚迪）
    -n, --rows: 显示记录数，默认为 10
    -o, --output: 输出格式，支持 table（默认）或 json
    -v, --verbose: 详细输出模式

依赖:
    pip install akshare pandas
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Literal

import akshare as ak
import pandas as pd


def fetch_fund_holdings(symbol: str) -> pd.DataFrame | None:
    """
    获取基金持仓数据

    Args:
        symbol: 股票代码

    Returns:
        DataFrame with fund holdings data, or None if failed
    """
    try:
        df = ak.stock_institute_fund_em(symbol=symbol)
        return df
    except Exception as e:
        print(f"基金持仓查询失败: {e}", file=sys.stderr)
        return None


def fetch_north_holdings(symbol: str) -> pd.DataFrame | None:
    """
    获取北向资金持股数据

    Args:
        symbol: 股票代码

    Returns:
        DataFrame with north capital holdings data, or None if failed
    """
    try:
        df = ak.stock_hk_hold_sz_em(symbol=symbol)
        return df
    except Exception as e:
        print(f"北向资金查询失败: {e}", file=sys.stderr)
        return None


def format_output(
    fund_df: pd.DataFrame | None,
    north_df: pd.DataFrame | None,
    symbol: str,
    rows: int,
    output_format: Literal["table", "json"]
) -> str:
    """
    格式化输出结果

    Args:
        fund_df: 基金持仓数据
        north_df: 北向资金数据
        symbol: 股票代码
        rows: 显示行数
        output_format: 输出格式

    Returns:
        格式化的输出字符串
    """
    if output_format == "json":
        result = {
            "symbol": symbol,
            "fund_holdings": fund_df.head(rows).to_dict("records") if fund_df is not None else None,
            "north_capital": north_df.tail(rows).to_dict("records") if north_df is not None else None,
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    # Table format
    lines = [f"查询股票({symbol})机构持仓...\n", "=" * 60]

    if fund_df is not None:
        lines.append("\n【基金持仓情况】")
        lines.append(str(fund_df[['基金数量', '基金持仓', '占流通股比']].head(rows)))
    else:
        lines.append("\n【基金持仓情况】查询失败")

    if north_df is not None:
        lines.append("\n【北向资金持股】")
        lines.append(str(north_df.tail(rows)))
    else:
        lines.append("\n【北向资金持股】查询失败")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(
        description="查询A股机构持仓数据工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "symbol",
        nargs="?",
        default="002594",
        help="股票代码（6位数字），默认为002594（比亚迪）"
    )
    parser.add_argument(
        "-n", "--rows",
        type=int,
        default=10,
        help="显示记录数，默认为10"
    )
    parser.add_argument(
        "-o", "--output",
        choices=["table", "json"],
        default="table",
        help="输出格式：table（表格）或 json，默认为table"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="详细输出模式"
    )

    args = parser.parse_args()

    # Validate symbol format
    if not args.symbol.isdigit() or len(args.symbol) != 6:
        print(f"错误: 股票代码必须是6位数字，收到: {args.symbol}", file=sys.stderr)
        return 1

    if args.verbose:
        print(f"[INFO] 查询股票: {args.symbol}", file=sys.stderr)
        print(f"[INFO] 显示行数: {args.rows}", file=sys.stderr)
        print(f"[INFO] 输出格式: {args.output}", file=sys.stderr)

    # Fetch data
    fund_df = fetch_fund_holdings(args.symbol)
    north_df = fetch_north_holdings(args.symbol)

    # Format and output
    output = format_output(fund_df, north_df, args.symbol, args.rows, args.output)
    print(output)

    # Return 0 if at least one data source succeeded
    return 0 if (fund_df is not None or north_df is not None) else 1


if __name__ == "__main__":
    sys.exit(main())
