"""
诱多识别器 (Trap Detector) - Week 2 防骗能力层

职责: 识别市场中的诱多陷阱，避免在假突破时买入
原则: 检测在前，决策在后

版本: 1.0.0 (Week 2 实施)

诱多类型:
1. 尾盘拉升 - 收盘前突然拉高，次日低开
2. 假突破 - 突破关键位后快速回落
3. 放量滞涨 - 放量但价格不涨
4. 资金背离 - 价格涨但资金流出
5. 消息诱多 - 利好消息发布但主力出货
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


# ============================================
# 数据模型定义
# ============================================

class TrapType(Enum):
    """诱多类型枚举"""
    END_OF_DAY_RALLY = "end_of_day_rally"      # 尾盘拉升
    FAKE_BREAKOUT = "fake_breakout"             # 假突破
    VOLUME_STAGNATION = "volume_stagnation"     # 放量滞涨
    MONEY_DIVERGENCE = "money_divergence"       # 资金背离
    NEWS_TRAP = "news_trap"                     # 消息诱多


class TrapSeverity(Enum):
    """诱多严重程度"""
    LOW = 1      # 轻度诱多，谨慎观望
    MEDIUM = 2   # 中度诱多，避免追高
    HIGH = 3     # 高度诱多，坚决不买
    CRITICAL = 4 # 极度诱多，考虑反手做空


@dataclass
class TrapPattern:
    """诱多模式检测结果"""
    trap_type: TrapType              # 诱多类型
    severity: TrapSeverity           # 严重程度
    confidence: float                # 置信度 0-1
    detected_at: datetime            # 检测时间
    symbol: str                      # 股票代码

    # 详细信息
    description: str                 # 描述
    signals: Dict[str, Any]          # 检测信号详情
    suggested_action: str            # 建议操作

    # 预测信息
    expected_decline: float = 0.0    # 预期跌幅
    time_horizon: str = "1-3天"      # 时间窗口


@dataclass
class TrapDetectionResult:
    """诱多检测总结果"""
    is_trap: bool                    # 是否为诱多
    patterns: List[TrapPattern]      # 检测到的诱多模式
    overall_confidence: float        # 综合置信度
    overall_severity: TrapSeverity   # 综合严重程度

    # 决策建议
    should_avoid: bool               # 是否应该避免买入
    reason: str                      # 原因说明


@dataclass
class MarketData:
    """市场数据输入"""
    # 基础数据
    symbol: str
    current_price: float
    current_time: datetime

    # 价格历史 (用于计算指标)
    price_history: List[float] = field(default_factory=list)
    volume_history: List[float] = field(default_factory=list)
    timestamps: List[datetime] = field(default_factory=list)

    # 盘口数据
    bid_price: float = 0.0
    ask_price: float = 0.0
    bid_volume: float = 0.0
    ask_volume: float = 0.0

    # 资金流数据
    net_inflow: float = 0.0          # 净流入
    main_inflow: float = 0.0         # 主力流入
    retail_inflow: float = 0.0       # 散户流入

    # 关键价位
    resistance_level: float = 0.0    # 阻力位
    support_level: float = 0.0       # 支撑位
    prev_close: float = 0.0          # 昨收价

    # 消息面
    has_news: bool = False           # 有无重大消息
    news_sentiment: str = "neutral"  # 消息情绪 positive/negative/neutral


# ============================================
# 诱多检测器基类
# ============================================

class BaseTrapDetector:
    """诱多检测器基类"""

    def __init__(self, name: str, trap_type: TrapType):
        self.name = name
        self.trap_type = trap_type
        self.detection_count = 0
        self.true_positive_count = 0  # 后续用于双向验证

    def detect(self, data: MarketData) -> Optional[TrapPattern]:
        """
        检测诱多模式

        Args:
            data: 市场数据

        Returns:
            TrapPattern if detected, None otherwise
        """
        raise NotImplementedError

    def _calculate_severity(self, signals: Dict) -> TrapSeverity:
        """根据信号计算严重程度"""
        score = signals.get('risk_score', 0)

        if score >= 0.8:
            return TrapSeverity.CRITICAL
        elif score >= 0.6:
            return TrapSeverity.HIGH
        elif score >= 0.4:
            return TrapSeverity.MEDIUM
        else:
            return TrapSeverity.LOW


# ============================================
# 具体诱多检测器实现
# ============================================

class EndOfDayRallyDetector(BaseTrapDetector):
    """
    尾盘拉升检测器

    特征:
    - 14:30后突然拉升
    - 拉升时放量不明显
    - 拉升后维持高位到收盘
    - 次日大概率低开

    检测逻辑:
    1. 检查当前时间是否在尾盘时段 (14:30-15:00)
    2. 计算尾盘涨幅 (14:30价格 vs 当前价格)
    3. 检查成交量是否配合
    4. 检查是否有持续性
    """

    def __init__(self):
        super().__init__("尾盘拉升检测器", TrapType.END_OF_DAY_RALLY)
        self.rally_threshold = 0.015  # 尾盘涨幅阈值 1.5%
        self.volume_ratio_threshold = 1.2  # 成交量倍数阈值
        self.start_time = timedelta(hours=14, minutes=30)

    def detect(self, data: MarketData) -> Optional[TrapPattern]:
        """检测尾盘拉升诱多"""

        # 1. 检查时间是否在尾盘
        current_time = data.current_time.time()
        if current_time.hour < 14 or (current_time.hour == 14 and current_time.minute < 30):
            return None

        # 2. 需要有足够的历史数据
        if len(data.price_history) < 20 or len(data.timestamps) < 20:
            return None

        # 3. 找到14:30左右的价格作为基准
        base_price = None
        for i, ts in enumerate(reversed(data.timestamps)):
            if ts.hour == 14 and ts.minute >= 30:
                base_price = data.price_history[-(i+1)]
                break

        if base_price is None:
            base_price = data.price_history[-20]  # 使用20个周期前的价格

        # 4. 计算尾盘涨幅
        rally = (data.current_price - base_price) / base_price

        # 5. 检查成交量
        if len(data.volume_history) >= 20:
            recent_volume = sum(data.volume_history[-5:]) / 5
            earlier_volume = sum(data.volume_history[-20:-5]) / 15
            volume_ratio = recent_volume / earlier_volume if earlier_volume > 0 else 1
        else:
            volume_ratio = 1.0

        # 6. 判断是否为尾盘拉升诱多
        signals = {
            'rally': rally,
            'volume_ratio': volume_ratio,
            'is_rallying': rally > self.rally_threshold,
            'volume_weak': volume_ratio < self.volume_ratio_threshold
        }

        # 诱多判断：涨幅大但成交量不配合
        if signals['is_rallying'] and signals['volume_weak']:
            confidence = min(0.9, rally * 30)  # 涨幅越大置信度越高
            severity = self._calculate_severity({
                'risk_score': confidence * (1.5 if volume_ratio < 1.0 else 1.0)
            })

            return TrapPattern(
                trap_type=self.trap_type,
                severity=severity,
                confidence=confidence,
                detected_at=data.current_time,
                symbol=data.symbol,
                description=f"尾盘拉升{rally*100:.2f}%，成交量不配合（{volume_ratio:.1f}倍）",
                signals=signals,
                suggested_action="避免尾盘追高",
                expected_decline=-0.02,  # 预期次日低开2%左右
                time_horizon="次日开盘"
            )

        # 也可能是真拉升，但需要谨慎
        elif signals['is_rallying']:
            return TrapPattern(
                trap_type=self.trap_type,
                severity=TrapSeverity.LOW,
                confidence=0.4,
                detected_at=data.current_time,
                symbol=data.symbol,
                description=f"尾盘拉升{rally*100:.2f}%，但成交量配合",
                signals=signals,
                suggested_action="观察次日走势",
                expected_decline=-0.01,
                time_horizon="次日开盘"
            )

        return None


class FakeBreakoutDetector(BaseTrapDetector):
    """
    假突破检测器

    特征:
    - 突破关键阻力位
    - 突破后快速回落
    - 成交量先放后缩
    - 突破无法维持

    检测逻辑:
    1. 检测是否突破阻力位
    2. 检查突破后的价格表现
    3. 检查成交量变化
    4. 判断是否为假突破
    """

    def __init__(self):
        super().__init__("假突破检测器", TrapType.FAKE_BREAKOUT)
        self.breakout_threshold = 0.01  # 突破阈值 1%
        self.pullback_threshold = 0.005  # 回落阈值 0.5%
        self.check_window = 10  # 检查窗口

    def detect(self, data: MarketData) -> Optional[TrapPattern]:
        """检测假突破诱多"""

        # 需要有阻力位数据
        if data.resistance_level <= 0:
            return None

        # 需要足够的历史数据
        if len(data.price_history) < self.check_window + 5:
            return None

        # 1. 检测是否突破
        breakout = (data.current_price - data.resistance_level) / data.resistance_level

        if breakout < self.breakout_threshold:
            return None  # 没有突破

        # 2. 检查突破后的表现
        # 获取突破后的价格序列
        prices_after_breakout = []
        for i, price in enumerate(reversed(data.price_history)):
            if price > data.resistance_level:
                prices_after_breakout.append(price)
            if len(prices_after_breakout) >= self.check_window:
                break

        if len(prices_after_breakout) < 3:
            return None

        # 3. 检查是否快速回落
        highest = max(prices_after_breakout)
        current = prices_after_breakout[0]
        pullback = (highest - current) / highest

        # 4. 检查成交量变化
        volume_declining = False
        if len(data.volume_history) >= self.check_window:
            recent_vol = sum(data.volume_history[:self.check_window//2]) / (self.check_window//2)
            earlier_vol = sum(data.volume_history[self.check_window//2:self.check_window]) / (self.check_window//2)
            volume_declining = recent_vol < earlier_vol * 0.8

        # 5. 判断是否为假突破
        signals = {
            'breakout': breakout,
            'pullback': pullback,
            'highest_price': highest,
            'current_price': current,
            'is_pulling_back': pullback > self.pullback_threshold,
            'volume_declining': volume_declining
        }

        # 假突破判断：突破后快速回落且成交量萎缩
        if signals['is_pulling_back'] and volume_declining:
            confidence = min(0.95, pullback * 100)
            severity = self._calculate_severity({
                'risk_score': confidence * (1.2 if pullback > 0.01 else 1.0)
            })

            return TrapPattern(
                trap_type=self.trap_type,
                severity=severity,
                confidence=confidence,
                detected_at=data.current_time,
                symbol=data.symbol,
                description=f"假突破{data.resistance_level:.2f}，回落{pullback*100:.2f}%",
                signals=signals,
                suggested_action="突破失败，等待回踩确认",
                expected_decline=-0.03,
                time_horizon="1-3天"
            )

        # 可能是假突破的早期信号
        elif signals['is_pulling_back']:
            return TrapPattern(
                trap_type=self.trap_type,
                severity=TrapSeverity.MEDIUM,
                confidence=0.6,
                detected_at=data.current_time,
                symbol=data.symbol,
                description=f"突破后回落{pullback*100:.2f}%，需观察",
                signals=signals,
                suggested_action="谨慎观察，等待确认",
                expected_decline=-0.015,
                time_horizon="1-2天"
            )

        return None


class VolumeStagnationDetector(BaseTrapDetector):
    """
    放量滞涨检测器

    特征:
    - 成交量明显放大
    - 价格却不涨或涨幅很小
    - 主力可能在出货

    检测逻辑:
    1. 检测成交量是否放大
    2. 检测价格涨幅
    3. 计算量价背离程度
    4. 判断是否为放量滞涨
    """

    def __init__(self):
        super().__init__("放量滞涨检测器", TrapType.VOLUME_STAGNATION)
        self.volume_surge_threshold = 1.5  # 放量阈值 1.5倍
        self.price_change_threshold = 0.005  # 价格变化阈值 0.5%
        self.lookback_period = 10

    def detect(self, data: MarketData) -> Optional[TrapPattern]:
        """检测放量滞涨诱多"""

        # 需要足够的历史数据
        if len(data.price_history) < self.lookback_period + 5:
            return None
        if len(data.volume_history) < self.lookback_period + 5:
            return None

        # 1. 计算平均成交量
        avg_volume = sum(data.volume_history[-self.lookback_period:-5]) / (self.lookback_period - 5)
        recent_volume = sum(data.volume_history[-5:]) / 5

        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1

        # 2. 计算价格变化
        start_price = data.price_history[-self.lookback_period]
        end_price = data.current_price
        price_change = (end_price - start_price) / start_price

        # 3. 判断放量滞涨
        signals = {
            'volume_ratio': volume_ratio,
            'price_change': price_change,
            'is_volume_surge': volume_ratio > self.volume_surge_threshold,
            'is_price_stagnant': abs(price_change) < self.price_change_threshold
        }

        # 放量但价格不涨 = 可能是出货
        if signals['is_volume_surge'] and signals['is_price_stagnant']:
            # 放量倍数越大，滞涨越严重，诱多可能性越高
            confidence = min(0.9, (volume_ratio - 1) * 0.5)
            severity = self._calculate_severity({
                'risk_score': confidence * (1.3 if price_change < 0 else 1.0)
            })

            return TrapPattern(
                trap_type=self.trap_type,
                severity=severity,
                confidence=confidence,
                detected_at=data.current_time,
                symbol=data.symbol,
                description=f"放量{volume_ratio:.1f}倍但价格{price_change*100:+.2f}%",
                signals=signals,
                suggested_action="放量滞涨，警惕主力出货",
                expected_decline=-0.025,
                time_horizon="1-3天"
            )

        # 放量但涨幅很小，也需要警惕
        elif signals['is_volume_surge'] and price_change < self.price_change_threshold * 2:
            confidence = min(0.7, (volume_ratio - 1) * 0.3)
            return TrapPattern(
                trap_type=self.trap_type,
                severity=TrapSeverity.LOW,
                confidence=confidence,
                detected_at=data.current_time,
                symbol=data.symbol,
                description=f"放量{volume_ratio:.1f}倍但涨幅仅{price_change*100:.2f}%",
                signals=signals,
                suggested_action="观察价格能否突破",
                expected_decline=-0.015,
                time_horizon="1-2天"
            )

        return None


class MoneyDivergenceDetector(BaseTrapDetector):
    """
    资金背离检测器

    特征:
    - 价格上涨
    - 但资金净流出
    - 主力流出，散户流入

    检测逻辑:
    1. 检测价格变化
    2. 检测资金流向
    3. 检测主力/散户资金对比
    4. 判断是否为资金背离
    """

    def __init__(self):
        super().__init__("资金背离检测器", TrapType.MONEY_DIVERGENCE)
        self.price_change_threshold = 0.005  # 价格变化阈值
        self.outflow_threshold = 0.0  # 资金流出阈值

    def detect(self, data: MarketData) -> Optional[TrapPattern]:
        """检测资金背离诱多"""

        # 需要资金流数据
        if len(data.price_history) < 5:
            return None

        # 1. 计算价格变化
        price_change = (data.current_price - data.price_history[-5]) / data.price_history[-5]

        # 2. 检查资金流向
        # 价格涨但资金流出 = 背离
        signals = {
            'price_change': price_change,
            'net_inflow': data.net_inflow,
            'main_inflow': data.main_inflow,
            'retail_inflow': data.retail_inflow,
            'is_price_up': price_change > self.price_change_threshold,
            'is_net_outflow': data.net_inflow < self.outflow_threshold,
            'is_main_outflow': data.main_inflow < 0,
            'is_retail_inflow': data.retail_inflow > 0
        }

        # 3. 判断资金背离
        # 最危险的背离：价格上涨 + 主力流出 + 散户流入
        is_divergence = (
            signals['is_price_up'] and
            signals['is_net_outflow'] and
            signals['is_main_outflow'] and
            signals['is_retail_inflow']
        )

        if is_divergence:
            # 主力流出越多，背离越严重
            main_outflow_ratio = abs(data.main_inflow) / (abs(data.main_inflow) + abs(data.retail_inflow))
            confidence = min(0.95, main_outflow_ratio * 1.5)
            severity = self._calculate_severity({
                'risk_score': confidence * (1.2 if price_change > 0.01 else 1.0)
            })

            return TrapPattern(
                trap_type=self.trap_type,
                severity=severity,
                confidence=confidence,
                detected_at=data.current_time,
                symbol=data.symbol,
                description=f"价格涨{price_change*100:.2f}%但资金流出{data.net_inflow/10000:.1f}万",
                signals=signals,
                suggested_action="资金背离，警惕诱多出货",
                expected_decline=-0.04,
                time_horizon="1-3天"
            )

        # 普通背离：价格涨但资金流出
        elif signals['is_price_up'] and signals['is_net_outflow']:
            confidence = 0.6
            return TrapPattern(
                trap_type=self.trap_type,
                severity=TrapSeverity.MEDIUM,
                confidence=confidence,
                detected_at=data.current_time,
                symbol=data.symbol,
                description=f"价格涨{price_change*100:.2f}%但资金流出",
                signals=signals,
                suggested_action="资金不支持上涨，谨慎",
                expected_decline=-0.02,
                time_horizon="1-2天"
            )

        return None


class NewsTrapDetector(BaseTrapDetector):
    """
    消息诱多检测器

    特征:
    - 发布重大利好消息
    - 但股价表现不佳
    - 主力借机出货

    检测逻辑:
    1. 检查是否有重大消息
    2. 检查消息情绪
    3. 检查价格反应
    4. 检查资金流向
    5. 判断是否为消息诱多
    """

    def __init__(self):
        super().__init__("消息诱多检测器", TrapType.NEWS_TRAP)
        self.price_reaction_threshold = 0.01  # 价格反应阈值
        self.volume_surge_threshold = 1.3  # 放量阈值

    def detect(self, data: MarketData) -> Optional[TrapPattern]:
        """检测消息诱多"""

        # 1. 需要有消息
        if not data.has_news:
            return None

        # 2. 检查消息情绪
        if data.news_sentiment != "positive":
            return None  # 不是利好消息

        # 3. 检查价格反应
        if len(data.price_history) < 10:
            return None

        price_change = (data.current_price - data.price_history[-10]) / data.price_history[-10]

        # 4. 检查成交量
        if len(data.volume_history) >= 10:
            avg_volume = sum(data.volume_history[-10:-5]) / 5
            recent_volume = sum(data.volume_history[-5:]) / 5
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
        else:
            volume_ratio = 1.0

        # 5. 检查资金流向
        signals = {
            'has_news': True,
            'news_sentiment': data.news_sentiment,
            'price_change': price_change,
            'volume_ratio': volume_ratio,
            'main_inflow': data.main_inflow,
            'is_price_weak': price_change < self.price_reaction_threshold,
            'is_volume_surge': volume_ratio > self.volume_surge_threshold,
            'is_main_outflow': data.main_inflow < 0
        }

        # 消息诱多判断：利好消息但价格不强 + 主力流出
        is_trap = (
            signals['is_price_weak'] and
            signals['is_volume_surge'] and
            signals['is_main_outflow']
        )

        if is_trap:
            confidence = 0.85
            severity = TrapSeverity.HIGH

            return TrapPattern(
                trap_type=self.trap_type,
                severity=severity,
                confidence=confidence,
                detected_at=data.current_time,
                symbol=data.symbol,
                description=f"利好消息但价格仅涨{price_change*100:.2f}%，主力出货",
                signals=signals,
                suggested_action="利好不涨，警惕出货",
                expected_decline=-0.05,
                time_horizon="1-5天"
            )

        # 利好但价格反应弱，需要警惕
        elif signals['is_price_weak']:
            confidence = 0.6
            return TrapPattern(
                trap_type=self.trap_type,
                severity=TrapSeverity.MEDIUM,
                confidence=confidence,
                detected_at=data.current_time,
                symbol=data.symbol,
                description=f"利好消息但价格反应弱（{price_change*100:.2f}%）",
                signals=signals,
                suggested_action="利好不涨，观察资金流向",
                expected_decline=-0.02,
                time_horizon="1-3天"
            )

        return None


# ============================================
# 诱多检测器主类
# ============================================

class TrapDetector:
    """
    诱多识别器 - Week 2 防骗能力层

    综合使用5种检测器识别市场诱多陷阱：
    1. 尾盘拉升检测器
    2. 假突破检测器
    3. 放量滞涨检测器
    4. 资金背离检测器
    5. 消息诱多检测器

    使用方式:
        detector = TrapDetector()
        result = detector.detect_all(market_data)
        if result.is_trap:
            print(f"检测到诱多陷阱: {result.reason}")
    """

    def __init__(self):
        self.detectors: List[BaseTrapDetector] = [
            EndOfDayRallyDetector(),
            FakeBreakoutDetector(),
            VolumeStagnationDetector(),
            MoneyDivergenceDetector(),
            NewsTrapDetector()
        ]

        # 统计信息
        self.total_detections = 0
        self.trap_count = 0

    def detect_all(self, data: MarketData) -> TrapDetectionResult:
        """
        使用所有检测器检测诱多模式

        Args:
            data: 市场数据

        Returns:
            TrapDetectionResult: 综合检测结果
        """

        self.total_detections += 1

        detected_patterns = []

        # 运行所有检测器
        for detector in self.detectors:
            try:
                pattern = detector.detect(data)
                if pattern:
                    detected_patterns.append(pattern)
                    detector.detection_count += 1
            except Exception as e:
                # 单个检测器失败不影响其他检测器
                print(f"检测器 {detector.name} 失败: {e}")
                continue

        # 综合判断
        if not detected_patterns:
            return TrapDetectionResult(
                is_trap=False,
                patterns=[],
                overall_confidence=0.0,
                overall_severity=TrapSeverity.LOW,
                should_avoid=False,
                reason="未检测到诱多模式"
            )

        # 有诱多模式被检测到
        self.trap_count += 1

        # 计算综合置信度
        overall_confidence = max(p.confidence for p in detected_patterns)

        # 计算综合严重程度
        severity_scores = {TrapSeverity.LOW: 1, TrapSeverity.MEDIUM: 2,
                         TrapSeverity.HIGH: 3, TrapSeverity.CRITICAL: 4}
        max_severity = max(detected_patterns, key=lambda p: severity_scores[p.severity])

        # 判断是否应该避免买入
        should_avoid = (
            max_severity.severity in [TrapSeverity.HIGH, TrapSeverity.CRITICAL] or
            len(detected_patterns) >= 2 or  # 多个诱多模式
            overall_confidence > 0.7
        )

        # 生成原因说明
        pattern_names = [p.trap_type.value for p in detected_patterns]
        reason = f"检测到{len(detected_patterns)}个诱多模式: {', '.join(pattern_names)}"

        return TrapDetectionResult(
            is_trap=True,
            patterns=detected_patterns,
            overall_confidence=overall_confidence,
            overall_severity=max_severity.severity,
            should_avoid=should_avoid,
            reason=reason
        )

    def get_statistics(self) -> Dict[str, Any]:
        """获取检测统计信息"""
        return {
            'total_detections': self.total_detections,
            'trap_count': self.trap_count,
            'trap_rate': self.trap_count / self.total_detections if self.total_detections > 0 else 0,
            'detector_stats': [
                {
                    'name': d.name,
                    'detection_count': d.detection_count
                }
                for d in self.detectors
            ]
        }


# ============================================
# 辅助函数
# ============================================

def create_market_data_from_dict(data: Dict) -> MarketData:
    """从字典创建MarketData对象"""
    return MarketData(
        symbol=data.get('symbol', ''),
        current_price=data.get('price', 0.0),
        current_time=datetime.now(timezone.utc),
        price_history=data.get('price_history', []),
        volume_history=data.get('volume_history', []),
        timestamps=[datetime.now(timezone.utc)] * len(data.get('price_history', [])),
        bid_price=data.get('bid_price', 0.0),
        ask_price=data.get('ask_price', 0.0),
        net_inflow=data.get('net_inflow', 0.0),
        main_inflow=data.get('main_inflow', 0.0),
        retail_inflow=data.get('retail_inflow', 0.0),
        resistance_level=data.get('resistance_level', 0.0),
        support_level=data.get('support_level', 0.0),
        prev_close=data.get('prev_close', 0.0),
        has_news=data.get('has_news', False),
        news_sentiment=data.get('news_sentiment', 'neutral')
    )


# ============================================
# 测试代码
# ============================================

if __name__ == "__main__":
    # 创建诱多检测器
    detector = TrapDetector()

    # 模拟尾盘拉升数据
    test_data = MarketData(
        symbol="TEST",
        current_price=102.0,
        current_time=datetime.now().replace(hour=14, minute=45),
        price_history=[100.0] * 15 + [101.0, 101.5, 102.0],
        volume_history=[1000] * 15 + [1100, 1050, 1080],
        timestamps=[datetime.now()] * 18,
        prev_close=100.0
    )

    # 检测诱多
    result = detector.detect_all(test_data)

    print(f"检测结果: {result.is_trap}")
    print(f"原因: {result.reason}")
    print(f"综合置信度: {result.overall_confidence:.2f}")
    print(f"综合严重程度: {result.overall_severity}")
    print(f"是否应避免: {result.should_avoid}")

    for pattern in result.patterns:
        print(f"\n- {pattern.description}")
        print(f"  建议操作: {pattern.suggested_action}")
