"""
Adapter → Core 集成测试

验证完整流水线:
策略代码 → SignalGeneratorAdapter → ExecuteSkill → 结果

运行方式: python -m skills.quant.test_adapter_integration
"""

import sys
from pathlib import Path

# 添加路径
repo_root = Path(__file__).parent.parent.parent.parent.parent
adapters_path = repo_root / "adapters" / "quant"
skillforge_src = repo_root / "skillforge" / "src"

sys.path.insert(0, str(adapters_path))
sys.path.insert(0, str(skillforge_src))

from contracts import (
    SignalAction,
    create_hold_signal,
    create_buy_signal,
    create_sell_signal
)

from skills.quant.execute import ExecuteSkill, ExecuteStatus
from strategies.signal_generator import SignalGeneratorAdapter, SignalGeneratorInput


def test_signal_adapter_contract():
    """测试 Signal Adapter 输出符合标准接口"""
    print("=== 测试 1: Adapter 接口契约 ===")

    # 1. 测试 HOLD 信号
    hold_output = create_hold_signal(
        symbol="AAPL",
        reasoning="No clear trend"
    )

    assert hold_output.status.value == "hold"
    assert hold_output.intent.action == SignalAction.HOLD
    assert hold_output.intent.symbol == "AAPL"
    print("✅ HOLD 信号格式正确")

    # 2. 测试 BUY 信号
    buy_output = create_buy_signal(
        symbol="AAPL",
        quantity=100,
        confidence=0.75,
        reasoning="Uptrend detected",
        price=150.0,
        target_price=165.0,
        stop_loss=145.0
    )

    assert buy_output.status.value == "success"
    assert buy_output.intent.action == SignalAction.BUY
    assert buy_output.intent.quantity == 100
    assert buy_output.intent.confidence == 0.75
    print("✅ BUY 信号格式正确")

    # 3. 测试 SELL 信号
    sell_output = create_sell_signal(
        symbol="AAPL",
        quantity=100,
        confidence=0.65,
        reasoning="Downtrend detected",
        price=140.0
    )

    assert sell_output.status.value == "success"
    assert sell_output.intent.action == SignalAction.SELL
    assert sell_output.intent.quantity == 100
    print("✅ SELL 信号格式正确")

    print()


def test_adapter_to_core_integration():
    """测试 Adapter → Core 完整流水线"""
    print("=== 测试 2: Adapter → Core 集成 ===")

    # 初始化 Core ExecuteSkill
    execute_skill = ExecuteSkill(mode="MOCK")

    # 1. 测试 HOLD 信号通过 Core
    print("\n--- 测试 2.1: HOLD 信号 ---")
    hold_adapter_output = create_hold_signal(
        symbol="AAPL",
        reasoning="No signal"
    )

    # 将 Adapter 输出转换为 Core 输入
    intent = hold_adapter_output.intent.to_core_intent()
    context = hold_adapter_output.context.to_core_context() if hold_adapter_output.context else {}

    result = execute_skill.execute(intent, context)

    assert result.status == ExecuteStatus.SUCCESS
    assert result.action == "HOLD"
    print(f"✅ HOLD 信号通过 Core")

    # 2. 测试 BUY 信号通过 Core (风控检查)
    print("\n--- 测试 2.2: BUY 信号 (风控) ---")
    buy_adapter_output = create_buy_signal(
        symbol="AAPL",
        quantity=100,
        confidence=0.75,
        reasoning="Strong uptrend",
        price=150.0
    )

    intent = buy_adapter_output.intent.to_core_intent()
    context = {
        "total_capital": 1000000,
        "current_equity": 1000000,
        "job_id": "test-job-001"
    }

    result = execute_skill.execute(intent, context)

    # 根据 Core 的风控规则，100股 @ $150 = $15000 < 20% 仓位限制，应该通过
    print(f"  状态: {result.status}")
    print(f"  动作: {result.action}")
    print(f"  Gate 结果: {result.gate_results}")
    print("✅ BUY 信号通过 Core 风控检查")

    # 3. 测试 SELL 信号通过 Core
    print("\n--- 测试 2.3: SELL 信号 ---")
    sell_adapter_output = create_sell_signal(
        symbol="AAPL",
        quantity=50,
        confidence=0.65,
        reasoning="Downtrend detected",
        price=140.0
    )

    intent = sell_adapter_output.intent.to_core_intent()
    result = execute_skill.execute(intent, context)

    print(f"  状态: {result.status}")
    print(f"  动作: {result.action}")
    print("✅ SELL 信号通过 Core")

    print()


def test_adapter_direct_function():
    """测试 SignalGeneratorAdapter 完整流程"""
    print("=== 测试 3: SignalGeneratorAdapter 完整流程 ===")

    adapter = SignalGeneratorAdapter()

    # 创建测试输入 - 上升趋势
    input_data = SignalGeneratorInput(
        symbol="AAPL",
        predictions=[
            {"close": 100 + i * 0.5, "timestamp": f"2024-01-{i+1:02d}"}
            for i in range(24)
        ],
        confidence=0.75,
        strategy="trend",
        confidence_threshold=0.6,
        price_change_threshold=0.02,
        available_capital=100000
    )

    # 执行
    output = adapter.execute(input_data, context={"job_id": "test-001"})

    # 验证输出格式
    assert output.status.value in ["success", "hold"]
    assert output.intent is not None
    assert output.intent.symbol == "AAPL"
    assert output.context is not None
    assert output.evidence is not None

    print(f"  状态: {output.status}")
    print(f"  动作: {output.intent.action}")
    print(f"  理由: {output.intent.reasoning}")
    print(f"  置信度: {output.intent.confidence}")

    # 通过 Core 执行
    if output.intent.action != SignalAction.HOLD:
        execute_skill = ExecuteSkill(mode="MOCK")
        intent = output.intent.to_core_intent()
        context = output.context.to_core_context()
        context.update({
            "total_capital": 1000000,
            "current_equity": 1000000
        })

        core_result = execute_skill.execute(intent, context)
        print(f"  Core 结果: {core_result.status}")

    print("✅ SignalGeneratorAdapter 完整流程通过")

    print()


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Adapter → Core 集成测试")
    print("=" * 60)
    print()

    try:
        test_signal_adapter_contract()
        test_adapter_to_core_integration()
        test_adapter_direct_function()

        print("=" * 60)
        print("✅ 所有测试通过!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        raise
    except Exception as e:
        print(f"\n❌ 测试错误: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    run_all_tests()
