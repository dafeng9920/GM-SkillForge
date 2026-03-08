"""
P0-02: data-validator Skill
校验数据质量，防止垃圾进垃圾出

版本: 1.0.0
优先级: P0
层级: data
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import json
import hashlib


# ============================================
# 数据模型
# ============================================

class ValidationStatus(str, Enum):
    """校验状态枚举"""
    VALID = "valid"
    INVALID = "invalid"
    PARTIAL = "partial"


class Severity(str, Enum):
    """问题严重程度"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """校验问题"""
    rule_id: str
    severity: Severity
    message: str
    column: Optional[str] = None
    row_index: Optional[int] = None
    actual_value: Optional[Any] = None
    expected_value: Optional[Any] = None
    count: int = 1

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "message": self.message,
            "column": self.column,
            "row_index": self.row_index,
            "actual_value": self.actual_value,
            "expected_value": self.expected_value,
            "count": self.count
        }


@dataclass
class ValidationRule:
    """校验规则"""
    rule_id: str
    name: str
    description: str
    enabled: bool = True
    threshold: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "threshold": self.threshold
        }


@dataclass
class DataValidatorInput:
    """data-validator 输入合同"""
    data: list[dict[str, Any]]
    schema: Optional[dict] = None
    rules: Optional[list[ValidationRule]] = None
    strict_mode: bool = False

    # 控制参数
    max_rows: int = 100000

    def validate(self) -> list[str]:
        """验证输入参数"""
        errors = []

        if not self.data:
            errors.append("data 不能为空")

        if len(self.data) > self.max_rows:
            errors.append(f"data 行数不能超过 {self.max_rows}")

        return errors

    def to_dict(self) -> dict:
        return {
            "data_count": len(self.data),
            "schema": self.schema,
            "rules": [r.to_dict() for r in (self.rules or [])],
            "strict_mode": self.strict_mode
        }


@dataclass
class ValidationResult:
    """校验结果"""
    total_rows: int
    valid_rows: int
    invalid_rows: int
    issues: list[ValidationIssue]

    @property
    def valid_ratio(self) -> float:
        if self.total_rows == 0:
            return 0.0
        return self.valid_rows / self.total_rows

    def to_dict(self) -> dict:
        return {
            "total_rows": self.total_rows,
            "valid_rows": self.valid_rows,
            "invalid_rows": self.invalid_rows,
            "valid_ratio": round(self.valid_ratio, 4),
            "issues": [issue.to_dict() for issue in self.issues],
            "issues_by_severity": {
                "critical": len([i for i in self.issues if i.severity == Severity.CRITICAL]),
                "warning": len([i for i in self.issues if i.severity == Severity.WARNING]),
                "info": len([i for i in self.issues if i.severity == Severity.INFO])
            }
        }


@dataclass
class DataValidatorOutput:
    """data-validator 输出合同"""
    status: ValidationStatus
    validation_result: ValidationResult
    cleaned_data: Optional[list[dict[str, Any]]] = None
    evidence_ref: str = ""

    # 错误信息
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        result = {
            "status": self.status.value,
            "validation_result": self.validation_result.to_dict(),
            "evidence_ref": self.evidence_ref
        }

        if self.cleaned_data is not None:
            result["cleaned_data"] = self.cleaned_data

        if self.error_code:
            result["error_code"] = self.error_code
        if self.error_message:
            result["error_message"] = self.error_message

        return result


# ============================================
# 默认校验规则
# ============================================

DEFAULT_RULES = [
    ValidationRule(
        rule_id="MISSING_VALUE_CHECK",
        name="缺失值检查",
        description="检查缺失值比例是否超过阈值",
        threshold=0.1  # 10%
    ),
    ValidationRule(
        rule_id="OUTLIER_CHECK",
        name="异常值检查",
        description="检查是否存在 3σ 外的异常值",
        threshold=0.05  # 5%
    ),
    ValidationRule(
        rule_id="CONTINUITY_CHECK",
        name="连续性检查",
        description="检查时间序列是否连续",
        threshold=0.01  # 1% 缺失
    ),
    ValidationRule(
        rule_id="SCHEMA_CHECK",
        name="Schema 检查",
        description="检查字段类型和格式",
        threshold=1.0  # 100% 必须符合
    ),
    ValidationRule(
        rule_id="DUPLICATE_CHECK",
        name="重复检查",
        description="检查是否存在重复行",
        threshold=0.01  # 1%
    ),
    ValidationRule(
        rule_id="NEGATIVE_VALUE_CHECK",
        name="负值检查",
        description="检查价格/成交量是否有负值",
        threshold=0.0  # 不允许
    )
]


# ============================================
# Skill 实现
# ============================================

class DataValidatorSkill:
    """data-validator Skill 实现"""

    SKILL_ID = "data-validator"
    VERSION = "1.0.0"

    # OHLCV 标准字段
    OHLCV_FIELDS = {
        "open": {"type": "number", "min": 0},
        "high": {"type": "number", "min": 0},
        "low": {"type": "number", "min": 0},
        "close": {"type": "number", "min": 0},
        "volume": {"type": "number", "min": 0},
        "timestamp": {"type": "datetime"}
    }

    def __init__(self, config: Optional[dict] = None):
        """初始化 Skill"""
        self.config = config or {}

    def _generate_evidence_ref(self, input_data: DataValidatorInput,
                                result: ValidationResult) -> str:
        """生成证据引用"""
        content = json.dumps({
            "skill_id": self.SKILL_ID,
            "input": input_data.to_dict(),
            "result_summary": {
                "total_rows": result.total_rows,
                "valid_rows": result.valid_rows,
                "issues_count": len(result.issues)
            },
            "timestamp": datetime.utcnow().isoformat()
        }, sort_keys=True)

        hash_value = hashlib.sha256(content.encode()).hexdigest()[:32]
        return f"evidence://validator/{hash_value}"

    def _check_missing_values(self, data: list[dict],
                              rule: ValidationRule) -> list[ValidationIssue]:
        """检查缺失值"""
        issues = []
        if not data:
            return issues

        columns = list(data[0].keys())

        for col in columns:
            missing_count = sum(1 for row in data if col not in row or row[col] is None)
            missing_ratio = missing_count / len(data)

            if missing_ratio > rule.threshold:
                issues.append(ValidationIssue(
                    rule_id="MISSING_VALUE_CHECK",
                    severity=Severity.WARNING if missing_ratio < 0.3 else Severity.CRITICAL,
                    message=f"列 '{col}' 缺失值比例为 {missing_ratio:.2%}，超过阈值 {rule.threshold:.2%}",
                    column=col,
                    actual_value=missing_ratio,
                    expected_value=rule.threshold,
                    count=missing_count
                ))

        return issues

    def _check_outliers(self, data: list[dict],
                        rule: ValidationRule) -> list[ValidationIssue]:
        """检查异常值 (3σ)"""
        issues = []

        # 只检查数值列
        numeric_cols = ["open", "high", "low", "close", "volume"]

        for col in numeric_cols:
            values = [row.get(col) for row in data if row.get(col) is not None]
            if not values:
                continue

            mean = sum(values) / len(values)
            std = (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5

            if std == 0:
                continue

            outliers = [v for v in values if abs(v - mean) > 3 * std]
            outlier_ratio = len(outliers) / len(values)

            if outlier_ratio > rule.threshold:
                issues.append(ValidationIssue(
                    rule_id="OUTLIER_CHECK",
                    severity=Severity.WARNING,
                    message=f"列 '{col}' 异常值比例为 {outlier_ratio:.2%}",
                    column=col,
                    actual_value=outlier_ratio,
                    expected_value=rule.threshold,
                    count=len(outliers)
                ))

        return issues

    def _check_continuity(self, data: list[dict],
                          rule: ValidationRule) -> list[ValidationIssue]:
        """检查时间序列连续性"""
        issues = []

        if not data or "timestamp" not in data[0]:
            return issues

        # 提取时间戳
        timestamps = []
        for row in data:
            ts = row.get("timestamp")
            if ts:
                if isinstance(ts, str):
                    timestamps.append(datetime.fromisoformat(ts.replace("Z", "+00:00")))
                elif isinstance(ts, datetime):
                    timestamps.append(ts)

        if len(timestamps) < 2:
            return issues

        timestamps.sort()

        # 计算间隔
        intervals = [(timestamps[i+1] - timestamps[i]).total_seconds()
                     for i in range(len(timestamps)-1)]

        if not intervals:
            return issues

        # 找到最常见间隔
        from collections import Counter
        interval_counts = Counter(intervals)
        expected_interval = interval_counts.most_common(1)[0][0]

        # 检查缺失
        gaps = [i for i in intervals if i > expected_interval * 2]
        gap_ratio = len(gaps) / len(intervals) if intervals else 0

        if gap_ratio > rule.threshold:
            issues.append(ValidationIssue(
                rule_id="CONTINUITY_CHECK",
                severity=Severity.WARNING,
                message=f"时间序列存在 {len(gaps)} 处缺失，缺失比例为 {gap_ratio:.2%}",
                actual_value=gap_ratio,
                expected_value=rule.threshold,
                count=len(gaps)
            ))

        return issues

    def _check_schema(self, data: list[dict],
                      rule: ValidationRule) -> list[ValidationIssue]:
        """检查 Schema"""
        issues = []

        for i, row in enumerate(data):
            for col, spec in self.OHLCV_FIELDS.items():
                if col not in row:
                    continue

                value = row[col]

                # 类型检查
                if spec["type"] == "number":
                    if not isinstance(value, (int, float)):
                        issues.append(ValidationIssue(
                            rule_id="SCHEMA_CHECK",
                            severity=Severity.WARNING,
                            message=f"行 {i} 列 '{col}' 类型错误，期望 number，实际 {type(value).__name__}",
                            column=col,
                            row_index=i
                        ))

                # 范围检查
                if "min" in spec and isinstance(value, (int, float)):
                    if value < spec["min"]:
                        issues.append(ValidationIssue(
                            rule_id="SCHEMA_CHECK",
                            severity=Severity.CRITICAL,
                            message=f"行 {i} 列 '{col}' 值 {value} 小于最小值 {spec['min']}",
                            column=col,
                            row_index=i,
                            actual_value=value,
                            expected_value=spec["min"]
                        ))

        return issues

    def _check_duplicates(self, data: list[dict],
                          rule: ValidationRule) -> list[ValidationIssue]:
        """检查重复行"""
        issues = []

        # 基于时间戳检查重复
        timestamps = [row.get("timestamp") for row in data if row.get("timestamp")]
        unique_timestamps = set(timestamps)

        duplicate_count = len(timestamps) - len(unique_timestamps)
        duplicate_ratio = duplicate_count / len(timestamps) if timestamps else 0

        if duplicate_ratio > rule.threshold:
            issues.append(ValidationIssue(
                rule_id="DUPLICATE_CHECK",
                severity=Severity.WARNING,
                message=f"存在 {duplicate_count} 条重复记录，比例为 {duplicate_ratio:.2%}",
                actual_value=duplicate_ratio,
                expected_value=rule.threshold,
                count=duplicate_count
            ))

        return issues

    def _check_negative_values(self, data: list[dict],
                                rule: ValidationRule) -> list[ValidationIssue]:
        """检查负值"""
        issues = []

        for col in ["open", "high", "low", "close", "volume"]:
            negative_count = sum(1 for row in data
                                if row.get(col) is not None and row.get(col) < 0)

            if negative_count > 0:
                issues.append(ValidationIssue(
                    rule_id="NEGATIVE_VALUE_CHECK",
                    severity=Severity.CRITICAL,
                    message=f"列 '{col}' 存在 {negative_count} 个负值",
                    column=col,
                    count=negative_count
                ))

        return issues

    def _clean_data(self, data: list[dict],
                    issues: list[ValidationIssue]) -> list[dict]:
        """清理数据"""
        cleaned = []

        # 找出需要排除的行
        exclude_rows = set()
        for issue in issues:
            if issue.severity == Severity.CRITICAL and issue.row_index is not None:
                exclude_rows.add(issue.row_index)

        # 保留有效行
        for i, row in enumerate(data):
            if i not in exclude_rows:
                cleaned.append(row)

        return cleaned

    def execute(self, input_data: DataValidatorInput) -> DataValidatorOutput:
        """执行数据校验"""

        # 验证输入
        errors = input_data.validate()
        if errors:
            return DataValidatorOutput(
                status=ValidationStatus.INVALID,
                validation_result=ValidationResult(
                    total_rows=0,
                    valid_rows=0,
                    invalid_rows=0,
                    issues=[ValidationIssue(
                        rule_id="INPUT_ERROR",
                        severity=Severity.CRITICAL,
                        message="; ".join(errors)
                    )]
                ),
                evidence_ref="",
                error_code="VALIDATION_ERROR",
                error_message="; ".join(errors)
            )

        data = input_data.data
        rules = input_data.rules or DEFAULT_RULES

        # 执行所有检查
        all_issues = []

        for rule in rules:
            if not rule.enabled:
                continue

            if rule.rule_id == "MISSING_VALUE_CHECK":
                all_issues.extend(self._check_missing_values(data, rule))
            elif rule.rule_id == "OUTLIER_CHECK":
                all_issues.extend(self._check_outliers(data, rule))
            elif rule.rule_id == "CONTINUITY_CHECK":
                all_issues.extend(self._check_continuity(data, rule))
            elif rule.rule_id == "SCHEMA_CHECK":
                all_issues.extend(self._check_schema(data, rule))
            elif rule.rule_id == "DUPLICATE_CHECK":
                all_issues.extend(self._check_duplicates(data, rule))
            elif rule.rule_id == "NEGATIVE_VALUE_CHECK":
                all_issues.extend(self._check_negative_values(data, rule))

        # 计算有效行数
        invalid_rows = len(set(issue.row_index for issue in all_issues
                              if issue.row_index is not None))
        valid_rows = len(data) - invalid_rows

        # 确定状态
        critical_issues = [i for i in all_issues if i.severity == Severity.CRITICAL]
        if critical_issues:
            status = ValidationStatus.INVALID
        elif all_issues:
            status = ValidationStatus.PARTIAL
        else:
            status = ValidationStatus.VALID

        # 清理数据
        cleaned_data = self._clean_data(data, all_issues) if all_issues else data

        # 构建结果
        result = ValidationResult(
            total_rows=len(data),
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            issues=all_issues
        )

        # 生成证据引用
        evidence_ref = self._generate_evidence_ref(input_data, result)

        return DataValidatorOutput(
            status=status,
            validation_result=result,
            cleaned_data=cleaned_data,
            evidence_ref=evidence_ref
        )

    def run(self, input_dict: dict) -> dict:
        """标准运行接口"""
        input_data = DataValidatorInput(
            data=input_dict.get("data", []),
            schema=input_dict.get("schema"),
            strict_mode=input_dict.get("strict_mode", False)
        )

        output = self.execute(input_data)
        return output.to_dict()


# ============================================
# 便捷函数
# ============================================

def validate_data(data: list[dict], strict: bool = False) -> dict:
    """
    校验数据的便捷函数

    Args:
        data: 数据列表
        strict: 严格模式

    Returns:
        校验结果字典
    """
    skill = DataValidatorSkill()

    input_data = DataValidatorInput(
        data=data,
        strict_mode=strict
    )

    return skill.execute(input_data).to_dict()


# ============================================
# 示例用法
# ============================================

if __name__ == "__main__":
    # 示例数据
    sample_data = [
        {"timestamp": "2025-01-01T09:30:00", "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.0, "volume": 10000},
        {"timestamp": "2025-01-01T09:35:00", "open": 101.0, "high": 103.0, "low": 100.0, "close": 102.5, "volume": 12000},
        {"timestamp": "2025-01-01T09:40:00", "open": 102.5, "high": 104.0, "low": 102.0, "close": 103.5, "volume": 15000},
        {"timestamp": "2025-01-01T09:45:00", "open": None, "high": None, "low": None, "close": None, "volume": None},  # 缺失值
        {"timestamp": "2025-01-01T09:50:00", "open": -5.0, "high": 105.0, "low": 101.0, "close": 104.0, "volume": 8000},  # 负值
    ]

    result = validate_data(sample_data)

    print(f"状态: {result['status']}")
    print(f"总行数: {result['validation_result']['total_rows']}")
    print(f"有效行数: {result['validation_result']['valid_rows']}")
    print(f"问题数量: {len(result['validation_result']['issues'])}")

    print("\n问题列表:")
    for issue in result['validation_result']['issues']:
        print(f"  [{issue['severity']}] {issue['rule_id']}: {issue['message']}")
