"""
系统迭代器 - 基于分析结果优化系统参数

根据错题分析和规律模式，自动调整 Phase 4 系统参数
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

from .analyzer import PatternAnalysis, MistakeAnalysis


@dataclass
class Iteration:
    """单次系统迭代"""
    timestamp: datetime
    target: str  # 迭代目标组件
    parameter: str  # 参数名
    old_value: Any
    new_value: Any
    reason: str  # 迭代原因
    expected_improvement: str  # 预期改进

    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'target': self.target,
            'parameter': self.parameter,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'reason': self.reason,
            'expected_improvement': self.expected_improvement,
        }


@dataclass
class IterationReport:
    """迭代报告"""
    iterations: List[Iteration] = field(default_factory=list)
    summary: str = ""
    applied_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            'iterations': [it.to_dict() for it in self.iterations],
            'summary': self.summary,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
        }


class SystemIterator:
    """
    系统迭代器

    基于错题分析结果，自动调整 Phase 4 系统参数
    """

    # 参数调整规则
    ADJUSTMENT_RULES = {
        '突破信号假阳性': {
            'target': 'perception',
            'adjustments': [
                {'param': 'min_breakout_amp', 'action': 'increase', 'factor': 1.2},
                {'param': 'min_volume_ratio', 'action': 'increase', 'factor': 1.1},
            ]
        },
        '共振信号失效': {
            'target': 'confirmation',
            'adjustments': [
                {'param': 'min_resonance', 'action': 'increase', 'step': 1},
            ]
        },
        '确认条件过于保守': {
            'target': 'confirmation',
            'adjustments': [
                {'param': 'min_breakout_amp', 'action': 'decrease', 'factor': 0.9},
                {'param': 'min_resonance', 'action': 'decrease', 'step': 1},
            ]
        },
        '确认条件不够严格': {
            'target': 'confirmation',
            'adjustments': [
                {'param': 'min_breakout_amp', 'action': 'increase', 'factor': 1.1},
                {'param': 'min_resonance', 'action': 'increase', 'step': 1},
            ]
        },
        '验证点目标设置过高': {
            'target': 'validation',
            'adjustments': [
                {'param': 'validation_target_gain', 'action': 'decrease', 'factor': 0.8},
                {'param': 'validation_time_window', 'action': 'increase', 'factor': 1.2},
            ]
        },
        '验证点目标设置过低': {
            'target': 'validation',
            'adjustments': [
                {'param': 'validation_target_gain', 'action': 'increase', 'factor': 1.2},
                {'param': 'validation_time_window', 'action': 'decrease', 'factor': 0.9},
            ]
        },
    }

    def __init__(self, phase4_engine):
        """
        初始化系统迭代器

        Args:
            phase4_engine: Phase4Engine实例
        """
        self.phase4 = phase4
        self.iteration_history: List[Iteration] = []

    def iterate(
        self,
        pattern_analysis: PatternAnalysis,
        min_occurrence: int = 3
    ) -> IterationReport:
        """
        根据规律分析结果迭代系统

        Args:
            pattern_analysis: 规律分析结果
            min_occurrence: 最小出现次数（低于此次数不迭代）

        Returns:
            IterationReport: 迭代报告
        """
        iterations = []

        for cause, count in pattern_analysis.patterns.items():
            if count < min_occurrence:
                continue

            # 获取调整规则
            rule = self.ADJUSTMENT_RULES.get(cause)
            if not rule:
                continue

            # 应用调整
            for adj in rule['adjustments']:
                iteration = self._apply_adjustment(cause, count, adj)
                if iteration:
                    iterations.append(iteration)

        # 生成总结
        summary = self._generate_summary(iterations)

        report = IterationReport(
            iterations=iterations,
            summary=summary,
            applied_at=datetime.now(),
        )

        return report

    def _apply_adjustment(
        self,
        cause: str,
        count: int,
        adjustment: Dict
    ) -> Optional[Iteration]:
        """应用单个调整"""
        param = adjustment['param']
        action = adjustment['action']

        # 获取当前值
        current_value = self._get_current_value(param)
        if current_value is None:
            return None

        # 计算新值
        new_value = self._calculate_new_value(current_value, action, adjustment)

        # 验证新值
        if not self._validate_new_value(param, new_value):
            return None

        # 应用新值
        self._set_new_value(param, new_value)

        # 记录迭代
        iteration = Iteration(
            timestamp=datetime.now(),
            target=adjustment.get('target', 'unknown'),
            parameter=param,
            old_value=current_value,
            new_value=new_value,
            reason=f'{cause}出现{count}次',
            expected_improvement=f'通过调整{param}减少{cause}错误'
        )

        self.iteration_history.append(iteration)

        return iteration

    def _get_current_value(self, param: str) -> Optional[Any]:
        """获取参数当前值"""
        if param in ['min_breakout_amp', 'min_volume_ratio', 'min_resonance',
                    'resistance_lookback']:
            return getattr(self.phase4, param, None)
        elif param in ['validation_target_gain', 'validation_time_window']:
            return getattr(self.phase4.validation_manager, param, None)
        return None

    def _calculate_new_value(
        self,
        current: Any,
        action: str,
        adjustment: Dict
    ) -> Any:
        """计算新值"""
        if isinstance(current, (int, float)):
            if action == 'increase':
                factor = adjustment.get('factor', 1.1)
                return current * factor
            elif action == 'decrease':
                factor = adjustment.get('factor', 0.9)
                return current * factor
            elif action == 'add':
                step = adjustment.get('step', 1)
                return current + step
            elif action == 'subtract':
                step = adjustment.get('step', 1)
                return current - step

        return current

    def _validate_new_value(self, param: str, value: Any) -> bool:
        """验证新值是否合理"""
        # 参数范围检查
        ranges = {
            'min_breakout_amp': (0.001, 0.1),
            'min_volume_ratio': (1.1, 5.0),
            'min_resonance': (1, 5),
            'resistance_lookback': (5, 100),
            'validation_target_gain': (0.001, 0.1),
            'validation_time_window': (1, 120),
        }

        if param in ranges and isinstance(value, (int, float)):
            min_val, max_val = ranges[param]
            return min_val <= value <= max_val

        return True

    def _set_new_value(self, param: str, value: Any):
        """设置新值到系统"""
        if param in ['min_breakout_amp', 'min_volume_ratio', 'min_resonance',
                    'resistance_lookback']:
            setattr(self.phase4, param, value)
        elif param in ['validation_target_gain', 'validation_time_window']:
            setattr(self.phase4.validation_manager, param, value)

    def _generate_summary(self, iterations: List[Iteration]) -> str:
        """生成迭代总结"""
        if not iterations:
            return "无需迭代"

        lines = [
            f"系统迭代完成，共调整{len(iterations)}个参数：",
        ]

        for it in iterations:
            lines.append(
                f"  • {it.parameter}: {it.old_value:.4f} → {it.new_value:.4f} ({it.reason})"
            )

        return "\n".join(lines)

    def print_report(self, report: IterationReport):
        """打印迭代报告"""
        print("\n" + "=" * 60)
        print("系统迭代报告")
        print("=" * 60)

        if not report.iterations:
            print("\n无需迭代")
            print("=" * 60)
            return

        print(f"\n应用时间: {report.applied_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"迭代次数: {len(report.iterations)}")

        print(f"\n【参数调整】")
        for it in report.iterations:
            print(f"\n  目标: {it.target}")
            print(f"  参数: {it.parameter}")
            print(f"  调整: {it.old_value:.4f} → {it.new_value:.4f}")
            print(f"  原因: {it.reason}")
            print(f"  预期: {it.expected_improvement}")

        print(f"\n【总结】")
        print(report.summary)

        print("\n" + "=" * 60)

    def save_history(self, filepath: str):
        """保存迭代历史"""
        data = {
            'iterations': [it.to_dict() for it in self.iteration_history],
            'count': len(self.iteration_history),
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
