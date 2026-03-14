"""
诱多识别器测试 - Week 2 防骗能力层

测试5种诱多模式的检测功能
"""

import pytest
from datetime import datetime, timezone, timedelta
from trap_detector import (
    TrapDetector,
    TrapType,
    TrapSeverity,
    MarketData,
    create_market_data_from_dict
)


class TestEndOfDayRallyDetector:
    """尾盘拉升检测器测试"""

    def test_no_rally_before_1430(self):
        """测试：14:30前不应检测到尾盘拉升"""
        detector = TrapDetector()

        data = MarketData(
            symbol="TEST",
            current_price=102.0,
            current_time=datetime.now().replace(hour=14, minute=0),
            price_history=[100.0] * 15 + [102.0],
            volume_history=[1000] * 16,
            timestamps=[datetime.now()] * 16,
            prev_close=100.0
        )

        result = detector.detect_all(data)
        assert not result.is_trap, "14:30前不应检测到尾盘拉升"

    def test_rally_with_weak_volume(self):
        """测试：尾盘拉升但成交量不配合"""
        detector = TrapDetector()

        # 模拟14:45突然拉升2%，但成交量没有明显放大
        data = MarketData(
            symbol="TEST",
            current_price=102.0,
            current_time=datetime.now().replace(hour=14, minute=45),
            price_history=[100.0] * 15 + [101.0, 102.0],
            volume_history=[1000] * 15 + [1050, 1080],  # 成交量没有明显放大
            timestamps=[datetime.now()] * 17,
            prev_close=100.0
        )

        result = detector.detect_all(data)
        assert result.is_trap, "应检测到尾盘拉升诱多"
        assert any(p.trap_type == TrapType.END_OF_DAY_RALLY for p in result.patterns)

    def test_rally_with_strong_volume(self):
        """测试：尾盘拉升且成交量配合（可能是真拉升）"""
        detector = TrapDetector()

        # 模拟14:45拉升2%，成交量也明显放大
        data = MarketData(
            symbol="TEST",
            current_price=102.0,
            current_time=datetime.now().replace(hour=14, minute=45),
            price_history=[100.0] * 15 + [101.0, 102.0],
            volume_history=[1000] * 15 + [1800, 2000],  # 成交量明显放大
            timestamps=[datetime.now()] * 17,
            prev_close=100.0
        )

        result = detector.detect_all(data)
        # 可能检测到但置信度较低，建议观察
        if result.is_trap:
            pattern = next(p for p in result.patterns if p.trap_type == TrapType.END_OF_DAY_RALLY)
            assert pattern.confidence < 0.7, "真拉升置信度应较低"
            assert "观察" in pattern.suggested_action


class TestFakeBreakoutDetector:
    """假突破检测器测试"""

    def test_no_breakout(self):
        """测试：没有突破不应检测到假突破"""
        detector = TrapDetector()

        data = MarketData(
            symbol="TEST",
            current_price=100.5,
            current_time=datetime.now(),
            price_history=[100.0] * 20,
            resistance_level=102.0,  # 当前价格未突破
            timestamps=[datetime.now()] * 20
        )

        result = detector.detect_all(data)
        assert not any(p.trap_type == TrapType.FAKE_BREAKOUT for p in result.patterns)

    def test_fake_breakout_with_pullback(self):
        """测试：突破后快速回落"""
        detector = TrapDetector()

        # 模拟突破102后回落到101.5
        data = MarketData(
            symbol="TEST",
            current_price=101.5,
            current_time=datetime.now(),
            price_history=[100.0] * 15 + [101.0, 102.5, 102.3, 101.8, 101.5],
            volume_history=[1000] * 15 + [1500, 1800, 1200, 1000, 900],  # 成交量萎缩
            resistance_level=102.0,
            timestamps=[datetime.now()] * 20
        )

        result = detector.detect_all(data)
        assert result.is_trap, "应检测到假突破"
        assert any(p.trap_type == TrapType.FAKE_BREAKOUT for p in result.patterns)


class TestVolumeStagnationDetector:
    """放量滞涨检测器测试"""

    def test_volume_surge_with_price_stagnation(self):
        """测试：放量但价格不涨"""
        detector = TrapDetector()

        # 模拟成交量放大1.5倍，但价格只涨0.3%
        data = MarketData(
            symbol="TEST",
            current_price=100.3,
            current_time=datetime.now(),
            price_history=[100.0] * 5 + [100.1, 100.2, 100.25, 100.3, 100.3],
            volume_history=[1000] * 5 + [1400, 1500, 1600, 1550, 1500],
            timestamps=[datetime.now()] * 10
        )

        result = detector.detect_all(data)
        assert result.is_trap, "应检测到放量滞涨"
        assert any(p.trap_type == TrapType.VOLUME_STAGNATION for p in result.patterns)

    def test_volume_surge_with_price_rise(self):
        """测试：放量且价格上涨（正常）"""
        detector = TrapDetector()

        # 模拟成交量放大且价格上涨1.5%
        data = MarketData(
            symbol="TEST",
            current_price=101.5,
            current_time=datetime.now(),
            price_history=[100.0] * 5 + [100.5, 101.0, 101.3, 101.5, 101.5],
            volume_history=[1000] * 5 + [1400, 1500, 1600, 1550, 1500],
            timestamps=[datetime.now()] * 10
        )

        result = detector.detect_all(data)
        # 可能不会检测到放量滞涨，或者置信度很低
        if result.is_trap:
            stagnation_patterns = [p for p in result.patterns if p.trap_type == TrapType.VOLUME_STAGNATION]
            if stagnation_patterns:
                assert stagnation_patterns[0].confidence < 0.6


