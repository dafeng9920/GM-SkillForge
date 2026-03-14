#!/usr/bin/env python3
"""
AKShare 函数查找工具

列出 AKShare 库中与股票交易相关的函数，按类别分组显示。

用法:
    python check_akshare_funcs.py                    # 默认文本格式输出
    python check_akshare_funcs.py -f json           # JSON 格式输出
    python check_akshare_funcs.py -c fund           # 只显示机构持仓相关
    python check_akshare_funcs.py --help            # 显示帮助信息

参数:
    -f, --format: 输出格式，支持 table（默认）或 json
    -c, --category: 过滤特定类别 (fund|dragon|north|block|all)
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Literal

import akshare as ak


# Category definitions with keywords
CATEGORIES = {
    "fund": {
        "name": "机构持仓相关",
        "keywords": ["fund", "hold", "institution"]
    },
    "dragon": {
        "name": "龙虎榜相关",
        "keywords": ["dragon", "tiger", "la"]
    },
    "north": {
        "name": "北向资金相关",
        "keywords": ["hk", "north", "bound"]
    },
    "block": {
        "name": "大宗交易相关",
        "keywords": ["block"]
    }
}


def get_functions() -> list[str]:
    """Get all public functions from akshare module."""
    return [x for x in dir(ak) if not x.startswith('_')]


def filter_by_category(funcs: list[str], category: str) -> list[str]:
    """Filter functions by category keywords."""
    if category == "all":
        return funcs

    if category not in CATEGORIES:
        return []

    keywords = CATEGORIES[category]["keywords"]
    return [f for f in funcs if any(kw in f.lower() for kw in keywords)]


def group_by_category(funcs: list[str]) -> dict[str, list[str]]:
    """Group functions by category."""
    result = {}
    for key, config in CATEGORIES.items():
        keywords = config["keywords"]
        matched = [f for f in funcs if any(kw in f.lower() for kw in keywords)]
        if matched:
            result[config["name"]] = matched
    return result


def format_table(grouped: dict[str, list[str]]) -> str:
    """Format output as text table."""
    lines = []
    for category_name, funcs in grouped.items():
        lines.append(f"\n=== {category_name} ===")
        for func in funcs:
            lines.append(f"  {func}")
    return "\n".join(lines)


def format_json(grouped: dict[str, list[str]]) -> str:
    """Format output as JSON."""
    return json.dumps(grouped, ensure_ascii=False, indent=2)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AKShare 函数查找工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "-f", "--format",
        choices=["table", "json"],
        default="table",
        help="输出格式：table（默认）或 json"
    )
    parser.add_argument(
        "-c", "--category",
        choices=["fund", "dragon", "north", "block", "all"],
        default="all",
        help="过滤特定类别"
    )

    args = parser.parse_args()

    # Get all functions
    all_funcs = get_functions()

    # Filter or group based on category
    if args.category == "all":
        filtered_funcs = all_funcs
        grouped = group_by_category(all_funcs)
    else:
        filtered_funcs = filter_by_category(all_funcs, args.category)
        category_name = CATEGORIES[args.category]["name"]
        grouped = {category_name: filtered_funcs}

    # Format and output
    if args.format == "json":
        output = format_json(grouped)
    else:
        output = format_table(grouped)

    print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
