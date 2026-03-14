"""
审计日志记录器
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import hashlib
import hmac


class EventType(Enum):
    """事件类型"""
    ORDER_SUBMIT = "order_submit"
    ORDER_FILL = "order_fill"
    ORDER_CANCEL = "order_cancel"
    ORDER_REJECT = "order_reject"
    ORDER_MODIFY = "order_modify"
    POSITION_CHANGE = "position_change"
    RISK_LIMIT_HIT = "risk_limit_hit"
    COMPLIANCE_ALERT = "compliance_alert"
    SYSTEM_CONFIG = "system_config"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_ACTION = "user_action"
    SYSTEM_ERROR = "system_error"
    DATA_ANOMALY = "data_anomaly"


@dataclass
class AuditEntry:
    """审计日志条目"""
    id: str
    event_type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    signature: Optional[str] = None
    checksum: Optional[str] = None

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "metadata": self.metadata,
            "signature": self.signature,
            "checksum": self.checksum,
        }

    def to_json(self) -> str:
        """转换为JSON"""
        return json.dumps(self.to_dict())


class AuditLogger:
    """
    审计日志记录器

    负责记录所有交易操作、系统事件，确保数据完整性和不可篡改
    """

    def __init__(self, secret_key: Optional[str] = None):
        self._entries: List[AuditEntry] = []
        self._secret_key = secret_key or "default_secret_key_change_me"
        self._storage_backend = None  # 可以是文件、数据库、MinIO等

    async def log(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEntry:
        """
        记录审计日志

        Args:
            event_type: 事件类型
            data: 事件数据
            metadata: 元数据

        Returns:
            审计日志条目
        """
        # 生成唯一ID
        audit_id = await self._generate_audit_id(event_type)

        # 创建条目
        entry = AuditEntry(
            id=audit_id,
            event_type=event_type,
            timestamp=datetime.now(),
            data=data,
            metadata=metadata or {},
        )

        # 计算校验和
        entry.checksum = await self._calculate_checksum(entry)

        # 数字签名
        entry.signature = await self._sign_entry(entry)

        # 存储条目
        await self._store_entry(entry)

        self._entries.append(entry)

        return entry

    async def _generate_audit_id(self, event_type: EventType) -> str:
        """生成审计ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sequence = len(self._entries) + 1
        return f"AUDIT_{timestamp}_{sequence:03d}"

    async def _calculate_checksum(self, entry: AuditEntry) -> str:
        """计算校验和"""
        # 创建不包含签名的数据
        data_for_hash = {
            "id": entry.id,
            "event_type": entry.event_type.value,
            "timestamp": entry.timestamp.isoformat(),
            "data": entry.data,
            "metadata": entry.metadata,
        }

        # 序列化并计算SHA256
        json_str = json.dumps(data_for_hash, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    async def _sign_entry(self, entry: AuditEntry) -> str:
        """对条目进行数字签名"""
        # 使用HMAC-SHA256进行签名
        message = entry.checksum.encode() if entry.checksum else b""
        signature = hmac.new(
            self._secret_key.encode(),
            message,
            hashlib.sha256,
        ).hexdigest()

        return signature

    async def verify_entry(self, entry: AuditEntry) -> bool:
        """
        验证条目完整性

        Returns:
            True if valid
        """
        # 验证校验和
        expected_checksum = await self._calculate_checksum(entry)
        if entry.checksum != expected_checksum:
            return False

        # 验证签名
        expected_signature = await self._sign_entry(entry)
        if entry.signature != expected_signature:
            return False

        return True

    async def _store_entry(self, entry: AuditEntry):
        """存储条目"""
        # 这里可以实现不同的存储后端
        # 例如：文件、数据库、MinIO等

        # 简化版：存储到内存
        pass

    async def query(
        self,
        event_type: Optional[EventType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[AuditEntry]:
        """
        查询审计日志

        Args:
            event_type: 事件类型过滤
            start_time: 开始时间
            end_time: 结束时间
            filters: 其他过滤条件

        Returns:
            审计日志条目列表
        """
        results = self._entries.copy()

        # 按事件类型过滤
        if event_type:
            results = [e for e in results if e.event_type == event_type]

        # 按时间范围过滤
        if start_time:
            results = [e for e in results if e.timestamp >= start_time]

        if end_time:
            results = [e for e in results if e.timestamp <= end_time]

        # 按其他条件过滤
        if filters:
            for key, value in filters.items():
                results = [
                    e for e in results
                    if e.data.get(key) == value or e.metadata.get(key) == value
                ]

        return results

    async def generate_audit_report(
        self,
        start_time: datetime,
        end_time: datetime,
    ) -> Dict:
        """
        生成审计报告

        Args:
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            审计报告
        """
        # 查询时间范围内的日志
        entries = await self.query(
            start_time=start_time,
            end_time=end_time,
        )

        # 统计各类事件
        event_counts = {}
        for entry in entries:
            event_type = entry.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        # 生成报告
        report = {
            "report_id": f"AUDIT_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_events": len(entries),
            "event_counts": event_counts,
            "entries": [e.to_dict() for e in entries],
        }

        return report

    async def export_to_json(
        self,
        filepath: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ):
        """
        导出审计日志到JSON文件

        Args:
            filepath: 文件路径
            start_time: 开始时间
            end_time: 结束时间
        """
        entries = await self.query(
            start_time=start_time,
            end_time=end_time,
        )

        with open(filepath, "w") as f:
            json.dump([e.to_dict() for e in entries], f, indent=2)

    async def verify_chain_integrity(self) -> bool:
        """
        验证整个日志链的完整性

        Returns:
            True if all entries are valid
        """
        for entry in self._entries:
            if not await self.verify_entry(entry):
                return False

        return True

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total_entries = len(self._entries)

        if total_entries == 0:
            return {
                "total_entries": 0,
                "event_types": {},
            }

        event_types = {}
        for entry in self._entries:
            event_type = entry.event_type.value
            event_types[event_type] = event_types.get(event_type, 0) + 1

        return {
            "total_entries": total_entries,
            "event_types": event_types,
            "first_entry_time": self._entries[0].timestamp.isoformat(),
            "last_entry_time": self._entries[-1].timestamp.isoformat(),
        }

    async def log_order_submit(
        self,
        order_id: str,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        user_id: str,
        strategy_id: str,
        metadata: Optional[Dict] = None,
    ) -> AuditEntry:
        """记录订单提交（便捷方法）"""
        return await self.log(
            EventType.ORDER_SUBMIT,
            {
                "order_id": order_id,
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "price": price,
                "user_id": user_id,
                "strategy_id": strategy_id,
            },
            metadata,
        )

    async def log_order_fill(
        self,
        order_id: str,
        fill_quantity: float,
        fill_price: float,
        venue: str,
        metadata: Optional[Dict] = None,
    ) -> AuditEntry:
        """记录订单成交（便捷方法）"""
        return await self.log(
            EventType.ORDER_FILL,
            {
                "order_id": order_id,
                "fill_quantity": fill_quantity,
                "fill_price": fill_price,
                "venue": venue,
            },
            metadata,
        )

    async def log_compliance_alert(
        self,
        alert_type: str,
        message: str,
        severity: str,
        metadata: Optional[Dict] = None,
    ) -> AuditEntry:
        """记录合规警报（便捷方法）"""
        return await self.log(
            EventType.COMPLIANCE_ALERT,
            {
                "alert_type": alert_type,
                "message": message,
                "severity": severity,
            },
            metadata,
        )

    async def log_user_action(
        self,
        user_id: str,
        action: str,
        target: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> AuditEntry:
        """记录用户操作（便捷方法）"""
        return await self.log(
            EventType.USER_ACTION,
            {
                "user_id": user_id,
                "action": action,
                "target": target,
            },
            metadata,
        )
