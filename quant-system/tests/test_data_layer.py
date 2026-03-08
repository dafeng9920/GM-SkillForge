"""
数据层 Skills 集成测试

测试 P0-01 openbb-fetch 和 P0-02 data-validator
"""

import pytest
from datetime import date, datetime
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skills.data.openbb_fetch import (
    OpenBBFetchSkill,
    OpenBBFetchInput,
    OpenBBFetchOutput,
    DataType,
    Provider,
    FetchStatus,
    fetch_market_data
)

from skills.data.data_validator import (
    DataValidatorSkill,
    DataValidatorInput,
    DataValidatorOutput,
    ValidationStatus,
    Severity,
    validate_data
)


# ============================================
# Fixtures
# ============================================

@pytest.fixture
def sample_ohlcv_data():
    """示例 OHLCV 数据"""
    return [
        {
            "timestamp": "2025-01-01T09:30:00",
            "symbol": "AAPL",
            "open": 100.0,
            "high": 102.0,
            "low": 99.0,
            "close": 101.0,
            "volume": 10000
        },
        {
            "timestamp": "2025-01-01T09:35:00",
            "symbol": "AAPL",
            "open": 101.0,
            "high": 103.0,
            "low": 100.0,
            "close": 102.5,
            "volume": 12000
        },
        {
            "timestamp": "2025-01-01T09:40:00",
            "symbol": "AAPL",
            "open": 102.5,
            "high": 104.0,
            "low": 102.0,
            "close": 103.5,
            "volume": 15000
        }
    ]


