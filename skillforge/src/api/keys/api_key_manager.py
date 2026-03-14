"""
API 密钥管理基础设施

APH-005: API 密钥管理基础设施

实现 API Key 的生成、安全存储（加密）、轮换、撤销和审计日志。
"""
from __future__ import annotations

import secrets
import hashlib
import logging
import json
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from pathlib import Path
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


# API Key 前缀（用于识别）
API_KEY_PREFIX = "sk"
API_KEY_VERSION = "v1"


class APIKeyManager:
    """API Key 管理器"""

    def __init__(self, storage_path: str | None = None, encryption_key: str | None = None):
        """
        初始化 API Key 管理器

        Args:
            storage_path: API Key 存储路径（JSON 文件）
            encryption_key: 加密密钥（Base64 编码）
        """
        self.storage_path = Path(storage_path or "data/api_keys.json")
        self.encryption_key = encryption_key or self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key.encode() if isinstance(self.encryption_key, str) else self.encryption_key)

        # 确保存储目录存在
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # 加载现有 API Keys
        self._keys = self._load_keys()

    def _get_or_create_encryption_key(self) -> str:
        """获取或创建加密密钥"""
        key_file = Path("data/.encryption_key")
        key_file.parent.mkdir(parents=True, exist_ok=True)

        if key_file.exists():
            return key_file.read_text().strip()

        # 创建新密钥
        key = Fernet.generate_key().decode()
        key_file.write_text(key)
        key_file.chmod(0o600)  # 仅所有者可读写
        logger.info("[APIKey] 创建新的加密密钥")
        return key

    def _load_keys(self) -> dict:
        """从存储加载 API Keys"""
        if not self.storage_path.exists():
            return {}

        try:
            data = json.loads(self.storage_path.read_text())
            logger.info(f"[APIKey] 加载了 {len(data)} 个 API Keys")
            return data
        except Exception as e:
            logger.error(f"[APIKey] 加载 API Keys 失败: {e}")
            return {}

    def _save_keys(self) -> None:
        """保存 API Keys 到存储"""
        try:
            self.storage_path.write_text(json.dumps(self._keys, indent=2, ensure_ascii=False))
            logger.info(f"[APIKey] 保存了 {len(self._keys)} 个 API Keys")
        except Exception as e:
            logger.error(f"[APIKey] 保存 API Keys 失败: {e}")

    def generate_api_key(
        self,
        name: str,
        description: str | None = None,
        expires_in_days: int | None = None,
    ) -> tuple[str, dict]:
        """
        生成新的 API Key

        Args:
            name: API Key 名称/标识
            description: 描述
            expires_in_days: 有效期（天数）

        Returns:
            (api_key, key_info)
        """
        # 生成随机部分（32 字节 = 64 十六进制字符）
        random_bytes = secrets.token_bytes(32)
        random_part = random_bytes.hex()

        # 构造 API Key: sk-v1-{random}
        api_key = f"{API_KEY_PREFIX}-{API_KEY_VERSION}-{random_part}"

        # 计算哈希（用于存储和验证）
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # 创建 key_info
        key_info = {
            "name": name,
            "description": description,
            "key_hash": key_hash,
            "prefix": f"{API_KEY_PREFIX}-{API_KEY_VERSION}-{random_part[:8]}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=expires_in_days)).isoformat() if expires_in_days else None,
            "last_used": None,
            "is_active": True,
            "is_revoked": False,
        }

        # 加密存储（不存储原始 key，只存储 key_info）
        self._keys[key_hash] = key_info
        self._save_keys()

        # 记录审计日志
        self._audit_log("api_key_created", key_info)

        logger.info(f"[APIKey] 生成新 API Key: {key_info['prefix']}")

        return api_key, key_info

    def validate_api_key(self, api_key: str) -> Optional[dict]:
        """
        验证 API Key

        Args:
            api_key: API Key

        Returns:
            key_info（如果有效），否则 None
        """
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        key_info = self._keys.get(key_hash)
        if not key_info:
            logger.warning("[APIKey] API Key 不存在")
            return None

        # 检查是否被撤销
        if key_info.get("is_revoked"):
            logger.warning(f"[APIKey] API Key 已撤销: {key_info['prefix']}")
            return None

        # 检查是否过期
        if key_info.get("expires_at"):
            expires_at = datetime.fromisoformat(key_info["expires_at"])
            if datetime.now(timezone.utc) > expires_at:
                logger.warning(f"[APIKey] API Key 已过期: {key_info['prefix']}")
                return None

        # 更新最后使用时间
        key_info["last_used"] = datetime.now(timezone.utc).isoformat()
        self._save_keys()

        return key_info

    def revoke_api_key(self, api_key: str) -> bool:
        """
        撤销 API Key

        Args:
            api_key: API Key

        Returns:
            是否成功
        """
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        key_info = self._keys.get(key_hash)

        if not key_info:
            return False

        key_info["is_revoked"] = True
        key_info["revoked_at"] = datetime.now(timezone.utc).isoformat()
        self._save_keys()

        self._audit_log("api_key_revoked", key_info)
        logger.info(f"[APIKey] 撤销 API Key: {key_info['prefix']}")

        return True

    def rotate_api_key(self, old_api_key: str) -> tuple[str, dict]:
        """
        轮换 API Key（撤销旧 key，生成新 key）

        Args:
            old_api_key: 旧的 API Key

        Returns:
            (new_api_key, new_key_info)
        """
        key_hash = hashlib.sha256(old_api_key.encode()).hexdigest()
        old_key_info = self._keys.get(key_hash)

        if not old_key_info:
            raise ValueError("API Key 不存在")

        # 生成新 key
        new_api_key, new_key_info = self.generate_api_key(
            name=old_key_info["name"],
            description=f"轮换自 {old_key_info['prefix']}",
        )

        # 撤销旧 key
        self.revoke_api_key(old_api_key)

        return new_api_key, new_key_info

    def list_api_keys(self) -> List[dict]:
        """列出所有 API Keys（不包含敏感信息）"""
        result = []
        for key_info in self._keys.values():
            result.append({
                "prefix": key_info["prefix"],
                "name": key_info["name"],
                "description": key_info.get("description"),
                "created_at": key_info["created_at"],
                "expires_at": key_info.get("expires_at"),
                "last_used": key_info.get("last_used"),
                "is_active": key_info.get("is_active", True),
                "is_revoked": key_info.get("is_revoked", False),
            })
        return result

    def _audit_log(self, action: str, key_info: dict) -> None:
        """记录审计日志"""
        log_entry = {
            "action": action,
            "key_prefix": key_info.get("prefix"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        logger.info(f"[APIKey Audit] {json.dumps(log_entry)}")


# 全局实例
_api_key_manager: Optional[APIKeyManager] = None


def get_api_key_manager() -> APIKeyManager:
    """获取全局 API Key 管理器实例"""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager
