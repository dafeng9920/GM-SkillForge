"""Fund Guard - 资金安全"""

from .guard import FundGuard

__all__ = ["FundGuard"]


class FundGuard:
    """资金守卫"""

    def __init__(self):
        self._vaults = {}
        self._transfers = []

    async def create_vault(self, vault_id, limits):
        """创建资金库"""
        self._vaults[vault_id] = {"balance": 0, "limits": limits}

    async def authorize_transfer(self, from_vault, to_vault, amount, approvals_needed):
        """授权资金划转"""
        if from_vault in self._vaults:
            vault = self._vaults[from_vault]
            if vault["balance"] >= amount and amount <= vault["limits"].get("max_transfer", float("inf")):
                return True
        return False

    async def execute_transfer(self, from_vault, to_vault, amount):
        """执行资金划转"""
        if await self.authorize_transfer(from_vault, to_vault, amount, 1):
            self._vaults[from_vault]["balance"] -= amount
            self._vaults[to_vault]["balance"] += amount
            self._transfers.append({"from": from_vault, "to": to_vault, "amount": amount})
            return True
        return False
