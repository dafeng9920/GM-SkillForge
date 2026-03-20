"""
Integration Gateway Module

SkillForge 与外部系统之间的纯连接层。
只做触发、路由、搬运、连接，绝不裁决。

阶段: 准备阶段 - 只定义骨架，不进入 runtime
"""

from .gateway_interface import GatewayInterface
from .router import Router
from .trigger import Trigger
from .transporter import Transporter

__all__ = [
    "GatewayInterface",
    "Router",
    "Trigger",
    "Transporter",
]
