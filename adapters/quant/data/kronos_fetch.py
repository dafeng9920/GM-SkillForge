"""
Kronos Data Adapter - Kronos预测数据适配器

职责: 从Kronos获取预测结果，翻译为标准格式
原则: 只翻译，不执行

版本: 1.0.0
"""

from __future__ import annotations
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# 导入标准接口契约
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from contracts import (
    DataAdapterOutput,
    AdapterStatus,
    Evidence,
    DataFrame,
    create_error
)


# ============================================
# Kronos 特定数据模型
# ============================================

@dataclass
class KronosPrediction:
    """Kronos预测结果"""
    symbol: str
    timestamp: str
    predicted_price: float
    confidence: float
    model_version: str
    horizon: int  # 预测步长 (天)
    features: Dict[str, float] = None

    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "predicted_price": round(self.predicted_price, 2),
            "confidence": round(self.confidence, 4),
            "model_version": self.model_version,
            "horizon": self.horizon,
            "features": self.features or {}
        }


@dataclass
class KronosFetchRequest:
    """Kronos数据请求"""
    symbols: List[str]
    horizon: int = 5  # 预测未来5天
    model_version: str = "latest"
    include_features: bool = False

    def validate(self) -> List[str]:
        """验证请求"""
        errors = []

        if not self.symbols:
            errors.append("symbols 不能为空")

        if len(self.symbols) > 50:
            errors.append("单次请求symbol数量不能超过50")

        if self.horizon <= 0 or self.horizon > 30:
            errors.append("horizon 必须在 1-30 之间")

        return errors


# ============================================
# Adapter 实现
# ============================================

class KronosFetchAdapter:
    """
    Kronos预测数据适配器

    从Kronos获取预测结果并翻译为标准格式
    """

    ADAPTER_ID = "kronos-fetch"
    VERSION = "1.0.0"

    # Kronos API 端点 (模拟)
    KRONOS_API_ENDPOINT = "https://api.kronos.example/v1/predict"

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._client = None

    def _get_client(self):
        """获取Kronos客户端 (延迟加载)"""
        # 实际实现中，这里会初始化Kronos客户端
        # from kronos import Client
        # self._client = Client(api_key=self.config.get("api_key"))
        return None

    def _fetch_predictions(
        self,
        request: KronosFetchRequest
    ) -> List[KronosPrediction]:
        """
        从Kronos获取预测结果

        实际实现中，这里会调用Kronos API
        这里返回模拟数据
        """
        import random

        predictions = []

        for symbol in request.symbols:
            # 模拟预测数据
            base_price = random.uniform(50, 200)
            predictions.append(KronosPrediction(
                symbol=symbol,
                timestamp=datetime.now(timezone.utc).isoformat(),
                predicted_price=base_price * random.uniform(0.95, 1.10),
                confidence=random.uniform(0.5, 0.9),
                model_version=request.model_version,
                horizon=request.horizon,
                features={"momentum": random.uniform(-0.1, 0.1)} if request.include_features else None
            ))

        return predictions

    def execute(
        self,
        request: KronosFetchRequest,
        context: Optional[Dict] = None
    ) -> DataAdapterOutput:
        """
        执行数据获取

        Args:
            request: Kronos数据请求
            context: 上下文 {job_id, trace_id, ...}

        Returns:
            DataAdapterOutput: 预测数据
        """
        start_time = time.time()
        context = context or {}

        # 1. 输入验证
        errors = request.validate()
        if errors:
            return DataAdapterOutput(
                status=AdapterStatus.FAILED,
                error_code="VALIDATION_ERROR",
                error_message="; ".join(errors),
                evidence=None
            )

        # 2. 获取预测数据
        try:
            predictions = self._fetch_predictions(request)
        except Exception as e:
            return DataAdapterOutput(
                status=AdapterStatus.FAILED,
                error_code="FETCH_FAILED",
                error_message=str(e),
                evidence=None
            )

        # 3. 转换为标准DataFrame格式
        if predictions:
            columns = ["symbol", "timestamp", "predicted_price", "confidence", "model_version", "horizon"]
            data = [
                [
                    p.symbol,
                    p.timestamp,
                    p.predicted_price,
                    p.confidence,
                    p.model_version,
                    p.horizon
                ]
                for p in predictions
            ]

            data_frame = DataFrame(columns=columns, data=data)
        else:
            data_frame = None

        # 4. 生成证据
        evidence_content = {
            "adapter_id": self.ADAPTER_ID,
            "symbols": request.symbols,
            "horizon": request.horizon,
            "prediction_count": len(predictions),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        import hashlib
        import json

        evidence = Evidence(
            source=self.ADAPTER_ID,
            timestamp=datetime.now(timezone.utc).isoformat(),
            data_hash=hashlib.sha256(
                json.dumps(evidence_content, sort_keys=True).encode()
            ).hexdigest()[:32],
            metadata={
                "symbols_count": len(request.symbols),
                "horizon": request.horizon,
                "latency_ms": int((time.time() - start_time) * 1000)
            }
        )

        # 5. 返回结果
        return DataAdapterOutput(
            status=AdapterStatus.SUCCESS,
            data=data_frame,
            evidence=evidence,
            metadata={
                "predictions": [p.to_dict() for p in predictions],
                "request": {
                    "symbols": request.symbols,
                    "horizon": request.horizon,
                    "model_version": request.model_version
                }
            }
        )

    def run(self, input_dict: Dict, context: Optional[Dict] = None) -> Dict:
        """标准运行接口"""
        request = KronosFetchRequest(
            symbols=input_dict.get("symbols", []),
            horizon=input_dict.get("horizon", 5),
            model_version=input_dict.get("model_version", "latest"),
            include_features=input_dict.get("include_features", False)
        )

        output = self.execute(request, context)
        return output.to_dict()


# ============================================
# 便捷函数
# ============================================

def fetch_kronos_predictions(
    symbols: List[str],
    horizon: int = 5
) -> Dict:
    """
    获取Kronos预测的便捷函数

    Example:
        result = fetch_kronos_predictions(
            symbols=["AAPL", "MSFT"],
            horizon=5
        )
    """
    adapter = KronosFetchAdapter()

    return adapter.run({
        "symbols": symbols,
        "horizon": horizon
    })


# ============================================
# CLI 入口
# ============================================

def main():
    """命令行入口"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Kronos预测数据适配器")
    parser.add_argument("--symbols", nargs="+", required=True, help="股票代码列表")
    parser.add_argument("--horizon", type=int, default=5, help="预测步长 (天)")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    result = fetch_kronos_predictions(
        symbols=args.symbols,
        horizon=args.horizon
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"结果已保存到: {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
