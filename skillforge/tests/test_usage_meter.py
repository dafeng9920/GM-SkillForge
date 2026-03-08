"""
Usage Meter 测试

测试计量入账与读取功能。
"""
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from skillforge.src.contracts.policy.usage_meter import (
    UsageMeter,
    UsageRecord,
    UsageSummary,
    record_usage,
    get_usage,
    get_meter,
    check_and_record_quota_usage,
)


class TestUsageRecord:
    """测试 UsageRecord 数据结构。"""

    def test_usage_record_creation(self):
        """测试创建用量记录。"""
        record = UsageRecord(
            account_id="ACC-123",
            action="AUDIT_L3",
            units=1,
            job_id="JOB-456",
            ts="2026-02-20T12:00:00Z",
        )
        assert record.account_id == "ACC-123"
        assert record.action == "AUDIT_L3"
        assert record.units == 1
        assert record.job_id == "JOB-456"

    def test_usage_record_to_json(self):
        """测试转换为 JSON。"""
        record = UsageRecord(
            account_id="ACC-123",
            action="AUDIT_L3",
            units=1,
            job_id="JOB-456",
            ts="2026-02-20T12:00:00Z",
        )
        json_str = record.to_json()
        data = json.loads(json_str)
        assert data["account_id"] == "ACC-123"
        assert data["action"] == "AUDIT_L3"


class TestUsageMeter:
    """测试 UsageMeter 类。"""

    @pytest.fixture
    def temp_log_path(self):
        """创建临时日志文件。"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write("")
            path = Path(f.name)
        yield path
        # 清理
        if path.exists():
            path.unlink()

    @pytest.fixture
    def meter(self, temp_log_path):
        """创建使用临时路径的 UsageMeter。"""
        return UsageMeter(log_path=temp_log_path)

    def test_record_usage(self, meter):
        """测试记录用量。"""
        record = meter.record(
            account_id="ACC-123",
            action="AUDIT_L3",
            units=1,
            job_id="JOB-456",
        )
        assert record.account_id == "ACC-123"
        assert record.action == "AUDIT_L3"
        assert record.units == 1
        # 验证文件写入
        with open(meter.log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["account_id"] == "ACC-123"

    def test_record_usage_with_custom_ts(self, meter):
        """测试使用自定义时间戳记录用量。"""
        custom_ts = "2026-02-20T10:30:00Z"
        record = meter.record(
            account_id="ACC-123",
            action="AUDIT_L4",
            units=2,
            job_id="JOB-789",
            ts=custom_ts,
        )
        assert record.ts == custom_ts

    def test_get_usage_empty(self, meter):
        """测试获取空用量。"""
        usage = meter.get_usage(account_id="ACC-123", action="AUDIT_L3")
        assert usage.total_units == 0
        assert usage.record_count == 0

    def test_get_usage_with_records(self, meter):
        """测试获取用量汇总。"""
        # 记录多条用量
        meter.record("ACC-123", "AUDIT_L3", 1, "JOB-1")
        meter.record("ACC-123", "AUDIT_L3", 1, "JOB-2")
        meter.record("ACC-123", "AUDIT_L4", 1, "JOB-3")
        meter.record("ACC-456", "AUDIT_L3", 1, "JOB-4")

        # 获取 ACC-123 的 AUDIT_L3 用量
        usage = meter.get_usage(account_id="ACC-123", action="AUDIT_L3")
        assert usage.total_units == 2
        assert usage.record_count == 2

        # 获取 ACC-123 的 AUDIT_L4 用量
        usage = meter.get_usage(account_id="ACC-123", action="AUDIT_L4")
        assert usage.total_units == 1
        assert usage.record_count == 1

        # 获取 ACC-456 的用量
        usage = meter.get_usage(account_id="ACC-456", action="AUDIT_L3")
        assert usage.total_units == 1

    def test_get_usage_all_actions(self, meter):
        """测试获取所有动作的用量（action=None）。"""
        meter.record("ACC-123", "AUDIT_L3", 1, "JOB-1")
        meter.record("ACC-123", "AUDIT_L4", 2, "JOB-2")

        usage = meter.get_usage(account_id="ACC-123", action=None)
        assert usage.total_units == 3
        assert usage.record_count == 2

    def test_get_usage_period_filter(self, meter):
        """测试时间周期过滤。"""
        now = datetime.now(timezone.utc)

        # 记录当前用量
        meter.record("ACC-123", "AUDIT_L3", 1, "JOB-1")

        # 手动添加一条旧记录
        old_ts = (now - timedelta(days=35)).isoformat().replace("+00:00", "Z")
        with open(meter.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "account_id": "ACC-123",
                "action": "AUDIT_L3",
                "units": 1,
                "job_id": "JOB-OLD",
                "ts": old_ts,
            }) + "\n")

        # 月度用量（应该只包含新记录）
        usage = meter.get_usage(account_id="ACC-123", action="AUDIT_L3", period="month")
        assert usage.total_units == 1  # 只有新记录

        # 所有用量
        usage = meter.get_usage(account_id="ACC-123", action="AUDIT_L3", period="all")
        assert usage.total_units == 2  # 两条记录

    def test_append_only(self, meter):
        """测试 append-only 特性。"""
        meter.record("ACC-123", "AUDIT_L3", 1, "JOB-1")
        meter.record("ACC-123", "AUDIT_L4", 1, "JOB-2")

        with open(meter.log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        assert len(lines) == 2
        # 验证追加顺序
        data1 = json.loads(lines[0])
        data2 = json.loads(lines[1])
        assert data1["action"] == "AUDIT_L3"
        assert data2["action"] == "AUDIT_L4"

    def test_get_all_usage_for_account(self, meter):
        """测试获取账户所有动作用量。"""
        meter.record("ACC-123", "AUDIT_L3", 1, "JOB-1")
        meter.record("ACC-123", "AUDIT_L4", 2, "JOB-2")
        meter.record("ACC-456", "AUDIT_L3", 1, "JOB-3")

        usages = meter.get_all_usage_for_account(account_id="ACC-123")
        assert "AUDIT_L3" in usages
        assert "AUDIT_L4" in usages
        assert usages["AUDIT_L3"].total_units == 1
        assert usages["AUDIT_L4"].total_units == 2


class TestConvenienceFunctions:
    """测试便捷函数。"""

    @pytest.fixture
    def temp_log_path(self, monkeypatch):
        """创建临时日志文件并 patch 全局实例。"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write("")
            path = Path(f.name)
        yield path
        if path.exists():
            path.unlink()

    def test_record_usage_function(self, temp_log_path, monkeypatch):
        """测试 record_usage 便捷函数。"""
        meter = UsageMeter(log_path=temp_log_path)
        monkeypatch.setattr(
            "skillforge.src.contracts.policy.usage_meter._meter_instance",
            meter
        )

        record = record_usage(
            account_id="ACC-123",
            action="AUDIT_L3",
            units=1,
            job_id="JOB-456",
        )
        assert record.account_id == "ACC-123"

    def test_get_usage_function(self, temp_log_path, monkeypatch):
        """测试 get_usage 便捷函数。"""
        meter = UsageMeter(log_path=temp_log_path)
        monkeypatch.setattr(
            "skillforge.src.contracts.policy.usage_meter._meter_instance",
            meter
        )

        meter.record("ACC-123", "AUDIT_L3", 1, "JOB-1")
        usage = get_usage(account_id="ACC-123", action="AUDIT_L3")
        assert usage.total_units == 1


