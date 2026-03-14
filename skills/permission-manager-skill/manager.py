"""Permission Manager - 权限管理"""

from .manager import PermissionManager, Role, Permission

__all__ = ["PermissionManager", "Role", "Permission"]


class Permission:
    """权限"""
    def __init__(self, name, resource):
        self.name = name
        self.resource = resource


class Role:
    """角色"""
    def __init__(self, name, permissions):
        self.name = name
        self.permissions = permissions


class PermissionManager:
    """权限管理器"""

    def __init__(self):
        self._roles = {}
        self._user_roles = {}

    def create_role(self, name, permissions):
        """创建角色"""
        self._roles[name] = Role(name, permissions)

    def assign_role(self, user_id, role_name):
        """分配角色"""
        if user_id not in self._user_roles:
            self._user_roles[user_id] = []
        self._user_roles[user_id].append(role_name)

    def check_permission(self, user_id, permission_name, resource):
        """检查权限"""
        if user_id not in self._user_roles:
            return False

        for role_name in self._user_roles[user_id]:
            role = self._roles.get(role_name)
            if role:
                for perm in role.permissions:
                    if perm.name == permission_name and perm.resource == resource:
                        return True

        return False
