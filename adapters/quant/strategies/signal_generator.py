"""
P0-04: signal-generator Skill
根据预测结果生成交易信号

版本: 1.0.0
层级: research
依赖: kronos-predict (上游)

输入: 预测结果 + 置信度
输出: BUY/SELL/HOLD 信号 + Evidence
"""

import sys
import time
import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, List, Dict
import math

# 导入基础类
sys.path.insert(0, str(Path(__file__).parent.parent))
from skills.base import (
    QuantSkillBase,
    QuantSkillOutput,
    SkillStatus,
    GateVerdict,
    Severity,
    Evidence,
    Provenance,
    GateDecision,
    Violation,
    SkillError,
    SkillMetrics,
    TraceContext
)


# ============================================
# 信号类型
# ============================================

class SignalAction(str):
    """信号动作"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


# ============================================
# 输入合同
# ============================================

@dataclass
class SignalGeneratorInput:
    """信号生成输入"""

    # 必填
    predictions: List[Dict]           # 预测结果 (来自 kronos-predict)
    confidence_metrics: Dict          # 置信度指标

    # 可选 - 策略参数
    strategy: str = "trend"           # 策略类型: trend, reversal, breakout
    confidence_threshold: float = 0.6  # 置信度阈值
    price_change_threshold: float = 0.02  # 价格变化阈值 (2%)
    risk_reward_ratio: float = 2.0    # 风险收益比
    max_signals: int = 10             # 最大信号数

    # 可选 - 上下文
    current_position: Optional[Dict] = None  # 当前持仓
    available_capital: float = 100000        # 可用资金

    def validate(self) -> List[str]:
        """验证输入"""
        errors = []

        if not self.predictions:
            errors.append("predictions 不能为空")

        if self.confidence_threshold < 0 or self.confidence_threshold > 1:
            errors.append("confidence_threshold 必须在 0-1 之间")

        if self.price_change_threshold < 0:
            errors.append("price_change_threshold 必须大于 0")

        valid_strategies = ["trend", "reversal", "breakout", "balanced"]
        if self.strategy not in valid_strategies:
            errors.append(f"strategy 必须是: {valid_strategies}")

        return errors


# ============================================
# 输出数据模型
# ============================================

@dataclass
class TradingSignal:
    """交易信号"""
    symbol: str
    action: str                       # BUY, SELL, HOLD
    confidence: float                 # 信号置信度
    target_price: Optional[float]     # 目标价格
    stop_loss: Optional[float]        # 止损价格
    quantity: Optional[int]           # 建议数量
    reasoning: str                    # 信号理由
    timestamp: str

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "action": self.action,
            "confidence": round(self.confidence, 4),
            "target_price": self.target_price,
            "stop_loss": self.stop_loss,
            "quantity": self.quantity,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp
        }


@dataclass
class SignalGeneratorData:
    """信号生成输出数据"""
    signals: List[TradingSignal]
    strategy_used: str
    market_analysis: Dict

    def to_dict(self) -> dict:
        return {
            "signals": [s.to_dict() for s in self.signals],
            "signal_count": len(self.signals),
            "strategy_used": self.strategy_used,
            "market_analysis": self.market_analysis
        }


# ============================================
# Skill 实现
# ============================================

class SignalGeneratorSkill(QuantSkillBase):
    """
    信号生成 Skill

    根据预测结果和策略规则生成交易信号
    """

    SKILL_ID = "signal-generator"
    VERSION = "1.0.0"
    DESCRIPTION = "根据预测结果生成交易信号"

    def __init__(self):
        super().__init__(skill_id=self.SKILL_ID, version=self.VERSION)

    def _validate_input(self, input_data: dict) -> List[str]:
        """验证输入"""
        errors = []

        if "predictions" not in input_data:
            errors.append("缺少 predictions 字段")

        if "confidence_metrics" not in input_data:
            errors.append("缺少 confidence_metrics 字段")

        return errors

    def _analyze_predictions(self, predictions: List[Dict]) -> Dict:
        """分析预测结果"""
        if not predictions:
            return {"trend": "neutral", "volatility": 0, "change_pct": 0}

        # 提取收盘价
        closes = [p.get("close", 0) for p in predictions if p.get("close")]

        if len(closes) < 2:
            return {"trend": "neutral", "volatility": 0, "change_pct": 0}

        # 计算趋势
        first_close = closes[0]
        last_close = closes[-1]
        change_pct = (last_close - first_close) / first_close if first_close else 0

        # 计算波动率
        returns = [(closes[i] - closes[i-1]) / closes[i-1]
                   for i in range(1, len(closes)) if closes[i-1]]
        volatility = math.sqrt(sum(r**2 for r in returns) / len(returns)) if returns else 0

        # 判断趋势
        if change_pct > 0.02:
            trend = "bullish"
        elif change_pct < -0.02:
            trend = "bearish"
        else:
            trend = "neutral"

        return {
            "trend": trend,
            "volatility": round(volatility, 4),
            "change_pct": round(change_pct, 4),
            "first_close": first_close,
            "last_close": last_close,
            "high": max(closes),
            "low": min(closes)
        }

    def _generate_trend_signal(
        self,
        symbol: str,
        predictions: List[Dict],
        confidence: float,
        analysis: Dict,
        threshold: float
    ) -> TradingSignal:
        """趋势策略信号"""

        change_pct = analysis["change_pct"]
        trend = analysis["trend"]

        if trend == "bullish" and change_pct > threshold and confidence > 0.6:
            action = "BUY"
            reasoning = f"上升趋势: 预测涨幅 {change_pct:.2%}, 置信度 {confidence:.2%}"
        elif trend == "bearish" and change_pct < -threshold and confidence > 0.6:
            action = "SELL"
            reasoning = f"下降趋势: 预测跌幅 {change_pct:.2%}, 置信度 {confidence:.2%}"
        else:
            action = "HOLD"
            reasoning = f"趋势不明确或置信度不足: 趋势={trend}, 变化={change_pct:.2%}"

        # 计算目标价和止损价
        last_close = analysis.get("last_close", 100)
        if action == "BUY":
            target_price = last_close * (1 + abs(change_pct) * 1.5)
            stop_loss = last_close * 0.97  # 3% 止损
        elif action == "SELL":
            target_price = None
            stop_loss = None
        else:
            target_price = None
            stop_loss = None

        return TradingSignal(
            symbol=symbol,
            action=action,
            confidence=confidence,
            target_price=round(target_price, 2) if target_price else None,
            stop_loss=round(stop_loss, 2) if stop_loss else None,
            quantity=None,
            reasoning=reasoning,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    def _generate_reversal_signal(
        self,
        symbol: str,
        predictions: List[Dict],
        confidence: float,
        analysis: Dict,
        threshold: float
    ) -> TradingSignal:
        """反转策略信号"""

        closes = [p.get("close", 0) for p in predictions if p.get("close")]

        if len(closes) < 5:
            return TradingSignal(
                symbol=symbol,
                action="HOLD",
                confidence=confidence,
                target_price=None,
                stop_loss=None,
                quantity=None,
                reasoning="数据不足",
                timestamp=datetime.now(timezone.utc).isoformat()
            )

        # 检测连续上涨或下跌后的反转
        early_trend = "up" if closes[0] < closes[4] else "down"
        late_trend = "up" if closes[-5] < closes[-1] else "down"

        # 反转信号
        if early_trend == "up" and late_trend == "down" and confidence > 0.6:
            action = "SELL"
            reasoning = "检测到上涨后的反转信号"
        elif early_trend == "down" and late_trend == "up" and confidence > 0.6:
            action = "BUY"
            reasoning = "检测到下跌后的反转信号"
        else:
            action = "HOLD"
            reasoning = "未检测到明显的反转模式"

        last_close = closes[-1] if closes else 100
        if action == "BUY":
            target_price = last_close * 1.05
            stop_loss = last_close * 0.97
        elif action == "SELL":
            target_price = None
            stop_loss = None
        else:
            target_price = None
            stop_loss = None

        return TradingSignal(
            symbol=symbol,
            action=action,
            confidence=confidence,
            target_price=round(target_price, 2) if target_price else None,
            stop_loss=round(stop_loss, 2) if stop_loss else None,
            quantity=None,
            reasoning=reasoning,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    def _generate_breakout_signal(
        self,
        symbol: str,
        predictions: List[Dict],
        confidence: float,
        analysis: Dict,
        threshold: float
    ) -> TradingSignal:
        """突破策略信号"""

        high = analysis.get("high", 0)
        low = analysis.get("low", 0)
        last_close = analysis.get("last_close", 100)

        if high == 0 or low == 0:
            return TradingSignal(
                symbol=symbol,
                action="HOLD",
                confidence=confidence,
                target_price=None,
                stop_loss=None,
                quantity=None,
                reasoning="无法计算突破水平",
                timestamp=datetime.now(timezone.utc).isoformat()
            )

        # 计算突破水平
        range_price = high - low
        resistance = high
        support = low

        # 检测突破
        if last_close > resistance * 0.99 and confidence > 0.6:
            action = "BUY"
            reasoning = f"突破阻力位 {resistance:.2f}"
            target_price = last_close * 1.05
            stop_loss = support
        elif last_close < support * 1.01 and confidence > 0.6:
            action = "SELL"
            reasoning = f"跌破支撑位 {support:.2f}"
            target_price = None
            stop_loss = None
        else:
            action = "HOLD"
            reasoning = f"价格在支撑 {support:.2f} 和阻力 {resistance:.2f} 之间"

        return TradingSignal(
            symbol=symbol,
            action=action,
            confidence=confidence,
            target_price=round(target_price, 2) if target_price else None,
            stop_loss=round(stop_loss, 2) if stop_loss else None,
            quantity=None,
            reasoning=reasoning,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    def _build_gate_decision(
        self,
        signal: TradingSignal,
        confidence_threshold: float
    ) -> GateDecision:
        """构建 Gate 决策"""
        violations = []
        checks_passed = []

        # 检查 1: 信号置信度
        if signal.confidence < confidence_threshold:
            violations.append(Violation(
                rule_id="LOW_SIGNAL_CONFIDENCE",
                severity=Severity.WARNING,
                message=f"信号置信度 {signal.confidence:.2%} 低于阈值 {confidence_threshold:.2%}",
                actual_value=signal.confidence,
                threshold=confidence_threshold
            ))
        else:
            checks_passed.append("signal_confidence")

        # 检查 2: HOLD 信号
        if signal.action == "HOLD":
            checks_passed.append("hold_signal")
        else:
            checks_passed.append("actionable_signal")

        # 计算裁决
        if signal.action == "HOLD":
            verdict = GateVerdict.ALLOW  # HOLD 总是允许
        elif signal.confidence < confidence_threshold:
            verdict = GateVerdict.WARN
        else:
            verdict = GateVerdict.ALLOW

        return GateDecision(
            verdict=verdict,
            checks_passed=checks_passed,
            violations=violations
        )

    def execute(
        self,
        input_data: dict,
        trace_context: Optional[TraceContext] = None
    ) -> QuantSkillOutput:
        """执行信号生成"""
        start_time = time.time()

        # 1. 输入验证
        validation_errors = self._validate_input(input_data)
        if validation_errors:
            return self.create_rejected_output(
                error_code="INPUT_VALIDATION_FAILED",
                error_message="; ".join(validation_errors),
                validation_errors=validation_errors,
                trace_context=trace_context
            )

        # 2. 提取参数
        predictions = input_data.get("predictions", [])
        confidence_metrics = input_data.get("confidence_metrics", {})
        strategy = input_data.get("strategy", "trend")
        confidence_threshold = input_data.get("confidence_threshold", 0.6)
        price_change_threshold = input_data.get("price_change_threshold", 0.02)
        symbol = input_data.get("symbol", "UNKNOWN")

        # 3. 分析预测结果
        analysis = self._analyze_predictions(predictions)

        # 4. 获取置信度
        confidence = confidence_metrics.get("mean", 0.5)

        # 5. 根据策略生成信号
        if strategy == "trend":
            signal = self._generate_trend_signal(
                symbol, predictions, confidence, analysis, price_change_threshold
            )
        elif strategy == "reversal":
            signal = self._generate_reversal_signal(
                symbol, predictions, confidence, analysis, price_change_threshold
            )
        elif strategy == "breakout":
            signal = self._generate_breakout_signal(
                symbol, predictions, confidence, analysis, price_change_threshold
            )
        else:
            signal = TradingSignal(
                symbol=symbol,
                action="HOLD",
                confidence=confidence,
                target_price=None,
                stop_loss=None,
                quantity=None,
                reasoning="未知策略",
                timestamp=datetime.now(timezone.utc).isoformat()
            )

        # 6. 构建 Gate 决策
        gate_decision = self._build_gate_decision(signal, confidence_threshold)

        # 7. 构建输出数据
        output_data = SignalGeneratorData(
            signals=[signal],
            strategy_used=strategy,
            market_analysis=analysis
        )

        latency_ms = int((time.time() - start_time) * 1000)

        # 8. 构建成功输出
        return self.create_success_output(
            data=output_data.to_dict(),
            provenance=Provenance(
                source="signal-generator",
                version=self.VERSION
            ),
            gate_decision=gate_decision,
            metrics=SkillMetrics(
                latency_ms=latency_ms,
                rows_processed=len(predictions)
            ),
            trace_context=trace_context
        )

    def run(self, input_dict: dict) -> dict:
        """标准运行接口"""
        output = self.execute(input_dict)
        return output.to_dict()


# ============================================
# 便捷函数
# ============================================

def generate_signals(
    predictions: List[Dict],
    confidence_metrics: Dict,
    strategy: str = "trend",
    confidence_threshold: float = 0.6
) -> dict:
    """生成交易信号的便捷函数"""
    skill = SignalGeneratorSkill()

    input_data = {
        "predictions": predictions,
        "confidence_metrics": confidence_metrics,
        "strategy": strategy,
        "confidence_threshold": confidence_threshold
    }

    return skill.run(input_data)


# ============================================
# CLI 入口
# ============================================

def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="信号生成器")
    parser.add_argument("--strategy", default="trend", help="策略类型")
    parser.add_argument("--mock", action="store_true", help="使用模拟数据")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    # 生成模拟数据
    if args.mock:
        predictions = [
            {"close": 100 + i * 0.5, "timestamp": f"2024-01-{i+1:02d}"}
            for i in range(24)
        ]
        confidence_metrics = {"mean": 0.72, "std": 0.15}
    else:
        print("请提供预测数据")
        return

    result = generate_signals(
        predictions=predictions,
        confidence_metrics=confidence_metrics,
        strategy=args.strategy
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"结果已保存到: {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
