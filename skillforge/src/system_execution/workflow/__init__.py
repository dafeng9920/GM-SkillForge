"""
Workflow Layer - 工作流编排层 (PREPARATION ONLY)

> 只负责编排入口与流程连接，不负责裁决

模块结构:
- entry: 入口编排，接收外部请求并路由
- orchestration: 流程编排，连接各层组件
- connections: 与其他层的连接说明

职责边界:
✅ 负责: 入口路由、流程连接、状态传递
❌ 不负责: 治理裁决、业务逻辑、资源操作

证据要求:
- 文件路径: skillforge/src/system_execution/workflow/
- 职责文档: WORKFLOW_RESPONSIBILITIES.md
- 连接说明: CONNECTIONS.md
- 自检脚本: _self_check.py
"""

from .entry import WorkflowContext, WorkflowEntry
from .orchestration import StageResult, WorkflowOrchestrator

__all__ = [
    "WorkflowContext",
    "WorkflowEntry",
    "StageResult",
    "WorkflowOrchestrator",
]
