"""
P0-01: openbb-fetch Skill
从 OpenBB 获取金融数据

版本: 1.0.0
优先级: P0
层级: data
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Any, Optional
import json
import hashlib
import time


# ============================================
# 数据模型
# ============================================

class DataType(str, Enum):
    """数据类型枚举"""
    EQUITY_PRICE_HISTORICAL = "equity.price.historical"
    EQUITY_FUNDAMENTAL = "equity.fundamental"
    ECONOMY_INDICATORS = "economy.indicators"
    CRYPTO_PRICE = "crypto.price"


class Provider(str, Enum):
    """数据提供商枚举"""
    YAHOO = "yahoo"
    ALPHA_VANTAGE = "alpha_vantage"
    FMP = "fmp"
    POLYGON = "polygon"


class FetchStatus(str, Enum):
    """获取状态枚举"""
    COMPLETED = "completed"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"
    PARTIAL = "partial"


@dataclass
class OpenBBFetchInput:
    """openbb-fetch 输入合同"""
    data_type: DataType
    symbols: list[str]
    provider: Provider = Provider.YAHOO
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    # 控制参数
    max_rows: int = 50000
    timeout_ms: int = 30000
    rate_limit: str = "10/min"
    retry_count: int = 3

    def validate(self) -> list[str]:
        """验证输入参数"""
        errors = []

        if not self.symbols:
            errors.append("symbols 不能为空")

        if len(self.symbols) > 100:
            errors.append("symbols 数量不能超过 100")

        if self.max_rows > 100000:
            errors.append("max_rows 不能超过 100000")

        if self.start_date and self.end_date and self.start_date > self.end_date:
            errors.append("start_date 不能晚于 end_date")

        return errors

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "data_type": self.data_type.value,
            "symbols": self.symbols,
            "provider": self.provider.value,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "controls": {
                "max_rows": self.max_rows,
                "timeout_ms": self.timeout_ms,
                "rate_limit": self.rate_limit,
                "retry_count": self.retry_count
            }
        }


@dataclass
class Provenance:
    """数据来源信息"""
    provider: str
    fetched_at: datetime
    source_url: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "provider": self.provider,
            "fetched_at": self.fetched_at.isoformat(),
            "source_url": self.source_url
        }


@dataclass
class Metrics:
    """执行指标"""
    rows_fetched: int
    latency_ms: int

    def to_dict(self) -> dict:
        return {
            "rows_fetched": self.rows_fetched,
            "latency_ms": self.latency_ms
        }


@dataclass
class OpenBBFetchOutput:
    """openbb-fetch 输出合同"""
    status: FetchStatus
    data: list[dict[str, Any]]
    provenance: Provenance
    evidence_ref: str
    metrics: Metrics

    # 错误信息
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        result = {
            "status": self.status.value,
            "data": self.data,
            "provenance": self.provenance.to_dict(),
            "evidence_ref": self.evidence_ref,
            "metrics": self.metrics.to_dict()
        }

        if self.error_code:
            result["error_code"] = self.error_code
        if self.error_message:
            result["error_message"] = self.error_message

        return result


# ============================================
# Skill 实现
# ============================================

class OpenBBFetchSkill:
    """openbb-fetch Skill 实现"""

    SKILL_ID = "openbb-fetch"
    VERSION = "1.0.0"

    def __init__(self, config: Optional[dict] = None):
        """初始化 Skill"""
        self.config = config or {}
        self._client = None

    def _get_client(self):
        """获取 OpenBB 客户端 (延迟加载)"""
        if self._client is None:
            try:
                from openbb import obb
                self._client = obb
            except ImportError:
                raise ImportError(
                    "OpenBB 未安装。请运行: pip install openbb\n"
                    "注意: OpenBB 使用 AGPLv3 许可证，建议作为独立服务部署。"
                )
        return self._client

    def _generate_evidence_ref(self, input_data: OpenBBFetchInput, output_data: list) -> str:
        """生成证据引用"""
        content = json.dumps({
            "skill_id": self.SKILL_ID,
            "input": input_data.to_dict(),
            "data_hash": hashlib.sha256(
                json.dumps(output_data, sort_keys=True).encode()
            ).hexdigest()[:16],
            "timestamp": datetime.utcnow().isoformat()
        }, sort_keys=True)

        hash_value = hashlib.sha256(content.encode()).hexdigest()[:32]
        return f"evidence://openbb/{hash_value}"

    def execute(self, input_data: OpenBBFetchInput) -> OpenBBFetchOutput:
        """执行数据获取"""
        start_time = time.time()

        # 验证输入
        errors = input_data.validate()
        if errors:
            return OpenBBFetchOutput(
                status=FetchStatus.FAILED,
                data=[],
                provenance=Provenance(
                    provider=input_data.provider.value,
                    fetched_at=datetime.utcnow()
                ),
                evidence_ref="",
                metrics=Metrics(rows_fetched=0, latency_ms=0),
                error_code="VALIDATION_ERROR",
                error_message="; ".join(errors)
            )

        try:
            obb = self._get_client()

            # 根据数据类型获取数据
            data = []
            for symbol in input_data.symbols:
                if input_data.data_type == DataType.EQUITY_PRICE_HISTORICAL:
                    result = obb.equity.price.historical(
                        symbol,
                        provider=input_data.provider.value,
                        start_date=input_data.start_date,
                        end_date=input_data.end_date
                    )
                    df = result.to_dataframe()
                    records = df.reset_index().to_dict('records')
                    for record in records:
                        record['symbol'] = symbol
                    data.extend(records)

            # 限制数据量
            if len(data) > input_data.max_rows:
                data = data[:input_data.max_rows]

            latency_ms = int((time.time() - start_time) * 1000)

            # 生成证据引用
            evidence_ref = self._generate_evidence_ref(input_data, data)

            return OpenBBFetchOutput(
                status=FetchStatus.COMPLETED,
                data=data,
                provenance=Provenance(
                    provider=input_data.provider.value,
                    fetched_at=datetime.utcnow(),
                    source_url=f"https://openbb.co/{input_data.data_type.value}"
                ),
                evidence_ref=evidence_ref,
                metrics=Metrics(rows_fetched=len(data), latency_ms=latency_ms)
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)

            # 判断错误类型
            error_code = "OPENBB_UNKNOWN_ERROR"
            if "rate limit" in str(e).lower():
                error_code = "OPENBB_RATE_LIMITED"
                status = FetchStatus.RATE_LIMITED
            elif "provider" in str(e).lower():
                error_code = "OPENBB_PROVIDER_UNAVAILABLE"
                status = FetchStatus.FAILED
            elif "symbol" in str(e).lower():
                error_code = "OPENBB_INVALID_SYMBOL"
                status = FetchStatus.FAILED
            else:
                status = FetchStatus.FAILED

            return OpenBBFetchOutput(
                status=status,
                data=[],
                provenance=Provenance(
                    provider=input_data.provider.value,
                    fetched_at=datetime.utcnow()
                ),
                evidence_ref="",
                metrics=Metrics(rows_fetched=0, latency_ms=latency_ms),
                error_code=error_code,
                error_message=str(e)
            )

    def run(self, input_dict: dict) -> dict:
        """标准运行接口"""
        # 解析输入
        input_data = OpenBBFetchInput(
            data_type=DataType(input_dict.get("data_type")),
            symbols=input_dict.get("symbols", []),
            provider=Provider(input_dict.get("provider", "yahoo")),
            start_date=input_dict.get("start_date"),
            end_date=input_dict.get("end_date"),
            max_rows=input_dict.get("max_rows", 50000),
            timeout_ms=input_dict.get("timeout_ms", 30000)
        )

        # 执行
        output = self.execute(input_data)

        return output.to_dict()


# ============================================
# 便捷函数
# ============================================

def fetch_market_data(
    symbols: list[str],
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    provider: str = "yahoo"
) -> dict:
    """
    获取市场数据的便捷函数

    Args:
        symbols: 标的代码列表
        start_date: 开始日期
        end_date: 结束日期
        provider: 数据提供商

    Returns:
        输出结果字典
    """
    skill = OpenBBFetchSkill()

    input_data = OpenBBFetchInput(
        data_type=DataType.EQUITY_PRICE_HISTORICAL,
        symbols=symbols,
        provider=Provider(provider),
        start_date=start_date,
        end_date=end_date
    )

    return skill.execute(input_data).to_dict()


# ============================================
# 示例用法
# ============================================

if __name__ == "__main__":
    # 示例: 获取苹果股票历史数据
    result = fetch_market_data(
        symbols=["AAPL"],
        start_date=date(2025, 1, 1),
        end_date=date(2025, 2, 1),
        provider="yahoo"
    )

    print(f"状态: {result['status']}")
    print(f"获取行数: {result['metrics']['rows_fetched']}")
    print(f"延迟: {result['metrics']['latency_ms']}ms")
    print(f"证据引用: {result['evidence_ref']}")

    if result['data']:
        print(f"\n前5条数据:")
        for row in result['data'][:5]:
            print(f"  {row}")
