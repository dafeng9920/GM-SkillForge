"""
作业生成器 - 基于Phase 4决策生成预测作业

从Phase 4引擎的决策中提取信息，生成次日验证作业
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import json


@dataclass
class Prediction:
    """单个预测"""
    symbol: str
    date: date
    field: str  # 'close', 'high', 'low', 'volume', 'signal_type'
    expected: Any
    reasoning: str
    confidence: float = 0.0
    actual: Any = None
    verified: bool = False
    result: Optional[Dict] = None

    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'date': self.date.isoformat(),
            'field': self.field,
            'expected': self.expected,
            'reasoning': self.reasoning,
            'confidence': self.confidence,
            'actual': self.actual,
            'verified': self.verified,
            'result': self.result,
        }


@dataclass
class Question:
    """单个问题"""
    symbol: str
    date: date
    question: str
    hypothesis: str
    answer: Optional[str] = None
    verified: bool = False

    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'date': self.date.isoformat(),
            'question': self.question,
            'hypothesis': self.hypothesis,
            'answer': self.answer,
            'verified': self.verified,
        }


@dataclass
class Homework:
    """作业 - 包含预测和问题"""
    date: date
    predictions: List[Prediction] = field(default_factory=list)
    questions: List[Question] = field(default_factory=list)

    def add_prediction(self, symbol: str, field: str, expected: Any,
                      reasoning: str, confidence: float = 0.0):
        """添加预测"""
        pred = Prediction(
            symbol=symbol,
            date=self.date,
            field=field,
            expected=expected,
            reasoning=reasoning,
            confidence=confidence,
        )
        self.predictions.append(pred)

    def add_question(self, symbol: str, question: str, hypothesis: str):
        """添加问题"""
        q = Question(
            symbol=symbol,
            date=self.date,
            question=question,
            hypothesis=hypothesis,
        )
        self.questions.append(q)

    def to_dict(self) -> Dict:
        return {
            'date': self.date.isoformat(),
            'predictions': [p.to_dict() for p in self.predictions],
            'questions': [q.to_dict() for q in self.questions],
        }

    def save(self, filepath: str):
        """保存作业到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, filepath: str) -> 'Homework':
        """从文件加载作业"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        homework = cls(date=datetime.fromisoformat(data['date']).date())
        for p_data in data['predictions']:
            pred = Prediction(**p_data)
            homework.predictions.append(pred)
        for q_data in data['questions']:
            q = Question(**q_data)
            homework.questions.append(q)
        return homework


class HomeworkGenerator:
    """
    作业生成器

    从Phase 4引擎的决策中提取信息，生成次日验证作业
    """

    def __init__(self, phase4_engine):
        """
        初始化作业生成器

        Args:
            phase4_engine: Phase4Engine实例
        """
        self.phase4 = phase4_engine

    def generate_from_day_trading(
        self,
        date: date,
        traded_symbols: List[str],
        market_data: Dict[str, Dict],
    ) -> Homework:
        """
        基于当日交易生成作业

        Args:
            date: 日期
            traded_symbols: 当日交易的标的列表
            market_data: 市场数据字典

        Returns:
            Homework: 生成的作业
        """
        homework = Homework(date=date)

        for symbol in traded_symbols:
            data = market_data.get(symbol, {})
            self._generate_for_symbol(homework, symbol, data)

        return homework

    def _generate_for_symbol(self, homework: Homework, symbol: str, data: Dict):
        """为单个标的生成作业"""

        # 1. 如果有买入信号，生成预测
        if data.get('buy_signal'):
            buy_price = data.get('buy_price', 0)
            buy_reason = data.get('buy_reason', '')

            # 预测：次日收盘价应该上涨
            expected_gain = self.phase4.validation_manager.target_gain
            expected_close = buy_price * (1 + expected_gain)

            homework.add_prediction(
                symbol=symbol,
                field='close',
                expected=expected_close,
                reasoning=f'买入信号: {buy_reason}，预期验证点达成({expected_gain:.1%})',
                confidence=data.get('buy_confidence', 0.6),
            )

            # 问题：成交量是否会放大？
            homework.add_question(
                symbol=symbol,
                question='次日是否会放量确认？',
                hypothesis=f'成交量需要达到今日的{self.phase4.min_volume_ratio}倍以上'
            )

        # 2. 如果有卖出信号，生成预测
        elif data.get('sell_signal'):
            sell_price = data.get('sell_price', 0)
            sell_reason = data.get('sell_reason', '')

            homework.add_prediction(
                symbol=symbol,
                field='close',
                expected=sell_price * 0.98,  # 预测跌2%
                reasoning=f'卖出信号: {sell_reason}，预期继续下跌',
                confidence=data.get('sell_confidence', 0.6),
            )

        # 3. 如果有验证点，生成相关问题
        if symbol in self.phase4.validation_manager.validation_points:
            vp = self.phase4.validation_manager.validation_points[symbol]

            if vp.status == 'pending':
                # 验证点尚未完成，预测明日结果
                homework.add_question(
                    symbol=symbol,
                    question=f'验证点能否达成？(目标{vp.target_price:.2f})',
                    hypothesis=f'需要在{vp.deadline.strftime("%H:%M")}前达到目标价'
                )

    def generate_from_validation_status(
        self,
        date: date,
        open_positions: Dict[str, Dict],
    ) -> Homework:
        """
        基于持仓验证状态生成作业

        Args:
            date: 日期
            open_positions: 持仓信息

        Returns:
            Homework: 生成的作业
        """
        homework = Homework(date=date)

        for symbol, pos in open_positions.items():
            # 检查验证点状态
            if symbol in self.phase4.validation_manager.validation_points:
                vp = self.phase4.validation_manager.validation_points[symbol]

                current_price = pos.get('current_price', 0)
                profit_pct = (current_price - vp.entry_price) / vp.entry_price

                # 根据盈亏生成不同问题
                if profit_pct > 0.05:
                    homework.add_question(
                        symbol=symbol,
                        question='盈利超过5%，是否继续持有？',
                        hypothesis='不跌破验证点目标价则继续持有'
                    )
                elif profit_pct < -0.02:
                    homework.add_question(
                        symbol=symbol,
                        question='亏损超过2%，是否止损？',
                        hypothesis='跌破验证点入场价则立即止损'
                    )

                # 预测次日验证点状态
                if vp.status == 'pending':
                    time_remaining = (vp.deadline - datetime.now()).total_seconds() / 60
                    if time_remaining > 0:
                        homework.add_prediction(
                            symbol=symbol,
                            field='validation_status',
                            expected='passed',  # 预测通过
                            reasoning=f'验证点剩余{time_remaining:.0f}分钟，预期达成',
                            confidence=0.5,
                        )

        return homework