class TestMoneyDivergenceDetector:
    """资金背离检测器测试"""

    def test_price_up_with_money_outflow(self):
        """测试：价格上涨但资金流出"""
        detector = TrapDetector()

        data = MarketData(
            symbol="TEST",
            current_price=102.0,
            current_time=datetime.now(),
            price_history=[100.0, 100.5, 101.0, 101.5, 102.0],
            net_inflow=-500000,  # 净流出50万
            main_inflow=-800000,  # 主力流出80万
            retail_inflow=300000,  # 散户流入30万
            timestamps=[datetime.now()] * 5
        )

        result = detector.detect_all(data)
        assert result.is_trap, "应检测到资金背离"
        assert any(p.trap_type == TrapType.MONEY_DIVERGENCE for p in result.patterns)

    def test_price_up_with_money_inflow(self):
        """测试：价格上涨且资金流入（正常）"""
        detector = TrapDetector()

        data = MarketData(
            symbol="TEST",
            current_price=102.0,
            current_time=datetime.now(),
            price_history=[100.0, 100.5, 101.0, 101.5, 102.0],
            net_inflow=500000,  # 净流入
            main_inflow=600000,  # 主力流入
            retail_inflow=-100000,  # 散户流出
            timestamps=[datetime.now()] * 5
        )

        result = detector.detect_all(data)
        assert not any(p.trap_type == TrapType.MONEY_DIVERGENCE for p in result.patterns)


class TestNewsTrapDetector:
    """消息诱多检测器测试"""

    def test_positive_news_with_weak_price(self):
        """测试：利好消息但价格反应弱且主力流出"""
        detector = TrapDetector()

        data = MarketData(
            symbol="TEST",
            current_price=100.3,
            current_time=datetime.now(),
            price_history=[100.0] * 5 + [100.1, 100.2, 100.25, 100.3, 100.3],
            volume_history=[1000] * 5 + [1400, 1500, 1600, 1550, 1500],
            has_news=True,
            news_sentiment="positive",
            main_inflow=-500000,  # 主力流出
            timestamps=[datetime.now()] * 10
        )

        result = detector.detect_all(data)
        assert result.is_trap, "应检测到消息诱多"
        assert any(p.trap_type == TrapType.NEWS_TRAP for p in result.patterns)

    def test_no_news(self):
        """测试：没有消息不应检测到消息诱多"""
        detector = TrapDetector()

        data = MarketData(
            symbol="TEST",
            current_price=100.3,
            current_time=datetime.now(),
            price_history=[100.0] * 10,
            has_news=False,
            timestamps=[datetime.now()] * 10
        )

        result = detector.detect_all(data)
        assert not any(p.trap_type == TrapType.NEWS_TRAP for p in result.patterns)


class TestTrapDetectorIntegration:
    """诱多检测器集成测试"""

    def test_multiple_traps(self):
        """测试：多个诱多模式同时存在"""
        detector = TrapDetector()

        # 模拟同时存在尾盘拉升和放量滞涨
        data = MarketData(
            symbol="TEST",
            current_price=102.0,
            current_time=datetime.now().replace(hour=14, minute=45),
            price_history=[100.0] * 10 + [101.0, 101.8, 102.0],
            volume_history=[1000] * 10 + [1050, 1100, 1080],  # 尾盘拉升但成交量不够
            net_inflow=-300000,
            main_inflow=-500000,
            retail_inflow=200000,
            timestamps=[datetime.now()] * 13,
            prev_close=100.0
        )

        result = detector.detect_all(data)

        # 应该检测到诱多
        assert result.is_trap
        assert result.should_avoid, "多个诱多模式应建议避免"
        assert result.overall_confidence > 0.5

    def test_no_trap(self):
        """测试：正常上涨不应检测到诱多"""
        detector = TrapDetector()

        # 模拟健康的上涨
        data = MarketData(
            symbol="TEST",
            current_price=102.0,
            current_time=datetime.now(),
            price_history=[100.0] * 5 + [100.5, 101.0, 101.5, 101.8, 102.0],
            volume_history=[1000] * 5 + [1200, 1300, 1400, 1500, 1600],  # 放量上涨
            net_inflow=800000,
            main_inflow=600000,
            retail_inflow=200000,
            timestamps=[datetime.now()] * 10
        )

        result = detector.detect_all(data)
        assert not result.is_trap, "健康的上涨不应检测为诱多"

    def test_get_statistics(self):
        """测试：获取统计信息"""
        detector = TrapDetector()

        # 运行几次检测
        for i in range(5):
            data = MarketData(
                symbol=f"TEST{i}",
                current_price=102.0,
                current_time=datetime.now(),
                price_history=[100.0] * 10,
                timestamps=[datetime.now()] * 10
            )
            detector.detect_all(data)

        stats = detector.get_statistics()
        assert 'total_detections' in stats
        assert 'trap_count' in stats
        assert 'detector_stats' in stats
        assert len(stats['detector_stats']) == 5  # 5个检测器


class TestMarketDataFactory:
    """MarketData工厂函数测试"""

    def test_create_from_dict(self):
        """测试：从字典创建MarketData"""
        data_dict = {
            'symbol': 'TEST',
            'price': 100.5,
            'price_history': [100.0, 100.2, 100.5],
            'volume_history': [1000, 1200, 1500],
            'net_inflow': 500000,
            'main_inflow': 400000,
            'retail_inflow': 100000,
            'resistance_level': 102.0,
            'prev_close': 100.0,
            'has_news': False
        }

        market_data = create_market_data_from_dict(data_dict)

        assert market_data.symbol == 'TEST'
        assert market_data.current_price == 100.5
        assert len(market_data.price_history) == 3
        assert market_data.net_inflow == 500000


# ============================================
# 运行测试
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
