"""Monitoring Dashboard - 监控仪表盘"""

from .dashboard import MonitoringDashboard

__all__ = ["MonitoringDashboard"]


class MonitoringDashboard:
    """监控仪表盘"""

    def __init__(self):
        self._metrics = {}
        self._alerts = []

    async def get_real_time_data(self):
        """获取实时数据"""
        return {"pnl": 0, "positions": {}, "risk_metrics": {}}

    async def add_alert(self, alert):
        """添加告警"""
        self._alerts.append(alert)

    async def get_dashboard_data(self):
        """获取仪表盘数据"""
        return {
            "real_time": await self.get_real_time_data(),
            "alerts": self._alerts,
        }
