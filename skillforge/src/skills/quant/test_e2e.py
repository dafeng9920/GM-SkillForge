"""
端到端测试 - 量化执行流水线

测试场景:
1. 正常买入
2. 仓位超限拒绝
3. 回撤熔断
4. HOLD 信号放行
"""
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from skills.quant import (
    risk_guard,
    drawdown_limiter,
    order_router,
    execute,
    RiskGuard,
    DrawdownLimiter,
    OrderRouter,
    ExecuteSkill,
)


def test_normal_buy():
    """测试正常买入"""
    print("\n=== 测试 1: 正常买入 ===")

    result = execute(
        action="BUY",
        symbol="AAPL",
        quantity=100,
        price=150.0,
        mode="MOCK",
        context={"total_capital": 1000000, "current_equity": 1000000}
    )

    print(f"状态: {result['status']}")
    print(f"订单ID: {result['order_id']}")
    print(f"Gate 结果: {result['gate_results']}")

    assert result["status"] == "SUCCESS", f"预期 SUCCESS，实际 {result['status']}"
    assert result["order_id"] is not None, "预期有订单ID"
    print("✅ 通过")


def test_position_limit_exceeded():
    """测试仓位超限"""
    print("\n=== 测试 2: 仓位超限拒绝 ===")

    result = execute(
        action="BUY",
        symbol="AAPL",
        quantity=20000,  # 3M 美元，超过 10% 仓位限制
        price=150.0,
        mode="MOCK",
        context={"total_capital": 1000000, "current_equity": 1000000}
    )

    print(f"状态: {result['status']}")
    print(f"错误: {result['error']}")
    print(f"Gate 结果: {result['gate_results']}")

    assert result["status"] == "REJECTED", f"预期 REJECTED，实际 {result['status']}"
    assert "risk_guard" in result["gate_results"]
    print("✅ 通过")


def test_hold_signal():
    """测试 HOLD 信号"""
    print("\n=== 测试 3: HOLD 信号放行 ===")

    result = execute(
        action="HOLD",
        symbol="AAPL",
        quantity=0,
        mode="MOCK",
        context={"total_capital": 1000000, "current_equity": 1000000}
    )

    print(f"状态: {result['status']}")
    print(f"订单ID: {result['order_id']}")

    assert result["status"] == "SUCCESS", f"预期 SUCCESS，实际 {result['status']}"
    assert result["order_id"] is None, "HOLD 不应有订单ID"
    print("✅ 通过")


def test_drawdown_warning():
    """测试回撤警告"""
    print("\n=== 测试 4: 回撤警告 ===")

    # 使用类实例以保持状态
    limiter = DrawdownLimiter()

    # 先设置 peak
    limiter.update_equity(1000000)

    # 模拟 6% 回撤 (超过 5% 警告线)
    result = limiter.execute(
        {"current_equity": 940000},  # 从 1M 跌到 940K = 6% 回撤
        context={"job_id": "test-001"}
    )

    print(f"裁决: {result.verdict.value}")
    print(f"状态: {limiter.get_state().value}")
    print(f"当前回撤: {limiter._current_drawdown:.2%}")

    assert result.verdict.value == "WARN", f"预期 WARN，实际 {result.verdict.value}"
    print("✅ 通过")


def test_order_router_mock():
    """测试订单路由 Mock 模式"""
    print("\n=== 测试 5: 订单路由 Mock 模式 ===")

    result = order_router(
        action="BUY",
        symbol="TSLA",
        quantity=50,
        price=200.0,
        mode="MOCK"
    )

    print(f"订单ID: {result['order_id']}")
    print(f"状态: {result['status']}")
    print(f"场所: {result['venue']}")

    assert result["status"] == "FILLED", f"预期 FILLED，实际 {result['status']}"
    assert result["venue"] == "MOCK"
    print("✅ 通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("量化执行流水线 - 端到端测试")
    print("=" * 50)

    tests = [
        test_normal_buy,
        test_position_limit_exceeded,
        test_hold_signal,
        test_drawdown_warning,
        test_order_router_mock,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ 失败: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ 错误: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"结果: {passed} 通过, {failed} 失败")
    print("=" * 50)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
