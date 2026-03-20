"""
Transporter Definition

在 SkillForge 内核与外部连接器之间搬运数据。
只定义搬运接口，不实现搬运逻辑。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any

from .gateway_interface import EvidenceRef, PermitRef


@dataclass
class TransportRequest:
    """
    搬运请求

    只定义请求结构，不实现搬运逻辑。
    """
    transport_id: str         # 搬运 ID
    source_data: Dict[str, Any]  # 源数据
    target_format: str         # 目标格式
    permit_ref: str            # Permit 引用


@dataclass
class TransportResult:
    """
    搬运结果

    只定义结果结构，不实现结果处理。
    """
    transport_id: str         # 搬运 ID
    transformed_data: Dict[str, Any]  # 转换后的数据
    evidence_refs: list[EvidenceRef]  # Evidence 引用（只搬运，不生成）


@dataclass
class TransformationRule:
    """
    转换规则

    只定义规则结构，不实现转换逻辑。
    """
    source_format: str         # 源格式
    target_format: str         # 目标格式
    transformation: Dict[str, Any]  # 转换逻辑（仅定义）


class TransporterInterface(ABC):
    """
    搬运器接口

    只定义搬运接口，不实现搬运逻辑。
    """

    @abstractmethod
    def transform_payload(self, request: TransportRequest) -> TransportResult:
        """
        转换载荷

        只定义转换接口，不实现转换逻辑。
        """
        pass

    @abstractmethod
    def attach_permit_ref(self, payload: Dict[str, Any], permit_ref: str) -> Dict[str, Any]:
        """
        附加 permit 引用

        只定义附加接口，不实现附加逻辑。
        """
        pass

    @abstractmethod
    def attach_evidence_refs(self, payload: Dict[str, Any], evidence_refs: list[EvidenceRef]) -> Dict[str, Any]:
        """
        附加 Evidence 引用

        只定义附加接口，不实现附加逻辑。
        只引用，不生成新的 Evidence。
        """
        pass

    @abstractmethod
    def extract_evidence_refs(self, source: Any) -> list[EvidenceRef]:
        """
        提取 Evidence 引用

        只定义提取接口，不实现提取逻辑。
        只提取引用，不生成新的 Evidence。
        """
        pass


class Transporter(TransporterInterface):
    """
    搬运器实现（仅骨架）

    当前阶段只提供接口占位，不实现具体逻辑。
    """

    def __init__(self):
        """初始化搬运器（仅骨架）"""
        # 不维护真实状态
        self._transformation_rules: list[TransformationRule] = []

    def transform_payload(self, request: TransportRequest) -> TransportResult:
        """
        转换载荷（仅骨架）

        当前阶段不实现转换逻辑。
        """
        # 不实现真实转换
        raise NotImplementedError("Transporter 转换功能待实现")

    def attach_permit_ref(self, payload: Dict[str, Any], permit_ref: str) -> Dict[str, Any]:
        """
        附加 permit 引用（仅骨架）

        当前阶段不实现附加逻辑。
        """
        # 不实现真实附加
        raise NotImplementedError("Transporter permit 附加功能待实现")

    def attach_evidence_refs(self, payload: Dict[str, Any], evidence_refs: list[EvidenceRef]) -> Dict[str, Any]:
        """
        附加 Evidence 引用（仅骨架）

        当前阶段不实现附加逻辑。
        """
        # 不实现真实附加
        raise NotImplementedError("Transporter evidence 附加功能待实现")

    def extract_evidence_refs(self, source: Any) -> list[EvidenceRef]:
        """
        提取 Evidence 引用（仅骨架）

        当前阶段不实现提取逻辑。
        """
        # 不实现真实提取
        raise NotImplementedError("Transporter evidence 提取功能待实现")
