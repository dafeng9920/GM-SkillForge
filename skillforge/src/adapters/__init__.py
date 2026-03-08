"""
Adapters module - 可替换适配器接口

提供外部依赖的可替换适配器：
- RAG Adapter: 检索增强生成查询
"""
from .rag_adapter import (
    RAGAdapter,
    MockRAGAdapter,
    RAGQueryResult,
    RAGQueryError,
    get_rag_adapter,
    set_rag_adapter,
)

__all__ = [
    "RAGAdapter",
    "MockRAGAdapter",
    "RAGQueryResult",
    "RAGQueryError",
    "get_rag_adapter",
    "set_rag_adapter",
]
