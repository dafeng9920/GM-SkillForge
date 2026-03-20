"""
Connector Contract Types (Legacy Export)

此模块保留用于向后兼容。
新代码应使用 skillforge.src.connector_contract。

Legacy exports for backward compatibility.
"""

from skillforge.src.connector_contract.types import (
    ConnectorRequest,
    ConnectorResult,
    EvidenceReferenceDeclaration,
    ExternalConnectionContract,
    FrozenDependencyDeclaration,
    GENERIC_CONNECTION_CONTRACT,
    PermitRequirementDeclaration,
)

__all__ = [
    "ExternalConnectionContract",
    "ConnectorRequest",
    "ConnectorResult",
    "FrozenDependencyDeclaration",
    "PermitRequirementDeclaration",
    "EvidenceReferenceDeclaration",
    "GENERIC_CONNECTION_CONTRACT",
]
