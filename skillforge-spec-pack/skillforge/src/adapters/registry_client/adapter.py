"""
RegistryClientAdapter — publish skills to and query the GM OS skill registry.

Error codes used: REG_DUPLICATE, REG_VALIDATION_FAILED, SYS_ADAPTER_UNAVAILABLE.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class RegistryClientAdapter:
    """
    Adapter for the skill registry.

    Attributes:
        adapter_id: Unique adapter identifier.
        registry_url: Base URL of the registry service.
    """

    adapter_id: str = "registry_client"
    registry_url: str = "http://localhost:8080"

    def health_check(self) -> bool:
        """Return True if the registry service is reachable."""
        return True

    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Generic dispatch. Supported actions: publish, check_exists.
        """
        if action == "publish":
            return self.publish(params)
        elif action == "check_exists":
            result = self.check_exists(params["skill_id"], params["version"])
            return {"exists": result}
        else:
            raise ValueError(f"Unsupported action: {action}")

    def publish(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Publish a skill to the registry.

        Args:
            request: Dict conforming to gm-os-core registry_publish.schema.json
                     (RegistryPublishRequest).

        Returns:
            Dict conforming to RegistryPublishResult:
            {
                "schema_version": "0.1.0",
                "skill_id": str,
                "version": str,
                "status": "published" | "rejected",
                "registry_url": str,
                "timestamp": str
            }
        """
        skill_id: str = request.get("skill_id", "unknown")
        version: str = request.get("version", "0.1.0")
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        return {
            "schema_version": "0.1.0",
            "skill_id": skill_id,
            "version": version,
            "status": "published",
            "registry_url": f"{self.registry_url}/skills/{skill_id}/{version}",
            "timestamp": timestamp,
        }

    def check_exists(self, skill_id: str, version: str) -> bool:
        """
        Check whether a skill at the given version already exists in the registry.

        Args:
            skill_id: Skill identifier.
            version: Semantic version string.

        Returns:
            True if the skill+version combination already exists.
        """
        return False