class TestQuotaIntegration:
    """测试配额集成功能。"""

    @pytest.fixture
    def meter(self):
        """创建使用临时路径的 UsageMeter。"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write("")
            path = Path(f.name)
        meter = UsageMeter(log_path=path)
        yield meter
        if path.exists():
            path.unlink()

    def test_check_and_record_quota_usage_allowed(self, meter, monkeypatch):
        """测试配额检查允许的情况。"""
        monkeypatch.setattr(
            "skillforge.src.contracts.policy.usage_meter._meter_instance",
            meter
        )

        allowed, usage = check_and_record_quota_usage(
            account_id="ACC-123",
            action="AUDIT_L3",
            quota_limit=10,
            job_id="JOB-1",
        )
        assert allowed is True
        assert usage.total_units == 1

    def test_check_and_record_quota_usage_denied(self, meter, monkeypatch):
        """测试配额检查拒绝的情况。"""
        monkeypatch.setattr(
            "skillforge.src.contracts.policy.usage_meter._meter_instance",
            meter
        )

        # 先记录到配额限制
        for i in range(10):
            meter.record("ACC-123", "AUDIT_L3", 1, f"JOB-{i}")

        # 再次尝试，应该被拒绝
        allowed, usage = check_and_record_quota_usage(
            account_id="ACC-123",
            action="AUDIT_L3",
            quota_limit=10,
            job_id="JOB-NEW",
        )
        assert allowed is False
        assert usage.total_units == 10

    def test_enqueue_time_metering(self, meter):
        """测试入队时记账（非完成时）。

        这是核心约束验证：入队/接受时扣减（非完成时）。
        """
        # 模拟入队操作
        account_id = "ACC-123"
        action = "AUDIT_L3"
        job_id = "JOB-ENQUEUE-TEST"

        # 入队时立即记录用量
        record = meter.record(account_id, action, 1, job_id)

        # 验证记录已写入
        usage = meter.get_usage(account_id, action)
        assert usage.total_units >= 1

        # 验证记录包含 job_id，可追溯
        assert record.job_id == job_id
        assert record.account_id == account_id


class TestSchemaCompliance:
    """测试 schema 合规性。"""

    @pytest.fixture
    def meter(self):
        """创建使用临时路径的 UsageMeter。"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write("")
            path = Path(f.name)
        meter = UsageMeter(log_path=path)
        yield meter
        if path.exists():
            path.unlink()

    def test_usage_jsonl_schema(self, meter):
        """测试 usage.jsonl 符合 schema。

        Schema: {"account_id": str, "action": str, "units": int, "job_id": str, "ts": str}
        """
        meter.record("ACC-123", "AUDIT_L3", 1, "JOB-1")

        with open(meter.log_path, "r", encoding="utf-8") as f:
            line = f.readline().strip()

        data = json.loads(line)

        # 验证必需字段
        assert "account_id" in data
        assert "action" in data
        assert "units" in data
        assert "job_id" in data
        assert "ts" in data

        # 验证类型
        assert isinstance(data["account_id"], str)
        assert isinstance(data["action"], str)
        assert isinstance(data["units"], int)
        assert isinstance(data["job_id"], str)
        assert isinstance(data["ts"], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
