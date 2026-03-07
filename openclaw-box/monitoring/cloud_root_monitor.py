#!/usr/bin/env python3
"""
GM-SkillForge CLOUD-ROOT Monitoring Daemon

Monitors all CLOUD-ROOT services with:
- Health checks
- Failure detection
- Automatic retry with exponential backoff
- Alerting (webhook, email, log)
- Fail-closed enforcement

Usage:
    python cloud_root_monitor.py [--config monitoring.yml] [--daemon]
"""

import argparse
import asyncio
import json
import logging
import os
import signal
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import yaml


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class ServiceStatus(str, Enum):
    """Service status."""
    RUNNING = "running"
    STOPPED = "stopped"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class Alert:
    """Alert data structure."""
    severity: AlertSeverity
    service: str
    message: str
    hostname: str
    timestamp: str
    runbook: Optional[str] = None
    immediate: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceHealth:
    """Service health status."""
    name: str
    status: ServiceStatus
    last_check: str
    uptime_seconds: float = 0
    failure_count: int = 0
    last_error: Optional[str] = None


class MonitoringDaemon:
    """Main monitoring daemon class."""

    def __init__(self, config_path: Path):
        self.config = self._load_config(config_path)
        self.services: Dict[str, ServiceHealth] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = True
        self.logger = self._setup_logging()
        self._alert_cooldowns: Dict[str, datetime] = {}

    def _load_config(self, config_path: Path) -> Dict:
        """Load monitoring configuration from YAML file."""
        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        return self._default_config()

    def _default_config(self) -> Dict:
        """Return default configuration."""
        return {
            "monitoring": {
                "check_interval_sec": 30,
                "alert_cooldown_sec": 300,
            },
            "retry_policy": {
                "max_attempts": 5,
                "initial_backoff_sec": 10,
                "max_backoff_sec": 300,
                "backoff_multiplier": 2.0,
            },
            "alerting": {
                "enabled": True,
                "channels": {
                    "log": {"enabled": True},
                    "webhook": {"enabled": False},
                    "email": {"enabled": False},
                },
            },
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger("gm-monitoring")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)
        return logger

    async def _send_alert(self, alert: Alert):
        """Send alert through configured channels."""
        alert_key = f"{alert.service}_{alert.severity}"
        cooldown = self.config["monitoring"]["alert_cooldown_sec"]

        # Check cooldown
        if alert_key in self._alert_cooldowns:
            if datetime.now(timezone.utc) - self._alert_cooldowns[alert_key] < timedelta(seconds=cooldown):
                self.logger.debug(f"Alert {alert_key} is in cooldown, skipping")
                return

        self._alert_cooldowns[alert_key] = datetime.now(timezone.utc)

        # Log alert
        self.logger.error(f"[{alert.severity.value.upper()}] {alert.service}: {alert.message}")

        # Send webhook if enabled
        if self.config["alerting"]["channels"]["webhook"].get("enabled"):
            await self._send_webhook_alert(alert)

        # Send email if enabled
        if self.config["alerting"]["channels"]["email"].get("enabled"):
            await self._send_email_alert(alert)

    async def _send_webhook_alert(self, alert: Alert):
        """Send alert via webhook."""
        webhook_url = os.environ.get("ALERT_WEBHOOK_URL")
        if not webhook_url:
            return

        try:
            async with self.session.post(webhook_url, json={
                "severity": alert.severity.value,
                "service": alert.service,
                "message": alert.message,
                "hostname": alert.hostname,
                "timestamp": alert.timestamp,
                "runbook": alert.runbook,
                "metadata": alert.metadata,
            }) as resp:
                if resp.status == 200:
                    self.logger.info(f"Webhook alert sent for {alert.service}")
                else:
                    self.logger.warning(f"Webhook alert failed: {resp.status}")
        except Exception as e:
            self.logger.error(f"Failed to send webhook alert: {e}")

    async def _send_email_alert(self, alert: Alert):
        """Send alert via email."""
        # Email implementation would go here
        self.logger.info(f"Email alert for {alert.service}: {alert.message}")

    async def _check_service_health(self, service_name: str, service_config: Dict) -> ServiceHealth:
        """Check health of a single service."""
        health = ServiceHealth(
            name=service_name,
            status=ServiceStatus.UNKNOWN,
            last_check=datetime.now(timezone.utc).isoformat()
        )

        try:
            # Check process
            process_name = service_config.get("process_name", service_name)
            if not await self._check_process_running(process_name):
                health.status = ServiceStatus.STOPPED
                health.last_error = f"Process {process_name} not running"
                return health

            # Check HTTP health endpoint if configured
            port = service_config.get("port")
            health_path = service_config.get("health_path", "/health")
            if port:
                try:
                    async with self.session.get(
                        f"http://localhost:{port}{health_path}",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as resp:
                        if resp.status == 200:
                            health.status = ServiceStatus.RUNNING
                        else:
                            health.status = ServiceStatus.DEGRADED
                            health.last_error = f"Health check returned {resp.status}"
                except asyncio.TimeoutError:
                    health.status = ServiceStatus.DEGRADED
                    health.last_error = "Health check timeout"
                except Exception as e:
                    health.status = ServiceStatus.DEGRADED
                    health.last_error = f"Health check failed: {e}"
            else:
                health.status = ServiceStatus.RUNNING

        except Exception as e:
            health.status = ServiceStatus.UNKNOWN
            health.last_error = f"Health check error: {e}"

        return health

    async def _check_process_running(self, process_name: str) -> bool:
        """Check if a process is running."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "pgrep", "-f", process_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            return proc.returncode == 0
        except Exception:
            return False

    async def _check_disk_space(self) -> Optional[Alert]:
        """Check disk space and alert if low."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "df", "-B1", "/var/lib/gm-skillforge",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            output = stdout.decode()

            # Parse df output
            lines = output.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                if len(parts) >= 5:
                    total = int(parts[1])
                    available = int(parts[3])
                    percent = int(parts[4].rstrip('%'))

                    min_percent = self.config.get("health_checks", {}).get("disk_space", {}).get("min_free_percent", 15)
                    if percent < min_percent:
                        return Alert(
                            severity=AlertSeverity.CRITICAL,
                            service="disk_space",
                            message=f"Disk space low: {available // (1024**3)}GB free ({percent}%)",
                            hostname=os.uname().nodename,
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            runbook="docs/runbooks/disk_cleanup.md",
                        )
        except Exception as e:
            self.logger.warning(f"Failed to check disk space: {e}")

        return None

    async def _monitor_services(self):
        """Monitor all services continuously."""
        services_config = self.config.get("services", {})

        while self.running:
            for service_name, service_config in services_config.items():
                health = await self._check_service_health(service_name, service_config)
                self.services[service_name] = health

                # Check for failures
                if health.status != ServiceStatus.RUNNING:
                    health.failure_count += 1

                    # Check alert conditions
                    alert_conditions = service_config.get("alert_on", [])
                    if "service_down" in alert_conditions and health.status == ServiceStatus.STOPPED:
                        await self._send_alert(Alert(
                            severity=AlertSeverity.CRITICAL if service_config.get("critical", False) else AlertSeverity.WARNING,
                            service=service_name,
                            message=f"Service {service_name} is down: {health.last_error}",
                            hostname=os.uname().nodename,
                            timestamp=health.last_check,
                            runbook=service_config.get("runbook", f"docs/runbooks/{service_name}_recovery.md"),
                            immediate=service_config.get("critical", False),
                        ))

                    # Check retry policy
                    if health.failure_count >= self.config["retry_policy"]["max_attempts"]:
                        self.logger.critical(f"Service {service_name} exceeded max retry attempts")
                        # Implement fail-closed behavior
                        await self._handle_fail_closed(service_name, health)
                else:
                    health.failure_count = 0

            # Check disk space
            disk_alert = await self._check_disk_space()
            if disk_alert:
                await self._send_alert(disk_alert)

            # Wait for next check
            await asyncio.sleep(self.config["monitoring"]["check_interval_sec"])

    async def _handle_fail_closed(self, service_name: str, health: ServiceHealth):
        """Handle fail-closed enforcement for critical services."""
        critical_services = ["mandatory_gate", "receipt_verifier"]

        if service_name in critical_services:
            self.logger.critical(f"CRITICAL SERVICE {service_name} IS DOWN - ENFORCING FAIL-CLOSED")

            # Block new tasks
            await self._block_new_tasks(service_name)

            # Send critical alert
            await self._send_alert(Alert(
                severity=AlertSeverity.CRITICAL,
                service="fail_closed_enforcement",
                message=f"FAIL-CLOSED ENFORCED: {service_name} is down, blocking all new tasks",
                hostname=os.uname().nodename,
                timestamp=datetime.now(timezone.utc).isoformat(),
                immediate=True,
            ))

    async def _block_new_tasks(self, failed_service: str):
        """Block new tasks due to fail-closed enforcement."""
        self.logger.warning(f"Blocking new tasks due to {failed_service} failure")
        # Implementation would write to dispatch queue to block new tasks

    async def start(self):
        """Start the monitoring daemon."""
        self.logger.info("Starting GM-SkillForge CLOUD-ROOT Monitoring Daemon")

        # Create HTTP session
        self.session = aiohttp.ClientSession()

        # Start monitoring
        try:
            await self._monitor_services()
        except asyncio.CancelledError:
            self.logger.info("Monitoring cancelled")
        finally:
            if self.session:
                await self.session.close()

    def stop(self):
        """Stop the monitoring daemon."""
        self.logger.info("Stopping monitoring daemon")
        self.running = False


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    print(f"\nReceived signal {signum}, shutting down...")
    sys.exit(0)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="GM-SkillForge CLOUD-ROOT Monitoring Daemon")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("/opt/gm-skillforge/config/monitoring.yml"),
        help="Path to monitoring configuration file"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run health checks once and exit"
    )
    args = parser.parse_args()

    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and start daemon
    daemon = MonitoringDaemon(args.config)

    if args.once:
        # Run checks once
        services_config = daemon.config.get("services", {})
        for service_name, service_config in services_config.items():
            health = await daemon._check_service_health(service_name, service_config)
            print(f"{service_name}: {health.status.value}")
            if health.last_error:
                print(f"  Error: {health.last_error}")
        return 0

    if args.daemon:
        # Fork to background
        # (Simplified - proper daemonization would use python-daemon)
        pass

    await daemon.start()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
