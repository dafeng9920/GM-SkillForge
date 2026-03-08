"""
API Envelope Helpers - Wave11-A

Inner 域统一响应信封:
- 成功: { data, _meta }
- 失败: { error_code, message, __meta }

_meta 最小字段:
- trace_id: 可追踪 ID
- signals: 信号列表
- recoverable: 可恢复性
- advisory_only: 仅建议层标记
"""
import uuid
from typing import Any, Dict, List, Optional


def ok(data: Any, meta: Optional[Dict] = None) -> Dict:
    """
    成功响应信封

    Args:
        data: 响应数据
        meta: 额外的 meta 字段

    Returns:
        {"data": ..., "_meta": {...}}
    """
    default_meta = {
        "trace_id": str(uuid.uuid4()),
        "signals": [],
        "recoverable": True,
        "advisory_only": False,
    }
    if meta:
        default_meta.update(meta)
    return {"data": data, "_meta": default_meta}


def err(
    code: str,
    message: str,
    meta: Optional[Dict] = None,
    signals: Optional[List[str]] = None,
    recoverable: bool = True,
) -> Dict:
    """
    失败响应信封

    Args:
        code: 错误码
        message: 错误信息
        meta: 额外的 meta 字段
        signals: 信号列表
        recoverable: 是否可恢复

    Returns:
        {"error_code": ..., "message": ..., "_meta": {...}}
    """
    default_meta = {
        "trace_id": str(uuid.uuid4()),
        "signals": signals or [],
        "recoverable": recoverable,
        "advisory_only": False,
    }
    if meta:
        default_meta.update(meta)
    return {"error_code": code, "message": message, "_meta": default_meta}
