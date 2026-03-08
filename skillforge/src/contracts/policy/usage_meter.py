"""
Usage Meter - 用量计费入账模块

在任务入队/接受时进行用量记账（非完成时）。

Usage:
    from contracts.policy.usage_meter import UsageMeter, record_usage, get_usage

    # 入队时记账
    meter = UsageMeter()
    meter.record(account_id="ACC-123", action="AUDIT_L3", units=1, job_id="JOB-456")

    # 读取用量（用于 quota 判断）
    usage = meter.get_usage(account_id="ACC-123", action="AUDIT_L3", period="month")
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
import threading


# 默认 usage 日志路径
DEFAULT_USAGE_LOG_PATH = Path(__file__).parent.parent.parent.parent.parent / "logs" / "usage.jsonl"


@dataclass
class UsageRecord:
    """用量记录数据结构。"""
    account_id: str
    action: str
    units: int
    job_id: str
    ts: str  # ISO 8601 timestamp

    def to_json(self) -> str:
        """转换为 JSON 行。"""
        return json.dumps(asdict(self), ensure_ascii=False)


@dataclass
class UsageSummary:
    """用量汇总。"""
    account_id: str
    action: str
    period: str
    total_units: int
    record_count: int
    first_ts: Optional[str] = None
    last_ts: Optional[str] = None


class UsageMeter:
    """
    用量计费器。

    提供入队时记账和读取功能。
    - record(): 入队时调用，追加写入 usage.jsonl
    - get_usage(): 读取指定账户的用量（用于 quota 判断）
    """

    def __init__(self, log_path: Optional[Path] = None):
        """
        初始化用量计费器。

        Args:
            log_path: usage.jsonl 路径，默认为 logs/usage.jsonl
        """
        self.log_path = log_path or DEFAULT_USAGE_LOG_PATH
        self._lock = threading.Lock()

    def record(
        self,
        account_id: str,
        action: str,
        units: int,
        job_id: str,
        ts: Optional[str] = None,
    ) -> UsageRecord:
        """
        记录用量（入队时调用）。

        这是一个 append-only 操作，将用量记录追加到 usage.jsonl。

        Args:
            account_id: 账户 ID
            action: 动作类型 (如 AUDIT_L3, AUDIT_L4, AUDIT_L5)
            units: 消耗单位数（通常为 1）
            job_id: 任务 ID
            ts: 时间戳（可选，默认当前时间）

        Returns:
            UsageRecord: 已记录的用量记录
        """
        if ts is None:
            ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        record = UsageRecord(
            account_id=account_id,
            action=action,
            units=units,
            job_id=job_id,
            ts=ts,
        )

        # 确保目录存在
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # 追加写入（线程锁保证进程内原子性）
        with self._lock:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(record.to_json() + "\n")
                f.flush()

        return record

    def get_usage(
        self,
        account_id: str,
        action: Optional[str] = None,
        period: str = "month",
    ) -> UsageSummary:
        """
        读取账户用量（用于 quota 判断）。

        Args:
            account_id: 账户 ID
            action: 动作类型过滤（可选，None 表示所有动作）
            period: 时间周期 ("day", "week", "month", "all")

        Returns:
            UsageSummary: 用量汇总
        """
        now = datetime.now(timezone.utc)

        # 计算时间范围
        if period == "day":
            start_time = now - timedelta(days=1)
        elif period == "week":
            start_time = now - timedelta(weeks=1)
        elif period == "month":
            start_time = now - timedelta(days=30)
        else:  # all
            start_time = datetime.min.replace(tzinfo=timezone.utc)

        total_units = 0
        record_count = 0
        first_ts = None
        last_ts = None

        if not self.log_path.exists():
            return UsageSummary(
                account_id=account_id,
                action=action or "ALL",
                period=period,
                total_units=0,
                record_count=0,
            )

        with self._lock:
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # 过滤账户
                    if data.get("account_id") != account_id:
                        continue

                    # 过滤动作
                    if action and data.get("action") != action:
                        continue

                    # 过滤时间
                    ts_str = data.get("ts", "")
                    try:
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        if ts < start_time:
                            continue
                    except ValueError:
                        continue

                    # 汇总
                    total_units += data.get("units", 0)
                    record_count += 1

                    if first_ts is None:
                        first_ts = ts_str
                    last_ts = ts_str

        return UsageSummary(
            account_id=account_id,
            action=action or "ALL",
            period=period,
            total_units=total_units,
            record_count=record_count,
            first_ts=first_ts,
            last_ts=last_ts,
        )

    def get_all_usage_for_account(
        self,
        account_id: str,
        period: str = "month",
    ) -> dict[str, UsageSummary]:
        """
        获取账户所有动作的用量汇总。

        Args:
            account_id: 账户 ID
            period: 时间周期

        Returns:
            dict[action, UsageSummary]: 按动作分组的用量汇总
        """
        # 先获取所有记录来确定有哪些动作
        if not self.log_path.exists():
            return {}

        actions = set()
        now = datetime.now(timezone.utc)

        if period == "day":
            start_time = now - timedelta(days=1)
        elif period == "week":
            start_time = now - timedelta(weeks=1)
        elif period == "month":
            start_time = now - timedelta(days=30)
        else:
            start_time = datetime.min.replace(tzinfo=timezone.utc)

        with self._lock:
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("account_id") == account_id:
                            ts_str = data.get("ts", "")
                            try:
                                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                                if ts >= start_time:
                                    actions.add(data.get("action"))
                            except ValueError:
                                continue
                    except json.JSONDecodeError:
                        continue

        # 按动作获取汇总
        result = {}
        for action in actions:
            result[action] = self.get_usage(account_id, action, period)

        return result


# 模块级便捷函数
_meter_instance: Optional[UsageMeter] = None


def get_meter() -> UsageMeter:
    """获取全局 UsageMeter 实例。"""
    global _meter_instance
    if _meter_instance is None:
        _meter_instance = UsageMeter()
    return _meter_instance


def record_usage(
    account_id: str,
    action: str,
    units: int,
    job_id: str,
    ts: Optional[str] = None,
) -> UsageRecord:
    """
    便捷函数：记录用量。

    使用全局 UsageMeter 实例。
    """
    return get_meter().record(account_id, action, units, job_id, ts)


def get_usage(
    account_id: str,
    action: Optional[str] = None,
    period: str = "month",
) -> UsageSummary:
    """
    便捷函数：获取用量。

    使用全局 UsageMeter 实例。
    """
    return get_meter().get_usage(account_id, action, period)


# 用于集成到 middleware 的函数
def check_and_record_quota_usage(
    account_id: str,
    action: str,
    quota_limit: int,
    job_id: str,
    period: str = "month",
) -> tuple[bool, UsageSummary]:
    """
    检查配额并记录使用量。

    这是一个原子操作：
    1. 先读取当前用量
    2. 检查是否超过配额
    3. 如果未超过，记录新用量

    Args:
        account_id: 账户 ID
        action: 动作类型
        quota_limit: 配额限制
        job_id: 任务 ID
        period: 时间周期

    Returns:
        tuple[bool, UsageSummary]: (是否允许, 当前用量汇总)
    """
    meter = get_meter()

    # 读取当前用量
    current_usage = meter.get_usage(account_id, action, period)

    # 检查配额
    if current_usage.total_units >= quota_limit:
        return False, current_usage

    # 记录新用量
    meter.record(account_id, action, 1, job_id)

    # 返回更新后的用量
    updated_usage = meter.get_usage(account_id, action, period)
    return True, updated_usage
