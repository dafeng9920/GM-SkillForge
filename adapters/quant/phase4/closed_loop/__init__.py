"""
Phase 4 双向验证闭环系统

将盘中实时系统与盘后复盘验证结合，形成完整的迭代闭环。

核心概念：
1. 盘中：Phase 4 引擎决策
2. 盘后：生成预测作业
3. T+1：市场批改作业
4. 分析：找出错误规律
5. 迭代：优化系统参数
"""

from .homework import HomeworkGenerator
from .grader import HomeworkGrader
from .analyzer import MistakeAnalyzer
from .iterator import SystemIterator
from .closed_loop import DailyClosedLoop

__all__ = [
    'HomeworkGenerator',
    'HomeworkGrader',
    'MistakeAnalyzer',
    'SystemIterator',
    'DailyClosedLoop',
]