@pytest.fixture
def sample_data_with_issues():
    """包含问题的示例数据"""
    return [
        {"timestamp": "2025-01-01T09:30:00", "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.0, "volume": 10000},
        {"timestamp": "2025-01-01T09:35:00", "open": None, "high": 103.0, "low": 100.0, "close": 102.5, "volume": 12000},  # 缺失值
        {"timestamp": "2025-01-01T09:40:00", "open": -5.0, "high": 104.0, "low": 102.0, "close": 103.5, "volume": 8000},  # 负值
        {"timestamp": "2025-01-01T09:30:00", "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.0, "volume": 10000},  # 重复
    ]


# ============================================
# P0-01: openbb-fetch 测试
# ============================================

class TestOpenBBFetchInput:
    """测试 OpenBBFetchInput"""

    def test_valid_input(self):
        """测试有效输入"""
        input_data = OpenBBFetchInput(
            data_type=DataType.EQUITY_PRICE_HISTORICAL,
            symbols=["AAPL", "MSFT"],
            provider=Provider.YAHOO
        )

        errors = input_data.validate()
        assert len(errors) == 0

    def test_empty_symbols(self):
        """测试空 symbols"""
        input_data = OpenBBFetchInput(
            data_type=DataType.EQUITY_PRICE_HISTORICAL,
            symbols=[]
        )

        errors = input_data.validate()
        assert len(errors) > 0
        assert "symbols 不能为空" in errors[0]

    def test_too_many_symbols(self):
        """测试过多 symbols"""
        input_data = OpenBBFetchInput(
            data_type=DataType.EQUITY_PRICE_HISTORICAL,
            symbols=["SYM" + str(i) for i in range(101)]
        )

        errors = input_data.validate()
        assert len(errors) > 0
        assert "100" in errors[0]

    def test_invalid_date_range(self):
        """测试无效日期范围"""
        input_data = OpenBBFetchInput(
            data_type=DataType.EQUITY_PRICE_HISTORICAL,
            symbols=["AAPL"],
            start_date=date(2025, 2, 1),
            end_date=date(2025, 1, 1)
        )

        errors = input_data.validate()
        assert len(errors) > 0
        assert "start_date" in errors[0]


class TestOpenBBFetchSkill:
    """测试 OpenBBFetchSkill"""

    def test_skill_properties(self):
        """测试 Skill 属性"""
        skill = OpenBBFetchSkill()
        assert skill.SKILL_ID == "openbb-fetch"
        assert skill.VERSION == "1.0.0"

    @patch('skills.data.openbb_fetch.OpenBBFetchSkill._get_client')
    def test_execute_success(self, mock_get_client, sample_ohlcv_data):
        """测试成功执行"""
        # Mock OpenBB 客户端
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_df = MagicMock()
        mock_df.reset_index.return_value.to_dict.return_value = sample_ohlcv_data
        mock_result.to_dataframe.return_value = mock_df
        mock_client.equity.price.historical.return_value = mock_result
        mock_get_client.return_value = mock_client

        skill = OpenBBFetchSkill()
        input_data = OpenBBFetchInput(
            data_type=DataType.EQUITY_PRICE_HISTORICAL,
            symbols=["AAPL"],
            provider=Provider.YAHOO
        )

        output = skill.execute(input_data)

        assert output.status == FetchStatus.COMPLETED
        assert len(output.data) == 3
        assert output.metrics.rows_fetched == 3
        assert output.evidence_ref.startswith("evidence://")

    def test_execute_validation_error(self):
        """测试输入验证错误"""
        skill = OpenBBFetchSkill()
        input_data = OpenBBFetchInput(
            data_type=DataType.EQUITY_PRICE_HISTORICAL,
            symbols=[]  # 空 symbols
        )

        output = skill.execute(input_data)

        assert output.status == FetchStatus.FAILED
        assert output.error_code == "VALIDATION_ERROR"


# ============================================
# P0-02: data-validator 测试
# ============================================

class TestDataValidatorInput:
    """测试 DataValidatorInput"""

    def test_valid_input(self, sample_ohlcv_data):
        """测试有效输入"""
        input_data = DataValidatorInput(data=sample_ohlcv_data)
        errors = input_data.validate()
        assert len(errors) == 0

    def test_empty_data(self):
        """测试空数据"""
        input_data = DataValidatorInput(data=[])
        errors = input_data.validate()
        assert len(errors) > 0


class TestDataValidatorSkill:
    """测试 DataValidatorSkill"""

    def test_skill_properties(self):
        """测试 Skill 属性"""
        skill = DataValidatorSkill()
        assert skill.SKILL_ID == "data-validator"
        assert skill.VERSION == "1.0.0"

    def test_validate_clean_data(self, sample_ohlcv_data):
        """测试校验干净数据"""
        skill = DataValidatorSkill()
        input_data = DataValidatorInput(data=sample_ohlcv_data)

        output = skill.execute(input_data)

        assert output.status == ValidationStatus.VALID
        assert output.validation_result.total_rows == 3
        assert output.validation_result.valid_rows == 3
        assert len(output.validation_result.issues) == 0

    def test_validate_data_with_issues(self, sample_data_with_issues):
        """测试校验包含问题的数据"""
        skill = DataValidatorSkill()
        input_data = DataValidatorInput(data=sample_data_with_issues)

        output = skill.execute(input_data)

        assert output.status == ValidationStatus.INVALID
        assert len(output.validation_result.issues) > 0

        # 检查是否检测到负值
        negative_issues = [i for i in output.validation_result.issues
                          if i.rule_id == "NEGATIVE_VALUE_CHECK"]
        assert len(negative_issues) > 0

    def test_missing_value_detection(self):
        """测试缺失值检测"""
        data = [
            {"open": None, "high": 102, "low": 99, "close": 101, "volume": 1000},
            {"open": None, "high": 103, "low": 100, "close": 102, "volume": 1200},
            {"open": None, "high": 104, "low": 101, "close": 103, "volume": 1500},
        ]

        skill = DataValidatorSkill()
        input_data = DataValidatorInput(data=data)

        output = skill.execute(input_data)

        missing_issues = [i for i in output.validation_result.issues
                         if i.rule_id == "MISSING_VALUE_CHECK"]
        assert len(missing_issues) > 0

    def test_negative_value_detection(self):
        """测试负值检测"""
        data = [
            {"open": -100, "high": 102, "low": 99, "close": 101, "volume": 1000},
        ]

        skill = DataValidatorSkill()
        input_data = DataValidatorInput(data=data)

        output = skill.execute(input_data)

        negative_issues = [i for i in output.validation_result.issues
                          if i.rule_id == "NEGATIVE_VALUE_CHECK"]
        assert len(negative_issues) > 0
        assert negative_issues[0].severity == Severity.CRITICAL

    def test_duplicate_detection(self):
        """测试重复检测"""
        data = [
            {"timestamp": "2025-01-01T09:30:00", "open": 100, "high": 102, "low": 99, "close": 101, "volume": 1000},
            {"timestamp": "2025-01-01T09:35:00", "open": 101, "high": 103, "low": 100, "close": 102, "volume": 1200},
            {"timestamp": "2025-01-01T09:30:00", "open": 100, "high": 102, "low": 99, "close": 101, "volume": 1000},  # 重复
        ]

        skill = DataValidatorSkill()
        input_data = DataValidatorInput(data=data)

        output = skill.execute(input_data)

        duplicate_issues = [i for i in output.validation_result.issues
                           if i.rule_id == "DUPLICATE_CHECK"]
        assert len(duplicate_issues) > 0

    def test_cleaned_data(self, sample_data_with_issues):
        """测试数据清理"""
        skill = DataValidatorSkill()
        input_data = DataValidatorInput(data=sample_data_with_issues)

        output = skill.execute(input_data)

        # 清理后的数据应该不包含有问题的行
        assert len(output.cleaned_data) <= len(sample_data_with_issues)


# ============================================
# 集成测试
# ============================================

class TestDataLayerIntegration:
    """数据层集成测试"""

    @patch('skills.data.openbb_fetch.OpenBBFetchSkill._get_client')
    def test_fetch_then_validate(self, mock_get_client):
        """测试: 获取数据 -> 校验数据 流程"""
        # Mock 数据
        sample_data = [
            {"timestamp": "2025-01-01T09:30:00", "symbol": "AAPL", "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.0, "volume": 10000},
            {"timestamp": "2025-01-01T09:35:00", "symbol": "AAPL", "open": 101.0, "high": 103.0, "low": 100.0, "close": 102.5, "volume": 12000},
        ]

        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_df = MagicMock()
        mock_df.reset_index.return_value.to_dict.return_value = sample_data
        mock_result.to_dataframe.return_value = mock_df
        mock_client.equity.price.historical.return_value = mock_result
        mock_get_client.return_value = mock_client

        # Step 1: 获取数据
        fetch_skill = OpenBBFetchSkill()
        fetch_input = OpenBBFetchInput(
            data_type=DataType.EQUITY_PRICE_HISTORICAL,
            symbols=["AAPL"],
            provider=Provider.YAHOO
        )
        fetch_output = fetch_skill.execute(fetch_input)

        assert fetch_output.status == FetchStatus.COMPLETED

        # Step 2: 校验数据
        validate_skill = DataValidatorSkill()
        validate_input = DataValidatorInput(data=fetch_output.data)
        validate_output = validate_skill.execute(validate_input)

        assert validate_output.status == ValidationStatus.VALID
        assert validate_output.evidence_ref.startswith("evidence://")


# ============================================
# 运行测试
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
