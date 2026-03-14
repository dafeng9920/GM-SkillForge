"""
诱多识别器演示 - Week 2 防骗能力层

展示5种诱多模式的检测功能
"""

from datetime import datetime, timezone
from trap_detector import TrapDetector, MarketData, TrapType, TrapSeverity


def print_separator(title=""):
    """打印分隔线"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    else:
        print(f"{'-'*60}")


def demo_end_of_day_rally():
    """演示1: 尾盘拉升诱多"""
    print_separator("演示1: 尾盘拉升诱多")

    detector = TrapDetector()

    # 模拟14:45尾盘突然拉升，但成交量没有明显配合
    data = MarketData(
        symbol="DEMO001",
        current_price=103.0,
        current_time=datetime.now().replace(hour=14, minute=45),
        price_history=[100.0] * 15 + [101.0, 102.0, 103.0],
        volume_history=[1000] * 15 + [1080, 1050, 1100],  # 成交量没有明显放大
        timestamps=[datetime.now()] * 18,
        prev_close=100.0
    )

    result = detector.detect_all(data)

    print(f"股票代码: {data.symbol}")
    print(f"当前价格: {data.current_price:.2f}")
    print(f"当前时间: {data.current_time.strftime('%H:%M')}")
    print(f"尾盘涨幅: {(data.current_price / data.price_history[15] - 1) * 100:.2f}%")
    print()
    print(f"检测结果: {'🚨 诱多陷阱' if result.is_trap else '✅ 正常'}")
    print(f"原因: {result.reason}")
    print(f"综合置信度: {result.overall_confidence:.1%}")

    if result.patterns:
        pattern = result.patterns[0]
        print(f"\n模式详情:")
        print(f"  描述: {pattern.description}")
        print(f"  严重程度: {pattern.severity.name}")
        print(f"  建议操作: {pattern.suggested_action}")
        print(f"  预期跌幅: {pattern.expected_decline:.1%}")


def demo_fake_breakout():
    """演示2: 假突破诱多"""
    print_separator("演示2: 假突破诱多")

    detector = TrapDetector()

    # 模拟突破102后快速回落
    data = MarketData(
        symbol="DEMO002",
        current_price=101.5,
        current_time=datetime.now(),
        price_history=[100.0] * 15 + [101.0, 102.5, 102.3, 101.8, 101.5],
        volume_history=[1000] * 15 + [1500, 1800, 1200, 1000, 900],  # 成交量先放后缩
        resistance_level=102.0,
        timestamps=[datetime.now()] * 20
    )

    result = detector.detect_all(data)

    print(f"股票代码: {data.symbol}")
    print(f"当前价格: {data.current_price:.2f}")
    print(f"阻力位: {data.resistance_level:.2f}")
    print(f"突破幅度: {(max(data.price_history[-5:]) / data.resistance_level - 1) * 100:.2f}%")
    print()
    print(f"检测结果: {'🚨 诱多陷阱' if result.is_trap else '✅ 正常'}")
    print(f"原因: {result.reason}")

    if result.patterns:
        pattern = result.patterns[0]
        print(f"\n模式详情:")
        print(f"  描述: {pattern.description}")
        print(f"  建议操作: {pattern.suggested_action}")


def demo_volume_stagnation():
    """演示3: 放量滞涨诱多"""
    print_separator("演示3: 放量滞涨诱多")

    detector = TrapDetector()

    # 模拟成交量放大1.5倍，但价格只涨0.3%
    data = MarketData(
        symbol="DEMO003",
        current_price=100.3,
        current_time=datetime.now(),
        price_history=[100.0] * 5 + [100.1, 100.2, 100.25, 100.3, 100.3],
        volume_history=[1000] * 5 + [1400, 1500, 1600, 1550, 1500],  # 放量
        timestamps=[datetime.now()] * 10
    )

    result = detector.detect_all(data)

    print(f"股票代码: {data.symbol}")
    print(f"当前价格: {data.current_price:.2f}")
    print(f"价格涨幅: {(data.current_price / data.price_history[0] - 1) * 100:.2f}%")
    print(f"成交量倍数: {sum(data.volume_history[-5:]) / sum(data.volume_history[:5]):.1f}x")
    print()
    print(f"检测结果: {'🚨 诱多陷阱' if result.is_trap else '✅ 正常'}")
    print(f"原因: {result.reason}")

    if result.patterns:
        pattern = result.patterns[0]
        print(f"\n模式详情:")
        print(f"  描述: {pattern.description}")
        print(f"  信号: 放量{pattern.signals['volume_ratio']:.1f}倍但价格{pattern.signals['price_change']*100:+.2f}%")


def demo_money_divergence():
    """演示4: 资金背离诱多"""
    print_separator("演示4: 资金背离诱多")

    detector = TrapDetector()

    # 模拟价格上涨2%，但主力资金流出
    data = MarketData(
        symbol="DEMO004",
        current_price=102.0,
        current_time=datetime.now(),
        price_history=[100.0, 100.5, 101.0, 101.5, 102.0],
        net_inflow=-500000,  # 净流出50万
        main_inflow=-800000,  # 主力流出80万
        retail_inflow=300000,  # 散户流入30万
        timestamps=[datetime.now()] * 5
    )

    result = detector.detect_all(data)

    print(f"股票代码: {data.symbol}")
    print(f"当前价格: {data.current_price:.2f}")
    print(f"价格涨幅: {(data.current_price / data.price_history[0] - 1) * 100:.2f}%")
    print(f"资金流向: {data.net_inflow/10000:.1f}万")
    print(f"主力流向: {data.main_inflow/10000:.1f}万")
    print(f"散户流向: {data.retail_inflow/10000:.1f}万")
    print()
    print(f"检测结果: {'🚨 诱多陷阱' if result.is_trap else '✅ 正常'}")
    print(f"原因: {result.reason}")

    if result.patterns:
        pattern = result.patterns[0]
        print(f"\n模式详情:")
        print(f"  描述: {pattern.description}")
        print(f"  建议操作: {pattern.suggested_action}")
        print(f"  预期跌幅: {pattern.expected_decline:.1%}")


def demo_news_trap():
    """演示5: 消息诱多"""
    print_separator("演示5: 消息诱多")

    detector = TrapDetector()

    # 模拟利好消息发布，但价格反应弱且主力出货
    data = MarketData(
        symbol="DEMO005",
        current_price=100.3,
        current_time=datetime.now(),
        price_history=[100.0] * 5 + [100.1, 100.2, 100.25, 100.3, 100.3],
        volume_history=[1000] * 5 + [1400, 1500, 1600, 1550, 1500],
        has_news=True,
        news_sentiment="positive",
        main_inflow=-500000,  # 主力流出
        timestamps=[datetime.now()] * 10
    )

    result = detector.detect_all(data)

    print(f"股票代码: {data.symbol}")
    print(f"当前价格: {data.current_price:.2f}")
    print(f"重大消息: {'是' if data.has_news else '否'}")
    print(f"消息情绪: {data.news_sentiment}")
    print(f"价格反应: {(data.current_price / data.price_history[0] - 1) * 100:+.2f}%")
    print(f"主力流向: {data.main_inflow/10000:.1f}万")
    print()
    print(f"检测结果: {'🚨 诱多陷阱' if result.is_trap else '✅ 正常'}")
    print(f"原因: {result.reason}")

    if result.patterns:
        pattern = result.patterns[0]
        print(f"\n模式详情:")
        print(f"  描述: {pattern.description}")
        print(f"  建议操作: {pattern.suggested_action}")


def demo_healthy_rise():
    """演示6: 健康上涨（不触发诱多）"""
    print_separator("演示6: 健康上涨（对比）")

    detector = TrapDetector()

    # 模拟健康的上涨：放量上涨 + 资金流入
    data = MarketData(
        symbol="DEMO006",
        current_price=103.0,
        current_time=datetime.now(),
        price_history=[100.0] * 5 + [100.8, 101.5, 102.0, 102.5, 103.0],
        volume_history=[1000] * 5 + [1200, 1400, 1600, 1800, 2000],  # 放量上涨
        net_inflow=1500000,  # 资金流入
        main_inflow=1000000,  # 主力流入
        retail_inflow=500000,  # 散户流入
        timestamps=[datetime.now()] * 10
    )

    result = detector.detect_all(data)

    print(f"股票代码: {data.symbol}")
    print(f"当前价格: {data.current_price:.2f}")
    print(f"价格涨幅: {(data.current_price / data.price_history[0] - 1) * 100:.2f}%")
    print(f"成交量趋势: 放量上涨")
    print(f"资金流向: 净流入{data.net_inflow/10000:.0f}万")
    print()
    print(f"检测结果: {'🚨 诱多陷阱' if result.is_trap else '✅ 正常'}")
    print(f"原因: {result.reason}")
    print(f"是否应避免: {'是' if result.should_avoid else '否'}")


def demo_statistics():
    """演示7: 检测统计"""
    print_separator("演示7: 检测统计")

    detector = TrapDetector()

    # 运行多次检测
    symbols = ["STAT001", "STAT002", "STAT003", "STAT004", "STAT005"]
    for symbol in symbols:
        data = MarketData(
            symbol=symbol,
            current_price=102.0,
            current_time=datetime.now(),
            price_history=[100.0] * 10,
            timestamps=[datetime.now()] * 10
        )
        detector.detect_all(data)

    stats = detector.get_statistics()

    print(f"总检测次数: {stats['total_detections']}")
    print(f"检测到诱多: {stats['trap_count']} 次")
    print(f"诱多检出率: {stats['trap_rate']:.1%}")
    print()
    print("各检测器统计:")
    for det_stat in stats['detector_stats']:
        print(f"  {det_stat['name']}: {det_stat['detection_count']} 次")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  诱多识别器演示 - Week 2 防骗能力层")
    print("  5种诱多模式检测功能展示")
    print("="*60)

    # 运行所有演示
    demo_end_of_day_rally()
    demo_fake_breakout()
    demo_volume_stagnation()
    demo_money_divergence()
    demo_news_trap()
    demo_healthy_rise()
    demo_statistics()

    print_separator("演示完成")
    print("\n📋 总结:")
    print("  ✅ 尾盘拉升检测器 - 识别收盘前突然拉升")
    print("  ✅ 假突破检测器 - 识别突破后快速回落")
    print("  ✅ 放量滞涨检测器 - 识别放量不涨")
    print("  ✅ 资金背离检测器 - 识别价涨资出")
    print("  ✅ 消息诱多检测器 - 识别利好出货")
    print("\n  💡 核心价值: 在买入前识别诱多陷阱，避免追高被套")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
