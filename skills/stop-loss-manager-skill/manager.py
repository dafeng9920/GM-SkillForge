"""Stop Loss Manager - 止损管理"""

from .manager import StopLossManager

__all__ = ["StopLossManager"]


class StopLossManager:
    """止损管理器"""

    def __init__(self):
        self._stop_orders = {}

    async def set_stop_loss(self, position_id, stop_type, stop_price):
        """设置止损"""
        pass
