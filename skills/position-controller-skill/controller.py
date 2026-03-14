"""Position Controller - 仓位控制"""

from .controller import PositionController

__all__ = ["PositionController"]


class PositionController:
    """仓位控制器"""

    def __init__(self):
        self._position_limits = {}

    async def calculate_position_size(self, signal, portfolio, risk_params):
        """计算仓位大小"""
        return 0
