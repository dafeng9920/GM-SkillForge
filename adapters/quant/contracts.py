"""
Quant Adapter 标准接口契约

职责: 定义 Adapter ↔ Core 之间的数据格式
原则: Adapter 只翻译，不执行

Adapter 输出格式必须匹配 Core execute.py 的输入:
    intent: {action, symbol, quantity, price, ...}
    context: {total_capital, current_equity, job_id, ...}
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from datetime import datetime, timezone


# ============================================
# 核心枚举类型
# ============================================

class SignalAction(str, Enum):
    """交易信号动作"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class SignalSource(str, Enum):
    """信号来源"""
    STRATEGY = "strategy"           # 策略信号
    PREDICTION = "prediction"       # 预测模型
    MANUAL = "manual"              # 手动输入


class AdapterStatus(str, Enum):
    """Adapter 状态"""
    SUCCESS = "success"
    FAILED = "failed"
    REJECTED = "rejected"
    HOLD = "hold"


# ============================================
# Evidence 数据模型 (Core 可理解的格式)
# ============================================

@dataclass
class Evidence:
    """证据数据 - Core 审计链可理解"""
    source: str                      # 数据来源
    timestamp: str                   # ISO 8601 格式
    data_hash: Optional[str] = None  # 数据哈希
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "timestamp": self.timestamp,
            "data_hash": self.data_hash,
            "metadata": self.metadata
        }


# ============================================
# Adapter 输出契约 (匹配 Core 输入)
# ============================================

@dataclass
class TradingIntent:
    """
    交易意图 - Adapter 输出的核心格式

    这是 Core execute.py 的标准输入格式
    """
    # 必填字段
    action: SignalAction              # BUY, SELL, HOLD
    symbol: str                       # 标的代码

    # 可选字段
    quantity: Optional[int] = None    # 数量
    price: Optional[float] = None     # 价格
    confidence: Optional[float] = None  # 置信度 0-1
    reasoning: Optional[str] = None   # 信号理由
    target_price: Optional[float] = None  # 目标价格
    stop_loss: Optional[float] = None    # 止损价格

    # 元数据
    source: Optional[SignalSource] = None
    generated_at: Optional[str] = None

    def to_core_intent(self) -> Dict[str, Any]:
        """
        转换为 Core execute.py 的 intent 格式
        """
        return {
            "action": self.action.value,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "price": self.price,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "target_price": self.target_price,
            "stop_loss": self.stop_loss,
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return self.to_core_intent()


@dataclass
class AdapterContext:
    """
    Adapter 上下文 - 传递给 Core 的上下文信息
    """
    # 策略信息
    strategy_id: Optional[str] = None
    strategy_version: Optional[str] = None

    # 账户信息 (可选，Core 会覆盖)
    total_capital: Optional[float] = None
    current_equity: Optional[float] = None

    # 作业追踪
    job_id: Optional[str] = None
    trace_id: Optional[str] = None

    def to_core_context(self) -> Dict[str, Any]:
        """转换为 Core execute.py 的 context 格式"""
        return {
            "strategy_id": self.strategy_id,
            "strategy_version": self.strategy_version,
            "total_capital": self.total_capital,
            "current_equity": self.current_equity,
            "job_id": self.job_id,
            "trace_id": self.trace_id,
        }


@dataclass
class AdapterOutput:
    """
    Adapter 标准输出

    这是所有 Adapter 必须遵循的输出格式
    """
    # 状态
    status: AdapterStatus

    # 核心输出 (可传递给 Core)
    intent: Optional[TradingIntent] = None
    context: Optional[AdapterContext] = None

    # 证据数据
    evidence: Optional[List[Evidence]] = None

    # 错误信息
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    # 额外元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "status": self.status.value,
        }

        if self.intent:
            result["intent"] = self.intent.to_core_intent()
        if self.context:
            result["context"] = self.context.to_core_context()
        if self.evidence:
            result["evidence"] = [e.to_dict() for e in self.evidence]
        if self.error_code:
            result["error_code"] = self.error_code
        if self.error_message:
            result["error_message"] = self.error_message
        if self.metadata:
            result["metadata"] = self.metadata

        return result


# ============================================
# 数据适配器输出契约 (用于数据源)
# ============================================

@dataclass
class DataFrame:
    """标准数据帧格式"""
    columns: List[str]
    data: List[List[Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "columns": self.columns,
            "data": self.data,
            "metadata": self.metadata
        }


@dataclass
class DataAdapterOutput:
    """
    数据适配器标准输出

    用于 openbb_fetch, kronos 等数据源适配器
    """
    status: AdapterStatus
    data: Optional[DataFrame] = None
    evidence: Optional[Evidence] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "status": self.status.value,
        }

        if self.data:
            result["data"] = self.data.to_dict()
        if self.evidence:
            result["evidence"] = self.evidence.to_dict()
        if self.error_code:
            result["error_code"] = self.error_code
        if self.error_message:
            result["error_message"] = self.error_message
        if self.metadata:
            result["metadata"] = self.metadata

        return result


# ============================================
# 辅助函数
# ============================================

def create_hold_signal(symbol: str, reasoning: str = "No signal") -> AdapterOutput:
    """创建 HOLD 信号的快捷方法"""
    return AdapterOutput(
        status=AdapterStatus.HOLD,
        intent=TradingIntent(
            action=SignalAction.HOLD,
            symbol=symbol,
            reasoning=reasoning,
            generated_at=datetime.now(timezone.utc).isoformat()
        )
    )


def create_buy_signal(
    symbol: str,
    quantity: int,
    confidence: float,
    reasoning: str,
    price: Optional[float] = None,
    target_price: Optional[float] = None,
    stop_loss: Optional[float] = None
) -> AdapterOutput:
    """创建 BUY 信号的快捷方法"""
    return AdapterOutput(
        status=AdapterStatus.SUCCESS,
        intent=TradingIntent(
            action=SignalAction.BUY,
            symbol=symbol,
            quantity=quantity,
            price=price,
            confidence=confidence,
            reasoning=reasoning,
            target_price=target_price,
            stop_loss=stop_loss,
            generated_at=datetime.now(timezone.utc).isoformat()
        )
    )


def create_sell_signal(
    symbol: str,
    quantity: int,
    confidence: float,
    reasoning: str,
    price: Optional[float] = None
) -> AdapterOutput:
    """创建 SELL 信号的快捷方法"""
    return AdapterOutput(
        status=AdapterStatus.SUCCESS,
        intent=TradingIntent(
            action=SignalAction.SELL,
            symbol=symbol,
            quantity=quantity,
            price=price,
            confidence=confidence,
            reasoning=reasoning,
            generated_at=datetime.now(timezone.utc).isoformat()
        )
    )


def create_error(error_code: str, error_message: str) -> AdapterOutput:
    """创建错误输出的快捷方法"""
    return AdapterOutput(
        status=AdapterStatus.FAILED,
        error_code=error_code,
        error_message=error_message
    )
