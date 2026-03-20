"""
Connector Contract Module

定义外部连接接口契约。
只定义接口，不实现连接。

Usage:
    from skillforge.src.connector_contract import (
        ExternalConnectionContract,
        ConnectorRequest,
        ConnectorResult,
        FrozenDependencyDeclaration,
        PermitRequirementDeclaration,
        EvidenceReferenceDeclaration,
        GENERIC_CONNECTION_CONTRACT,
    )
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
