"""
作业批改器 - 验证预测与实际的偏差

对比昨日生成的预测作业与今日实际市场数据
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict, Any, Optional
import json

from .homework import Homework, Prediction, Question


@dataclass
class GradeResult:
    """批改结果"""
    date: date
    homework: Homework
    actual_data: Dict[str, Dict]

    # 统计
    total_predictions: int = 0
    correct_predictions: int = 0
    accuracy: float = 0.0

    total_questions: int = 0
    correct_questions: int = 0

    # 错题
    mistakes: List[Dict] = field(default_factory=list)

    # 正确但原因不一致
    correct_but_wrong_reason: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'date': self.date.isoformat(),
            'total_predictions': self.total_predictions,
            'correct_predictions': self.correct_predictions,
            'accuracy': self.accuracy,
            'total_questions': self.total_questions,
            'correct_questions': self.correct_questions,
            'mistakes': self.mistakes,
            'correct_but_wrong_reason': self.correct_but_wrong_reason,
        }


class HomeworkGrader:
    """
    作业批改器

    对比预测作业与实际市场数据，给出批改结果
    """

    def __init__(self, tolerance: float = 0.01):
        """
        初始化批改器

        Args:
            tolerance: 容忍误差（默认1%）
        """
        self.tolerance = tolerance

    def grade(self, homework: Homework, actual_data: Dict[str, Dict]) -> GradeResult:
        """
        批改作业

        Args:
            homework: 待批改的作业
            actual_data: 实际市场数据 {symbol: {field: value}}

        Returns:
            GradeResult: 批改结果
        """
        result = GradeResult(
            date=homework.date,
            homework=homework,
            actual_data=actual_data,
        )

        # 批改预测题
        result.total_predictions = len(homework.predictions)
        result.correct_predictions = 0

        for pred in homework.predictions:
            actual = actual_data.get(pred.symbol, {}).get(pred.field)
            if actual is not None:
                grade = self._grade_prediction(pred, actual)
                pred.verified = True
                pred.actual = actual
                pred.result = grade

                if grade['correct']:
                    result.correct_predictions += 1
                else:
                    # 记录错题
                    result.mistakes.append({
                        'type': 'prediction',
                        'symbol': pred.symbol,
                        'field': pred.field,
                        'expected': pred.expected,
                        'actual': actual,
                        'error': grade['error'],
                        'reasoning': pred.reasoning,
                    })

                # 检查原因是否一致
                if grade['correct']:
                    reason_check = self._check_reasoning(pred, actual, actual_data)
                    if not reason_check['match']:
                        result.correct_but_wrong_reason.append({
                            'symbol': pred.symbol,
                            'prediction': pred.to_dict(),
                            'reason_mismatch': reason_check,
                        })

        # 计算准确率
        if result.total_predictions > 0:
            result.accuracy = result.correct_predictions / result.total_predictions

        # 批改问答题
        result.total_questions = len(homework.questions)
        result.correct_questions = 0

        for q in homework.questions:
            answer = actual_data.get(q.symbol, {}).get(q.question)
            if answer is not None:
                q.answer = str(answer)
                q.verified = True

                grade = self._grade_question(q, answer)
                if grade['correct']:
                    result.correct_questions += 1
                else:
                    # 记录错题
                    result.mistakes.append({
                        'type': 'question',
                        'symbol': q.symbol,
                        'question': q.question,
                        'hypothesis': q.hypothesis,
                        'actual_answer': answer,
                    })

        return result

    def _grade_prediction(self, pred: Prediction, actual: Any) -> Dict:
        """
        批改单个预测

        Returns:
            Dict: {correct: bool, error: float}
        """
        if isinstance(pred.expected, (int, float)) and isinstance(actual, (int, float)):
            error = (actual - pred.expected) / pred.expected
            correct = abs(error) <= self.tolerance
            return {'correct': correct, 'error': error}
        else:
            # 非数值预测（如信号类型）
            correct = str(actual) == str(pred.expected)
            return {'correct': correct, 'error': 0.0 if correct else 1.0}

    def _grade_question(self, q: Question, answer: Any) -> Dict:
        """
        批改单个问题

        Returns:
            Dict: {correct: bool}
        """
        # 简化版：检查答案是否符合假设
        # 实际应该更复杂，可能需要解析自然语言
        answer_str = str(answer).lower()
        hypothesis_str = q.hypothesis.lower()

        # 包含关键词就认为正确
        keywords = ['是', 'yes', 'true', 'confirm', '达到', '超过']
        correct = any(kw in answer_str for kw in keywords)

        return {'correct': correct}

    def _check_reasoning(
        self,
        pred: Prediction,
        actual: Any,
        actual_data: Dict[str, Dict]
    ) -> Dict:
        """
        检查预测正确的原因是否与预期一致

        这是双向验证的核心：不仅结果要对，原因也要对
        """
        # 提取预期原因
        expected_reason = pred.reasoning.lower()

        # 找出实际原因
        actual_reason = self._find_actual_reason(pred.symbol, actual_data)

        # 检查是否一致
        match = self._compare_reasons(expected_reason, actual_reason)

        return {
            'match': match,
            'expected': expected_reason,
            'actual': actual_reason,
        }

    def _find_actual_reason(self, symbol: str, actual_data: Dict[str, Dict]) -> str:
        """
        找出实际走势的原因

        基于实际数据推断原因
        """
        data = actual_data.get(symbol, {})

        # 检查各种信号
        reasons = []

        if data.get('breakout_confirmed'):
            reasons.append('突破确认')
        if data.get('volume_surge'):
            reasons.append('放量')
        if data.get('resonance_count', 0) >= 2:
            reasons.append('多信号共振')

        return ' + '.join(reasons) if reasons else '其他原因'

    def _compare_reasons(self, expected: str, actual: str) -> bool:
        """比较原因是否一致"""
        # 简化版：检查关键词是否匹配
        keywords = ['突破', '放量', '共振', '验证', '诱多']

        expected_keywords = [kw for kw in keywords if kw in expected]
        actual_keywords = [kw for kw in keywords if kw in actual]

        # 至少有一个关键词匹配
        return len(set(expected_keywords) & set(actual_keywords)) > 0

    def print_report(self, result: GradeResult):
        """打印批改报告"""
        print("\n" + "=" * 60)
        print(f"作业批改报告 - {result.date}")
        print("=" * 60)

        # 预测题结果
        print(f"\n【预测题】")
        print(f"总计: {result.total_predictions}题")
        print(f"正确: {result.correct_predictions}题")
        print(f"准确率: {result.accuracy:.1%}")

        for pred in result.homework.predictions:
            if pred.verified:
                status = "✓" if pred.result['correct'] else "✗"
                print(f"  {status} {pred.symbol}: 预测{pred.expected} → 实际{pred.actual}")
                if not pred.result['correct']:
                    print(f"      误差: {pred.result['error']:.2%}")
                    print(f"      理由: {pred.reasoning}")

        # 问答题结果
        if result.total_questions > 0:
            print(f"\n【问答题】")
            print(f"总计: {result.total_questions}题")
            print(f"正确: {result.correct_questions}题")

            for q in result.homework.questions:
                if q.verified:
                    status = "✓" if self._grade_question(q, q.answer)['correct'] else "✗"
                    print(f"  {status} {q.symbol}: {q.question}")
                    print(f"      回答: {q.answer}")

        # 错题总结
        if result.mistakes:
            print(f"\n【错题本】({len(result.mistakes)}题)")
            for i, m in enumerate(result.mistakes, 1):
                print(f"\n  错题 {i}:")
                print(f"    标的: {m['symbol']}")
                if m['type'] == 'prediction':
                    print(f"    预测: {m['field']} = {m['expected']}")
                    print(f"    实际: {m['actual']}")
                    print(f"    误差: {m['error']:.2%}")
                else:
                    print(f"    问题: {m['question']}")
                    print(f"    假设: {m['hypothesis']}")
                    print(f"    实际: {m['actual_answer']}")

        # 原因不一致的题
        if result.correct_but_wrong_reason:
            print(f"\n【原因不一致】({len(result.correct_but_wrong_reason)}题)")
            for i, item in enumerate(result.correct_but_wrong_reason, 1):
                print(f"\n  题 {i}: {item['symbol']}")
                print(f"    预期原因: {item['reason_mismatch']['expected']}")
                print(f"    实际原因: {item['reason_mismatch']['actual']}")

        print("\n" + "=" * 60)
