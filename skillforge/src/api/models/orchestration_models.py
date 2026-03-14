from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional, Dict
from pydantic import BaseModel, Field

class GateDecision(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    DENY = "DENY"
    REQUIRES_CHANGES = "REQUIRES_CHANGES"

class FiveStageId(str, Enum):
    TRIGGER = "trigger"
    COLLECT = "collect"
    PROCESS = "process"
    DELIVER = "deliver"
    REPORT = "report"

class FiveStageStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"

class FiveStageItem(BaseModel):
    id: FiveStageId
    title: str
    status: FiveStageStatus
    summary: str
    refs: List[str] = Field(default_factory=list)
    payload: Optional[Dict[str, Any]] = None

class FiveStageViewModel(BaseModel):
    run_id: str
    evidence_ref: Optional[str] = None
    stages: List[FiveStageItem]

class ThreeCardKind(str, Enum):
    UNDERSTANDING = "understanding"
    PLAN = "plan"
    EXECUTION_CONTRACT = "execution_contract"

class ThreeCard(BaseModel):
    kind: ThreeCardKind
    title: str
    bullets: List[str]
    confidence: Optional[float] = None
    refs: List[str] = Field(default_factory=list)
    payload: Optional[Dict[str, Any]] = None

class ThreeCardsViewModel(BaseModel):
    run_id: str
    evidence_ref: Optional[str] = None
    cards: List[ThreeCard]

class SOSEvent(BaseModel):
    id: str
    status: str  # 'help_needed' | 'brain_planning' | 'resolved'
    node_name: str
    error_message: str
    rationale: Optional[str] = None
    suggested_action: Optional[str] = None  # 'retry_with_params' | 'human_intervention' | 'fallback_path'
    instructions: Optional[str] = None

class OrchestrationProjection(BaseModel):
    run_id: str
    evidence_ref: Optional[str] = None
    gate_decision: Optional[GateDecision] = None
    release_allowed: Optional[bool] = None
    sos_event: Optional[SOSEvent] = None
    five_stage: FiveStageViewModel
    three_cards: ThreeCardsViewModel
