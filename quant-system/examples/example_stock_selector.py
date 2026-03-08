"""
使用示例: 股票选股 Skill

展示如何使用适配层调用 select-stock-5 选股框架
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.research.stock_selector import StockSelectorSkill, run_stock_selector


def example_basic():
    """基本用法示例"""
    print("=" * 60)
    print("示例 1: 基本选股")
    print("=" * 60)

    # 使用便捷函数
    result = run_stock_selector(
        start_date="2020-01-01",
        end_date="2024-12-31",
        hold_period="5D",          # 5天持仓周期
        select_num=10,             # 选10只股票
        factor_list=[
            ("市值", True, None, 1),        # 市值因子，升序，权重1
            ("换手率", True, 5, 1),         # 5日换手率，升序，权重1
        ],
        filter_list=[
            ("市值", None, "val:<=5000000000"),  # 市值<=50亿
        ]
    )

    # 打印结果
    print(f"\n状态: {result['status']}")
    print(f"Skill ID: {result['skill_id']}")
    print(f"Run ID: {result['run_id']}")

    if result['status'] == 'completed':
        print("\n--- Gate 决策 ---")
        print(f"裁决: {result['gate_decision']['verdict']}")
        print(f"通过检查: {result['gate_decision']['checks_passed']}")

        if result['gate_decision']['violations']:
            print("违规项:")
            for v in result['gate_decision']['violations']:
                print(f"  [{v['severity']}] {v['rule_id']}: {v['message']}")

        print("\n--- 选股结果 ---")
        data = result['data']
        print(f"选中股票数: {len(data.get('selected_stocks', []))}")

        print("\n--- 回测指标 ---")
        metrics = data.get('metrics', {})
        print(f"总收益: {metrics.get('total_return', 0):.2%}")
        print(f"年化收益: {metrics.get('annual_return', 0):.2%}")
        print(f"最大回撤: {metrics.get('max_drawdown', 0):.2%}")
        print(f"夏普比率: {metrics.get('sharpe_ratio', 0):.2f}")

        print("\n--- Evidence 引用 ---")
        print(f"Evidence Ref: {result['evidence']['evidence_ref']}")
        print(f"Data Hash: {result['evidence']['data_hash']}")

    print("\n--- 执行指标 ---")
    print(f"延迟: {result['metrics']['latency_ms']}ms")


def example_with_class():
    """使用类接口示例"""
    print("\n" + "=" * 60)
    print("示例 2: 使用类接口")
    print("=" * 60)

    # 创建 Skill 实例
    skill = StockSelectorSkill()

    # 准备输入
    input_data = {
        "start_date": "2018-01-01",
        "end_date": "2024-12-31",
        "hold_period": "W",         # 周频
        "select_num": 5,            # 选5只
        "factor_list": [
            ("ROE", False, None, 1),           # ROE，降序（高ROE优先）
            ("市值", True, None, 0.5),         # 市值，升序，权重0.5
        ],
        "filter_list": [
            ("市值", None, "val:>=1000000000"),   # 市值>=10亿
            ("收盘价", None, "pct:<=0.95"),      # 收盘价不超过前95%分位
        ],
        "initial_cash": 500000,     # 50万初始资金
        "excluded_boards": ["bj"]    # 只排除北交所
    }

    # 执行
    output = skill.execute(input_data)

    # 打印结果
    print(f"\nSkill: {output.skill_id}")
    print(f"状态: {output.status.value}")
    print(f"裁决: {output.gate_decision.verdict.value}")
    print(f"Evidence: {output.evidence.evidence_ref}")


def example_error_handling():
    """错误处理示例"""
    print("\n" + "=" * 60)
    print("示例 3: 错误处理")
    print("=" * 60)

    # 故意使用错误的输入
    result = run_stock_selector(
        start_date="invalid-date",  # 错误的日期格式
        select_num=-10              # 错误的数量
    )

    print(f"\n状态: {result['status']}")
    if result['status'] == 'rejected':
        print(f"错误码: {result['error']['error_code']}")
        print(f"错误信息: {result['error']['error_message']}")


if __name__ == "__main__":
    # 运行示例
    example_basic()
    example_with_class()
    example_error_handling()

    print("\n" + "=" * 60)
    print("示例完成")
    print("=" * 60)
