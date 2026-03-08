"""
P0-03: kronos-predict Skill
使用 Kronos 模型预测未来 K线

版本: 1.0.0
层级: research
依赖: Kronos (MIT)

输入: 历史 OHLCV 数据
输出: 预测 K线 + 置信度 + Evidence
"""

import sys
import time
import json
import hashlib
import random
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, List, Dict

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
# 错误码定义
# ============================================

ERROR_CODES = {
    "INPUT_VALIDATION_FAILED": "输入验证失败",
    "CONTEXT_OVERFLOW": "输入上下文超过模型最大长度",
    "LOW_CONFIDENCE": "预测置信度低于阈值",
    "MODEL_NOT_LOADED": "模型未加载",
    "PREDICTION_TIMEOUT": "预测超时",
    "TOKENIZER_MISMATCH": "Tokenizer 与模型版本不匹配",
    "DATA_INSUFFICIENT": "输入数据不足",
    "INVALID_INTERVAL": "无效的时间间隔"
}


# ============================================
# 输入合同
# ============================================

@dataclass
class KronosPredictInput:
    """Kronos 预测输入"""

    # 必填
    symbol: str                    # 标的代码
    ohlcv_data: List[Dict]         # 历史 OHLCV 数据

    # 可选 - 模型参数
    lookback: int = 400            # 回看长度 (max: 512)
    pred_len: int = 120            # 预测长度 (max: 240)
    interval: str = "5min"         # 时间间隔
    model_version: str = "kronos-small"  # 模型版本

    # 可选 - 控制参数
    confidence_threshold: float = 0.5  # 置信度阈值
    timeout_ms: int = 60000            # 超时时间

    def validate(self) -> List[str]:
        """验证输入"""
        errors = []

        if not self.symbol:
            errors.append("symbol 不能为空")

        if not self.ohlcv_data or len(self.ohlcv_data) == 0:
            errors.append("ohlcv_data 不能为空")

        if self.lookback < 50:
            errors.append("lookback 不能小于 50")
        if self.lookback > 512:
            errors.append("lookback 不能超过 512")

        if self.pred_len < 1:
            errors.append("pred_len 必须大于 0")
        if self.pred_len > 240:
            errors.append("pred_len 不能超过 240")

        valid_intervals = ["1min", "5min", "15min", "30min", "1h", "4h", "1d"]
        if self.interval not in valid_intervals:
            errors.append(f"interval 必须是: {valid_intervals}")

        if self.confidence_threshold < 0 or self.confidence_threshold > 1:
            errors.append("confidence_threshold 必须在 0-1 之间")

        return errors

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "lookback": self.lookback,
            "pred_len": self.pred_len,
            "interval": self.interval,
            "model_version": self.model_version,
            "data_count": len(self.ohlcv_data)
        }


# ============================================
# 输出数据模型
# ============================================

@dataclass
class PredictionResult:
    """单条预测结果"""
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
        }


@dataclass
class ConfidenceMetrics:
    """置信度指标"""
    mean: float
    std: float
    percentile_25: float
    percentile_75: float
    min: float
    max: float

    def to_dict(self) -> dict:
        return {
            "mean": round(self.mean, 4),
            "std": round(self.std, 4),
            "percentile_25": round(self.percentile_25, 4),
            "percentile_75": round(self.percentile_75, 4),
            "min": round(self.min, 4),
            "max": round(self.max, 4)
        }


@dataclass
class ModelInfo:
    """模型信息"""
    version: str
    commit_sha: str
    tokenizer_version: str
    params_count: str

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "commit_sha": self.commit_sha,
            "tokenizer_version": self.tokenizer_version,
            "params_count": self.params_count
        }


@dataclass
class KronosPredictData:
    """Kronos 预测输出数据"""
    predictions: List[PredictionResult]
    confidence_metrics: ConfidenceMetrics
    model_info: ModelInfo
    input_hash: str

    def to_dict(self) -> dict:
        return {
            "predictions": [p.to_dict() for p in self.predictions],
            "confidence_metrics": self.confidence_metrics.to_dict(),
            "model_info": self.model_info.to_dict(),
            "input_hash": self.input_hash,
            "prediction_count": len(self.predictions)
        }


