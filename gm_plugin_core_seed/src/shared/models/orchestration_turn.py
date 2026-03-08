"""
OrchestrationTurn v1 - C3 编排层核心数据结构

冻结规则：
- schema_version 必须为 "orch_turn_v1"
- 所有字段必须 deterministic（不依赖 LLM）
- 必须包含 policy_checks 和 evidence_refs（可审计）
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class IntentMap(BaseModel):
    """意图地图：用户诉求的结构化表达"""

    user_goal: str = Field(..., description="用户目标（一句话）")
    deliverable: Optional[str] = Field(None, description="交付物类型")
    constraints: List[str] = Field(default_factory=list, description="约束条件")
    risk_level: str = Field("medium", description="风险等级: low/medium/high")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="已收集的输入/回答")


class OptionWithTradeoff(BaseModel):
    """方案选项（快/稳/强）"""

    option_type: str = Field(..., description="fast/steady/power")
    label_zh: str = Field(..., description="中文标签")
    label_en: str = Field(..., description="英文标签")
    tradeoffs: List[str] = Field(..., description="权衡点列表")
    estimated_time: Optional[str] = Field(None, description="预估时长")


class MinimalConfirmation(BaseModel):
    """最小确认集（<=2 个关键缺口问题）"""

    questions: List[Dict[str, Any]] = Field(..., description="缺口问题列表")
    # 每个 question 包含: {key, text_zh, text_en, why_critical, options}


@dataclass
class ThreeCardsData:
    """C3 三卡数据结构"""
    intent_map: Optional[Dict[str, Any]] = None  # 理解卡
    options_with_tradeoffs: Optional[List[Dict[str, Any]]] = None  # 方案卡
    minimal_confirmation: Optional[Dict[str, Any]] = None  # 执行契约卡
    next_action: str = "ask_user"  # ask_user/commit_ready/execute/refuse


class PolicyCheck(BaseModel):
    """治理检查点"""

    check_type: str = Field(..., description="NO_SECRETS_LEAK/FAIL_CLOSED/HITL_REQUIRED/POLICY_DECISION_DRIFT")
    passed: bool = Field(..., description="是否通过")
    reason: Optional[str] = Field(None, description="未通过原因")
    status: Optional[str] = Field(None, description="状态: error/warn/info")
    message: Optional[str] = Field(None, description="详细消息")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")


class OrchestrationTurn(BaseModel):
    """
    OrchestrationTurn v1 - 单轮编排数据

    每次用户输入产生一个 Turn，包含：
    - Level 升阶信息
    - Intent Map（意图地图）
    - 快/稳/强三方案
    - 最小确认集（<=2 个关键缺口问题）
    - 治理检查点
    - 证据引用
    """

    # 元数据
    schema_version: Literal["orch_turn_v1"] = "orch_turn_v1"
    session_id: str = Field(..., description="会话 ID")
    turn_id: str = Field(..., description="轮次 ID")
    ts: datetime = Field(default_factory=datetime.utcnow, description="时间戳")

    # 用户输入
    user_message: str = Field(..., description="用户原始输入")
    assistant_message: Optional[str] = Field(None, description="助手回复消息")

    # Level 升阶
    level_before: int = Field(..., ge=1, le=10, description="升阶前 Level")
    level_after: int = Field(..., ge=1, le=10, description="升阶后 Level")
    level_step: int = Field(..., ge=0, le=2, description="升阶步长（0、1 或 2）")
    why_level_up: str = Field(..., description="升阶理由（deterministic）")
    why_this_question: Optional[str] = Field(None, description="为何问这个问题")

    # 降维打击三连
    intent_map: IntentMap = Field(
        ...,
        description=(
            "意图地图 (DEPRECATED: Spec v2 迁移期由投影填充，不再作为权威源)"
        ),
    )
    options_with_tradeoffs: List[OptionWithTradeoff] = Field(
        ...,
        min_items=3,
        max_items=3,
        description="快/稳/强三方案",
    )
    minimal_confirmation: MinimalConfirmation = Field(..., description="最小确认集")
    three_cards: Optional[ThreeCardsData] = Field(
        default=None,
        description="三卡数据 (intent_map/options_with_tradeoffs/minimal_confirmation)",
    )

    # 治理与证据
    policy_checks: List[PolicyCheck] = Field(..., description="治理检查点")
    evidence_refs: List[str] = Field(..., description="证据引用列表")

    # 下一步动作
    next_action: str = Field(..., description="ask_user/execute/refuse/end_session")

    # 可选：artifact delta（STEP 3 补充）
    artifact_delta: Optional[Dict[str, Any]] = Field(
        None, description="产物增量"
    )

    # ===== Spec v2 引用字段（新增） =====
    spec_id: Optional[str] = Field(
        default=None,
        description="关联的 OrchestrationSpec ID (Spec v2)",
    )
    spec_version: Optional[int] = Field(
        default=None,
        description="Spec 版本号 (Spec v2)",
    )
    spec_hash: Optional[str] = Field(
        default=None,
        description="Spec 稳定哈希 (Spec v2)",
    )
    decision_hash_struct: Optional[str] = Field(
        default=None,
        description="决策输出结构哈希 (仅结构字段，用于 drift 检测)",
    )

    domain: Optional[str] = Field(
        None,
        description="领域分类: writing/etl/ops/unknown"
    )
    commit_boundary: Optional[Dict[str, Any]] = Field(
        None,
        description=(
            "提交边界: {ready: bool, reason: str, required_keys: list, "
            "side_effects: list|dict, preflight_id: str|null, contract_hash: str|null, "
            "gate_snapshot_hash: str|null, ticket: str|null}"
        )
    )
    cognition: Optional[Dict[str, Any]] = Field(
        None,
        description="认知深度控制器输出: {depth_target, render_plan, scores, layers}"
    )
    control: Optional[Dict[str, Any]] = Field(
        None,
        description=(
            "控制面投影 (Phase 0 止血): meta.control_plane 的兼容投影，"
            "包含 intent_map, cognition, options_with_tradeoffs, assumption_ledger, "
            "draft_deliverable, chips, baton_progress 等字段"
        )
    )


def create_initial_turn(
    session_id: str,
    user_message: str,
    spec_id: Optional[str] = None,
    spec_version: Optional[int] = None,
    spec_hash: Optional[str] = None,
) -> OrchestrationTurn:
    """创建初始 Turn（level_before=1）"""
    return OrchestrationTurn(
        session_id=session_id,
        turn_id=f"{session_id}-T1",
        user_message=user_message,
        level_before=1,
        level_after=1,
        level_step=1,
        why_level_up="初始状态",
        intent_map=IntentMap(user_goal="待分析"),
        options_with_tradeoffs=[
            OptionWithTradeoff(
                option_type="fast",
                label_zh="快速方案",
                label_en="Fast",
                tradeoffs=["待生成"],
            ),
            OptionWithTradeoff(
                option_type="steady",
                label_zh="稳健方案",
                label_en="Steady",
                tradeoffs=["待生成"],
            ),
            OptionWithTradeoff(
                option_type="power",
                label_zh="强力方案",
                label_en="Power",
                tradeoffs=["待生成"],
            ),
        ],
        minimal_confirmation=MinimalConfirmation(questions=[]),
        policy_checks=[],
        evidence_refs=[],
        next_action="ask_user",
        spec_id=spec_id,
        spec_version=spec_version,
        spec_hash=spec_hash,
    )
