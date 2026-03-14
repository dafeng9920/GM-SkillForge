"""Anomaly Detector - 异常检测"""

from .detector import AnomalyDetector

__all__ = ["AnomalyDetector"]


class AnomalyDetector:
    """异常检测器"""

    def __init__(self):
        self._thresholds = {}
        self._models = {}

    async def detect_price_anomaly(self, symbol, current_price, history):
        """检测价格异常"""
        return False

    async def detect_volume_anomaly(self, symbol, current_volume, history):
        """检测成交量异常"""
        return False

    async def detect_behavior_anomaly(self, user_id, action):
        """检测行为异常"""
        return False