# ============================================
# Skill 实现
# ============================================

class KronosPredictSkill(QuantSkillBase):
    """
    Kronos 预测 Skill

    使用 Kronos 模型预测未来 K线走势
    """

    SKILL_ID = "kronos-predict"
    VERSION = "1.0.0"
    DESCRIPTION = "使用 Kronos 模型预测未来 K线"

    # 模型配置
    MODEL_VERSIONS = {
        "kronos-mini": {"params": "4.1M", "context": 2048},
        "kronos-small": {"params": "24.7M", "context": 512},
        "kronos-base": {"params": "102.3M", "context": 512}
    }

    def __init__(self, model_path: Optional[str] = None, mock_mode: bool = False):
        """
        初始化

        Args:
            model_path: 模型文件路径
            mock_mode: 是否使用模拟模式 (用于测试)
        """
        super().__init__(skill_id=self.SKILL_ID, version=self.VERSION)
        self.model_path = model_path
        self.mock_mode = mock_mode
        self._model = None
        self._tokenizer = None

    def _load_model(self):
        """延迟加载模型"""
        if self._model is None and not self.mock_mode:
            try:
                # 尝试加载 Kronos
                from model import Kronos, KronosTokenizer

                # 加载 tokenizer
                self._tokenizer = KronosTokenizer.from_pretrained(
                    "NeoQuasar/Kronos-Tokenizer-base"
                )

                # 加载模型
                model_name = f"NeoQuasar/{self.MODEL_VERSION}"
                self._model = Kronos.from_pretrained(model_name)

            except ImportError:
                raise ImportError(
                    "Kronos 模型未安装。\n"
                    "请参考: https://github.com/shiyu-coder/Kronos\n"
                    "或使用 mock_mode=True 进行测试"
                )

    def _compute_input_hash(self, data: List[Dict]) -> str:
        """计算输入数据哈希"""
        content = json.dumps(data, sort_keys=True, default=str)
        return f"sha256:{hashlib.sha256(content.encode()).hexdigest()[:32]}"

    def _validate_input(self, input_data: dict) -> List[str]:
        """验证输入"""
        errors = []

        # 检查必要字段
        if "symbol" not in input_data:
            errors.append("缺少 symbol 字段")

        if "ohlcv_data" not in input_data:
            errors.append("缺少 ohlcv_data 字段")
        elif len(input_data["ohlcv_data"]) < 50:
            errors.append(f"ohlcv_data 数据不足 (需要 >= 50, 实际 {len(input_data['ohlcv_data'])})")

        return errors

    def _check_context_overflow(self, data_len: int, lookback: int) -> Optional[str]:
        """检查上下文是否超限"""
        model_config = self.MODEL_VERSIONS.get("kronos-small", {})
        max_context = model_config.get("context", 512)

        if data_len > max_context:
            return f"输入数据长度 {data_len} 超过模型最大上下文 {max_context}"

        if lookback > max_context:
            return f"lookback {lookback} 超过模型最大上下文 {max_context}"

        return None

    def _mock_predict(self, input_data: dict) -> tuple:
        """
        模拟预测 (用于测试)

        Returns:
            (predictions, confidence_metrics)
        """
        pred_len = input_data.get("pred_len", 120)
        symbol = input_data.get("symbol", "UNKNOWN")
        ohlcv_data = input_data.get("ohlcv_data", [])

        # 基于最后一条数据生成模拟预测
        if ohlcv_data:
            last = ohlcv_data[-1]
            last_close = float(last.get("close", 100))
            last_time = last.get("timestamp", datetime.now().isoformat())
            last_volume = int(last.get("volume", 1000000))
        else:
            last_close = 100.0
            last_time = datetime.now().isoformat()
            last_volume = 1000000

        # 生成模拟预测
        predictions = []
        random.seed(42)  # 可复现

        def gauss(mu=0, sigma=1):
            """简单的正态分布模拟"""
            u1 = random.random()
            u2 = random.random()
            z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
            return mu + sigma * z

        for i in range(pred_len):
            # 模拟价格波动
            change = gauss(0, 0.02)  # 2% 标准差
            pred_close = last_close * (1 + change)

            # 生成 OHLC
            high = pred_close * (1 + abs(gauss(0, 0.005)))
            low = pred_close * (1 - abs(gauss(0, 0.005)))
            open_price = pred_close * (1 + gauss(0, 0.003))

            # 模拟时间戳
            try:
                base_time = datetime.fromisoformat(last_time.replace("Z", "+00:00"))
            except:
                base_time = datetime.now(timezone.utc)

            pred_time = base_time.timestamp() + (i + 1) * 300  # 5分钟间隔
            pred_timestamp = datetime.fromtimestamp(pred_time, tz=timezone.utc).isoformat()

            predictions.append(PredictionResult(
                timestamp=pred_timestamp,
                open=round(open_price, 4),
                high=round(high, 4),
                low=round(low, 4),
                close=round(pred_close, 4),
                volume=int(last_volume * (1 + gauss(0, 0.1)))
            ))

            last_close = pred_close

        # 模拟置信度指标
        confidence = ConfidenceMetrics(
            mean=0.72,
            std=0.15,
            percentile_25=0.58,
            percentile_75=0.85,
            min=0.45,
            max=0.92
        )

        return predictions, confidence

    def _real_predict(self, input_data: dict) -> tuple:
        """
        真实预测

        Returns:
            (predictions, confidence_metrics)
        """
        self._load_model()

        # TODO: 实现真实预测逻辑
        # from model import KronosPredictor
        # predictor = KronosPredictor(self._model, self._tokenizer)
        # predictions = predictor.predict(...)

        raise NotImplementedError("真实预测模式需要安装 Kronos 模型")

    def _build_gate_decision(
        self,
        confidence: ConfidenceMetrics,
        threshold: float
    ) -> GateDecision:
        """构建 Gate 决策"""
        violations = []
        checks_passed = []

        # 检查 1: 置信度
        if confidence.mean < threshold:
            violations.append(Violation(
                rule_id="LOW_CONFIDENCE",
                severity=Severity.WARNING,
                message=f"平均置信度 {confidence.mean:.2%} 低于阈值 {threshold:.2%}",
                actual_value=confidence.mean,
                threshold=threshold
            ))
        else:
            checks_passed.append("confidence_threshold")

        # 检查 2: 置信度方差
        if confidence.std > 0.25:
            violations.append(Violation(
                rule_id="HIGH_VARIANCE",
                severity=Severity.INFO,
                message=f"置信度方差 {confidence.std:.2%} 较大，预测不稳定",
                actual_value=confidence.std,
                threshold=0.25
            ))
        else:
            checks_passed.append("confidence_stable")

        # 检查 3: 最小置信度
        if confidence.min < 0.3:
            violations.append(Violation(
                rule_id="MIN_CONFIDENCE_TOO_LOW",
                severity=Severity.WARNING,
                message=f"最低置信度 {confidence.min:.2%} 过低",
                actual_value=confidence.min,
                threshold=0.3
            ))
        else:
            checks_passed.append("min_confidence_ok")

        # 计算裁决
        critical_count = sum(1 for v in violations if v.severity == Severity.CRITICAL)
        if critical_count > 0:
            verdict = GateVerdict.DENY
        elif len(violations) > 0:
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
        """
        执行预测

        Args:
            input_data: 输入数据
            trace_context: 追踪上下文

        Returns:
            QuantSkillOutput
        """
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
        symbol = input_data.get("symbol")
        ohlcv_data = input_data.get("ohlcv_data", [])
        lookback = input_data.get("lookback", 400)
        pred_len = input_data.get("pred_len", 120)
        confidence_threshold = input_data.get("confidence_threshold", 0.5)
        model_version = input_data.get("model_version", "kronos-small")

        # 3. 检查上下文溢出
        context_error = self._check_context_overflow(len(ohlcv_data), lookback)
        if context_error:
            return self.create_failure_output(
                error_code="CONTEXT_OVERFLOW",
                error_message=context_error,
                retryable=False,
                metrics=SkillMetrics(latency_ms=int((time.time() - start_time) * 1000)),
                trace_context=trace_context,
                gate_decision=GateDecision(
                    verdict=GateVerdict.DENY,
                    checks_passed=[],
                    violations=[Violation(
                        rule_id="CONTEXT_OVERFLOW",
                        severity=Severity.CRITICAL,
                        message=context_error
                    )]
                )
            )

        # 4. 执行预测
        try:
            if self.mock_mode:
                predictions, confidence = self._mock_predict(input_data)
            else:
                predictions, confidence = self._real_predict(input_data)

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return self.create_failure_output(
                error_code="PREDICTION_ERROR",
                error_message=str(e),
                retryable=True,
                metrics=SkillMetrics(latency_ms=latency_ms),
                trace_context=trace_context
            )

        latency_ms = int((time.time() - start_time) * 1000)

        # 5. 构建输出数据
        input_hash = self._compute_input_hash(ohlcv_data)

        output_data = KronosPredictData(
            predictions=predictions,
            confidence_metrics=confidence,
            model_info=ModelInfo(
                version=model_version,
                commit_sha="mock" if self.mock_mode else "abc123",
                tokenizer_version="v1",
                params_count=self.MODEL_VERSIONS.get(model_version, {}).get("params", "unknown")
            ),
            input_hash=input_hash
        )

        # 6. 构建 Gate 决策
        gate_decision = self._build_gate_decision(confidence, confidence_threshold)

        # 7. 构建成功输出
        return self.create_success_output(
            data=output_data.to_dict(),
            provenance=Provenance(
                source="kronos-model" if not self.mock_mode else "mock",
                model_version=model_version,
                input_hash=input_hash
            ),
            gate_decision=gate_decision,
            metrics=SkillMetrics(
                latency_ms=latency_ms,
                rows_processed=len(ohlcv_data),
                tokens_used=pred_len
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

def predict_kline(
    symbol: str,
    ohlcv_data: List[Dict],
    pred_len: int = 120,
    lookback: int = 400,
    confidence_threshold: float = 0.5,
    mock_mode: bool = True
) -> dict:
    """
    K线预测便捷函数

    Args:
        symbol: 标的代码
        ohlcv_data: 历史 OHLCV 数据
        pred_len: 预测长度
        lookback: 回看长度
        confidence_threshold: 置信度阈值
        mock_mode: 是否使用模拟模式

    Returns:
        预测结果
    """
    skill = KronosPredictSkill(mock_mode=mock_mode)

    input_data = {
        "symbol": symbol,
        "ohlcv_data": ohlcv_data,
        "pred_len": pred_len,
        "lookback": lookback,
        "confidence_threshold": confidence_threshold
    }

    return skill.run(input_data)


# ============================================
# CLI 入口
# ============================================

def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Kronos K线预测")
    parser.add_argument("--symbol", required=True, help="标的代码")
    parser.add_argument("--pred-len", type=int, default=120, help="预测长度")
    parser.add_argument("--mock", action="store_true", help="使用模拟模式")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    # 生成模拟输入数据
    mock_data = [
        {
            "timestamp": f"2024-01-{i+1:02d}T09:30:00Z",
            "open": 100 + i * 0.5,
            "high": 101 + i * 0.5,
            "low": 99 + i * 0.5,
            "close": 100.5 + i * 0.5,
            "volume": 1000000
        }
        for i in range(400)
    ]

    # 执行预测
    result = predict_kline(
        symbol=args.symbol,
        ohlcv_data=mock_data,
        pred_len=args.pred_len,
        mock_mode=args.mock
    )

    # 输出
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"结果已保存到: {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
