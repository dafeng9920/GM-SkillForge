"""
错题分析器 - 分析预测错误的原因和规律

从批改结果中找出错误模式，为系统迭代提供依据
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Dict, Any, Optional
from collections import Counter
import json


@dataclass
class MistakeAnalysis:
    """错题分析结果"""
    mistake: Dict
    causes: List[str]
    primary_cause: str
    action_items: List[str]

    def to_dict(self) -> Dict:
        return {
            'mistake': self.mistake,
            'causes': self.causes,
            'primary_cause': self.primary_cause,
            'action_items': self.action_items,
        }


@dataclass
class PatternAnalysis:
    """规律分析结果"""
    patterns: Dict[str, int]  # 原因 -> 次数
    top_causes: List[tuple]   # (原因, 次数) 按次数排序
    recommendations: List[str]

    def to_dict(self) -> Dict:
        return {
            'patterns': self.patterns,
            'top_causes': self.top_causes,
            'recommendations': self.recommendations,
        }


class MistakeAnalyzer:
    """
    错题分析器

    分析预测错误的原因，找出规律模式，提出改进建议
    """

    def __init__(self):
        self.mistake_history: List[Dict] = []
        self.pattern_history: List[PatternAnalysis] = []

    def analyze(self, mistake: Dict, context: Optional[Dict] = None) -> MistakeAnalysis:
        """
        分析单个错题

        Args:
            mistake: 错题数据
            context: 上下文信息（市场环境、日期等）

        Returns:
            MistakeAnalysis: 分析结果
        """
        causes = []

        # 1. 信号层面分析
        signal_cause = self._analyze_signal_level(mistake)
        if signal_cause:
            causes.append(signal_cause)

        # 2. 确认层面分析
        confirmation_cause = self._analyze_confirmation_level(mistake)
        if confirmation_cause:
            causes.append(confirmation_cause)

        # 3. 验证点层面分析
        validation_cause = self._analyze_validation_level(mistake)
        if validation_cause:
            causes.append(validation_cause)

        # 4. 市场层面分析
        if context:
            market_cause = self._analyze_market_level(mistake, context)
            if market_cause:
                causes.append(market_cause)

        # 5. 确定主要原因
        primary_cause = causes[0] if causes else '未知原因'

        # 6. 生成改进建议
        action_items = self._generate_action_items(primary_cause, mistake)

        # 7. 保存到历史
        self.mistake_history.append(mistake)

        return MistakeAnalysis(
            mistake=mistake,
            causes=causes,
            primary_cause=primary_cause,
            action_items=action_items,
        )

    def _analyze_signal_level(self, mistake: Dict) -> Optional[str]:
        """分析信号层面的问题"""
        reasoning = mistake.get('reasoning', '').lower()

        if '突破' in reasoning and mistake.get('error', 0) < -0.02:
            return '突破信号假阳性'
        elif '诱多' in reasoning and mistake.get('error', 0) > 0.02:
            return '诱多信号假阳性'
        elif '共振' in reasoning and mistake.get('error', 0) < -0.03:
            return '共振信号失效'
        elif '放量' in reasoning:
            actual_volume_change = mistake.get('actual_data', {}).get('volume_change', 0)
            if actual_volume_change < 1.2:
                return '放量信号不持续'

        return None

    def _analyze_confirmation_level(self, mistake: Dict) -> Optional[str]:
        """分析确认层面的问题"""
        error = mistake.get('error', 0)

        if error > 0.02:  # 实际涨幅远超预期
            return '确认条件过于保守（错过机会）'
        elif error < -0.01 and error > -0.02:  # 小幅亏损
            return '确认条件不够严格'
        elif abs(error) < 0.005:  # 非常接近
            return '确认条件基本合理'

        return None

    def _analyze_validation_level(self, mistake: Dict) -> Optional[str]:
        """分析验证点层面的问题"""
        field = mistake.get('field', '')

        if field == 'validation_status':
            actual = mistake.get('actual')
            expected = mistake.get('expected')

            if expected == 'passed' and actual == 'failed':
                return '验证点目标设置过高'
            elif expected == 'failed' and actual == 'passed':
                return '验证点目标设置过低'

        return None

    def _analyze_market_level(self, mistake: Dict, context: Dict) -> Optional[str]:
        """分析市场层面的问题"""
        market_change = context.get('market_change', 0)
        volatility = context.get('volatility', 0)

        if abs(market_change) > 0.03:  # 市场剧烈波动
            return '市场环境突变'
        elif volatility > 0.05:  # 高波动
            return '市场波动过大'
        elif context.get('gap_up', False):
            return '跳空影响'
        elif context.get('gap_down', False):
            return '跳空影响'

        return None

    def _generate_action_items(self, cause: str, mistake: Dict) -> List[str]:
        """根据错误原因生成改进建议"""
        actions = []

        cause_actions = {
            '突破信号假阳性': [
                '提高突破确认的成交量要求',
                '增加突破后的时间验证',
                '添加假突破检测器',
            ],
            '诱多信号假阳性': [
                '优化诱多识别算法',
                '增加确认时间窗口',
            ],
            '共振信号失效': [
                '提高共振信号数要求',
                '增加共振信号的质量检查',
            ],
            '放量信号不持续': [
                '检查成交量持续性',
                '增加成交量衰减检测',
            ],
            '确认条件过于保守': [
                '降低确认阈值',
                '缩短确认时间窗口',
            ],
            '确认条件不够严格': [
                '提高确认阈值',
                '延长确认时间窗口',
            ],
            '验证点目标设置过高': [
                '降低验证点目标涨幅',
                '延长验证点时间窗口',
            ],
            '验证点目标设置过低': [
                '提高验证点目标涨幅',
                '缩短验证点时间窗口',
            ],
            '市场环境突变': [
                '增加市场环境监测',
                '添加市场突变保护机制',
            ],
        }

        return cause_actions.get(cause, ['继续观察'])

    def find_patterns(self, min_count: int = 2) -> PatternAnalysis:
        """
        找出错题中的规律模式

        Args:
            min_count: 最小出现次数

        Returns:
            PatternAnalysis: 规律分析结果
        """
        if not self.mistake_history:
            return PatternAnalysis(
                patterns={},
                top_causes=[],
                recommendations=['暂无数据'],
            )

        # 分析所有错题
        all_analyses = []
        for mistake in self.mistake_history:
            analysis = self.analyze(mistake)
            all_analyses.append(analysis)

        # 统计原因
        cause_counter = Counter()
        for analysis in all_analyses:
            cause_counter[analysis.primary_cause] += 1

        # 过滤掉出现次数少的
        patterns = {
            cause: count
            for cause, count in cause_counter.items()
            if count >= min_count
        }

        # 排序
        top_causes = cause_counter.most_common()

        # 生成建议
        recommendations = self._generate_recommendations(patterns)

        result = PatternAnalysis(
            patterns=patterns,
            top_causes=top_causes,
            recommendations=recommendations,
        )

        self.pattern_history.append(result)
        return result

    def _generate_recommendations(self, patterns: Dict[str, int]) -> List[str]:
        """基于规律模式生成改进建议"""
        recommendations = []

        # 按严重程度排序
        sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)

        for cause, count in sorted_patterns[:5]:  # 只取前5个
            if count >= 3:
                recommendations.append(
                    f"【高频错误】{cause}出现{count}次，建议优先处理"
                )

            # 具体建议
            if '突破' in cause and count >= 2:
                recommendations.append('  → 调整突破确认参数（min_breakout_amp）')
            elif '共振' in cause and count >= 2:
                recommendations.append('  → 调整共振要求（min_resonance）')
            elif '验证点' in cause and count >= 2:
                recommendations.append('  → 调整验证点参数（target_gain, time_window）')

        return recommendations

    def print_patterns(self, analysis: PatternAnalysis):
        """打印规律分析"""
        print("\n" + "=" * 60)
        print("错题规律分析")
        print("=" * 60)

        if not analysis.patterns:
            print("\n暂无足够的错题数据")
            return

        print(f"\n【错误统计】")
        print(f"总错题数: {len(self.mistake_history)}")
        print(f"发现规律: {len(analysis.patterns)}种")

        print(f"\n【错误排行】")
        for i, (cause, count) in enumerate(analysis.top_causes, 1):
            bar = "█" * (count * 2)
            print(f"  {i}. {cause}: {count}次 {bar}")

        print(f"\n【改进建议】")
        for i, rec in enumerate(analysis.recommendations, 1):
            print(f"  {i}. {rec}")

        print("\n" + "=" * 60)
