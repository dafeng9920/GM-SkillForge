"""
每日闭环系统 - 协调复盘、批改、分析、迭代

整合所有组件，形成完整的每日闭环流程
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from .homework import Homework, HomeworkGenerator
from .grader import HomeworkGrader, GradeResult
from .analyzer import MistakeAnalyzer, PatternAnalysis
from .iterator import SystemIterator, IterationReport


@dataclass
class DailyLoopResult:
    """每日闭环结果"""
    date: date
    grade_result: Optional[GradeResult] = None
    pattern_analysis: Optional[PatternAnalysis] = None
    iteration_report: Optional[IterationReport] = None

    def to_dict(self) -> Dict:
        return {
            'date': self.date.isoformat(),
            'grade_result': self.grade_result.to_dict() if self.grade_result else None,
            'pattern_analysis': self.pattern_analysis.to_dict() if self.pattern_analysis else None,
            'iteration_report': self.iteration_report.to_dict() if self.iteration_report else None,
        }


class DailyClosedLoop:
    """
    每日闭环系统

    完整流程：
    1. 加载昨日作业
    2. 批改作业
    3. 分析错题
    4. 找出规律
    5. 迭代系统
    6. 生成今日作业
    """

    def __init__(self, phase4_engine, data_dir: str = None):
        """
        初始化闭环系统

        Args:
            phase4_engine: Phase4Engine实例
            data_dir: 数据存储目录
        """
        self.phase4 = phase4_engine

        # 数据目录
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent.parent / 'data' / 'closed_loop'
        else:
            data_dir = Path(data_dir)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 组件
        self.homework_generator = HomeworkGenerator(phase4_engine)
        self.grader = HomeworkGrader()
        self.analyzer = MistakeAnalyzer()
        self.iterator = SystemIterator(phase4_engine)

        # 状态
        self.yesterday_homework: Optional[Homework] = None
        self.today_homework: Optional[Homework] = None
        self.loop_history: List[DailyLoopResult] = []

    def run(
        self,
        today_date: date,
        today_data: Dict[str, Dict],
        next_day_data: Optional[Dict[str, Dict]] = None,
    ) -> DailyLoopResult:
        """
        运行完整闭环

        Args:
            today_date: 今日日期
            today_data: 今日市场数据
            next_day_data: 次日市场数据（如果已有）

        Returns:
            DailyLoopResult: 闭环结果
        """
        result = DailyLoopResult(date=today_date)

        print("\n" + "=" * 70)
        print(f"    每日闭环系统 - {today_date}")
        print("=" * 70)

        # Step 1: 加载昨日作业
        yesterday_path = self._get_homework_path(today_date, offset=-1)
        if yesterday_path.exists():
            print("\n【Step 1】加载昨日作业")
            self.yesterday_homework = Homework.load(str(yesterday_path))
            print(f"  ✓ 已加载 {len(self.yesterday_homework.predictions)} 个预测")
            print(f"  ✓ 已加载 {len(self.yesterday_homework.questions)} 个问题")
        else:
            print("\n【Step 1】无昨日作业（首次运行）")
            self.yesterday_homework = None

        # Step 2: 批改昨日作业
        if self.yesterday_homework and next_day_data:
            print("\n【Step 2】批改昨日作业")
            result.grade_result = self.grader.grade(self.yesterday_homework, next_day_data)
            self.grader.print_report(result.grade_result)
        else:
            print("\n【Step 2】跳过批改（无作业或无次日数据）")

        # Step 3: 分析错题
        if result.grade_result and result.grade_result.mistakes:
            print("\n【Step 3】分析错题原因")

            # 分析每个错题
            for mistake in result.grade_result.mistakes:
                context = self._get_context(today_date)
                analysis = self.analyzer.analyze(mistake, context)
                print(f"  • {mistake['symbol']}: {analysis.primary_cause}")

            # 找出规律
            print("\n【Step 4】找出错题规律")
            result.pattern_analysis = self.analyzer.find_patterns(min_count=2)
            self.analyzer.print_patterns(result.pattern_analysis)
        else:
            print("\n【Step 3-4】无错题需要分析")
            result.pattern_analysis = None

        # Step 5: 迭代系统
        if result.pattern_analysis and result.pattern_analysis.patterns:
            print("\n【Step 5】系统迭代")
            result.iteration_report = self.iterator.iterate(
                result.pattern_analysis,
                min_occurrence=3
            )
            self.iterator.print_report(result.iteration_report)

            # 保存迭代历史
            history_path = self.data_dir / 'iteration_history.json'
            self.iterator.save_history(str(history_path))
        else:
            print("\n【Step 5】无需迭代")
            result.iteration_report = None

        # Step 6: 生成今日作业
        print("\n【Step 6】生成今日作业")
        self.today_homework = self._generate_homework(today_date, today_data)
        self._save_homework(self.today_homework)
        self._print_homework_summary(self.today_homework)

        # 保存结果
        self.loop_history.append(result)

        print("\n" + "=" * 70)
        print("    闭环完成")
        print("=" * 70)

        return result

    def _generate_homework(self, today_date: date, today_data: Dict) -> Homework:
        """生成今日作业"""
        # 提取今日交易的标的
        traded_symbols = [
            symbol for symbol, data in today_data.items()
            if data.get('buy_signal') or data.get('sell_signal')
        ]

        if traded_symbols:
            # 基于今日交易生成
            homework = self.homework_generator.generate_from_day_trading(
                date=today_date,
                traded_symbols=traded_symbols,
                market_data=today_data,
            )
        else:
            # 基于持仓状态生成
            open_positions = {
                symbol: data
                for symbol, data in today_data.items()
                if data.get('has_position')
            }
            homework = self.homework_generator.generate_from_validation_status(
                date=today_date,
                open_positions=open_positions,
            )

        return homework

    def _save_homework(self, homework: Homework):
        """保存作业"""
        filepath = self._get_homework_path(homework.date)
        homework.save(str(filepath))
        print(f"  ✓ 作业已保存: {filepath.name}")

    def _get_homework_path(self, date: date, offset: int = 0) -> Path:
        """获取作业文件路径"""
        from datetime import timedelta
        target_date = date + timedelta(days=offset)
        filename = f"homework_{target_date.isoformat()}.json"
        return self.data_dir / filename

    def _get_context(self, date: date) -> Dict:
        """获取上下文信息"""
        # 简化版，实际应该从数据库或文件读取
        return {
            'market_change': 0.0,
            'volatility': 0.02,
            'gap_up': False,
            'gap_down': False,
        }

    def _print_homework_summary(self, homework: Homework):
        """打印作业摘要"""
        print(f"\n【明日作业摘要】")
        print(f"  预测: {len(homework.predictions)}个")
        print(f"  问题: {len(homework.questions)}个")

        if homework.predictions:
            print(f"\n  预测列表:")
            for pred in homework.predictions[:3]:  # 只显示前3个
                print(f"    • {pred.symbol}: {pred.field} = {pred.expected}")

        if homework.questions:
            print(f"\n  问题列表:")
            for q in homework.questions[:3]:  # 只显示前3个
                print(f"    • {q.symbol}: {q.question}")

    def save_result(self, result: DailyLoopResult):
        """保存闭环结果"""
        filepath = self.data_dir / f"loop_result_{result.date.isoformat()}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

    def get_summary(self, last_n_days: int = 7) -> Dict:
        """获取最近N天的闭环摘要"""
        recent_results = self.loop_history[-last_n_days:]

        if not recent_results:
            return {'message': '暂无闭环数据'}

        total_predictions = sum(
            r.grade_result.total_predictions
            for r in recent_results
            if r.grade_result
        )
        total_correct = sum(
            r.grade_result.correct_predictions
            for r in recent_results
            if r.grade_result
        )
        avg_accuracy = total_correct / total_predictions if total_predictions > 0 else 0

        total_mistakes = sum(
            len(r.grade_result.mistakes)
            for r in recent_results
            if r.grade_result
        )

        total_iterations = sum(
            len(r.iteration_report.iterations)
            for r in recent_results
            if r.iteration_report
        )

        return {
            'period': f'最近{last_n_days}天',
            'total_predictions': total_predictions,
            'total_correct': total_correct,
            'avg_accuracy': f'{avg_accuracy:.1%}',
            'total_mistakes': total_mistakes,
            'total_iterations': total_iterations,
            'system_improving': total_iterations > 0,
        }
