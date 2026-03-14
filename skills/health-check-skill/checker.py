"""Health Check - 系统健康检查"""

from .checker import HealthChecker, HealthStatus

__all__ = ["HealthChecker", "HealthStatus"]


class HealthStatus:
    """健康状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthChecker:
    """健康检查器"""

    def __init__(self):
        self._components = {}
        self._dependencies = {}

    def register_component(self, name, check_func):
        """注册组件"""
        self._components[name] = check_func

    def add_dependency(self, component, depends_on):
        """添加依赖关系"""
        if component not in self._dependencies:
            self._dependencies[component] = []
        self._dependencies[component].extend(depends_on)

    async def check_component(self, name):
        """检查单个组件"""
        if name in self._components:
            return await self._components[name]()
        return HealthStatus.UNHEALTHY

    async def check_all(self):
        """检查所有组件"""
        results = {}
        for name in self._components:
            results[name] = await self.check_component(name)
        return results

    async def get_system_health(self):
        """获取系统整体健康状态"""
        component_status = await self.check_all()

        if all(s == HealthStatus.HEALTHY for s in component_status.values()):
            return HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in component_status.values()):
            return HealthStatus.UNHEALTHY
        else:
            return HealthStatus.DEGRADED
