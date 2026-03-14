from __future__ import annotations

from typing import Any, Dict, List, Optional
from api.models.orchestration_models import (
    OrchestrationProjection,
    FiveStageViewModel,
    FiveStageItem,
    FiveStageId,
    FiveStageStatus,
    ThreeCardsViewModel,
    ThreeCard,
    ThreeCardKind,
    GateDecision
)

class ProjectionService:
    """
    Orchestration Projection Service - 编排投影服务
    
    Transforms raw n8n execution data into Five-Stage and Three-Card models.
    """

    @staticmethod
    def project_to_five_stage(
        run_id: str,
        execution_data: Dict[str, Any],
        evidence_ref: Optional[str] = None
    ) -> FiveStageViewModel:
        """Projects raw execution data to the Five-Stage model."""
        
        # 1. Trigger Stage
        trigger = FiveStageItem(
            id=FiveStageId.TRIGGER,
            title="Intent Triggered",
            status=FiveStageStatus.SUCCESS,
            summary=f"Intent '{execution_data.get('intent_id', 'unknown')}' identified from {execution_data.get('repo_url', 'N/A')}",
            refs=[execution_data.get('commit_sha')] if execution_data.get('commit_sha') else [],
            payload={
                "intent_id": execution_data.get("intent_id"),
                "repo_url": execution_data.get("repo_url"),
                "requester_id": execution_data.get("requester_id")
            }
        )

        # 2. Collect Stage
        collect_status = FiveStageStatus.IDLE
        collect_summary = "Waiting for source collection..."
        if "pack_details" in execution_data or "evidence_ref" in execution_data:
            collect_status = FiveStageStatus.SUCCESS
            collect_summary = "AuditPack discovery and source collection completed."
        
        collect = FiveStageItem(
            id=FiveStageId.COLLECT,
            title="Source Collection",
            status=collect_status,
            summary=collect_summary,
            refs=[execution_data.get("evidence_ref")] if execution_data.get("evidence_ref") else []
        )

        # 3. Process Stage
        process_status = FiveStageStatus.IDLE
        process_summary = "Processing and RAG analysis pending..."
        if "rag_results" in execution_data:
            process_status = FiveStageStatus.SUCCESS
            res_count = len(execution_data.get("rag_results", []))
            process_summary = f"RAG analysis completed with {res_count} relevant findings."
        
        process = FiveStageItem(
            id=FiveStageId.PROCESS,
            title="Knowledge Analysis",
            status=process_status,
            summary=process_summary,
            payload={"rag_count": len(execution_data.get("rag_results", []))} if "rag_results" in execution_data else None
        )

        # 4. Deliver Stage
        gate_decision = execution_data.get("gate_decision", "BLOCK")
        deliver_status = FiveStageStatus.IDLE
        deliver_summary = "Gate clearance pending..."
        
        if gate_decision == "ALLOW":
            deliver_status = FiveStageStatus.SUCCESS
            deliver_summary = "Gate cleared. Execution permitted."
        elif gate_decision == "REQUIRES_CHANGES":
            deliver_status = FiveStageStatus.BLOCKED
            deliver_summary = "Gate blocked. Changes required before execution."
        elif gate_decision == "DENY":
            deliver_status = FiveStageStatus.FAILED
            deliver_summary = "Gate denied. Execution forbidden."
            
        deliver = FiveStageItem(
            id=FiveStageId.DELIVER,
            title="Governance Delivery",
            status=deliver_status,
            summary=deliver_summary,
            payload={"gate_decision": gate_decision}
        )

        # 5. Report Stage
        report_status = FiveStageStatus.IDLE
        report_summary = "Waiting for final audit report..."
        if execution_data.get("release_allowed"):
            report_status = FiveStageStatus.SUCCESS
            report_summary = "Final report generated and archived."
            
        report = FiveStageItem(
            id=FiveStageId.REPORT,
            title="Audit Reporting",
            status=report_status,
            summary=report_summary
        )

        return FiveStageViewModel(
            run_id=run_id,
            evidence_ref=evidence_ref,
            stages=[trigger, collect, process, deliver, report]
        )

    @staticmethod
    def project_to_three_cards(
        run_id: str,
        five_stage: FiveStageViewModel,
        evidence_ref: Optional[str] = None
    ) -> ThreeCardsViewModel:
        """Projects Five-Stage data to Three-Card model."""
        
        # 1. Understanding Card
        trigger_stage = next(s for s in five_stage.stages if s.id == FiveStageId.TRIGGER)
        understanding = ThreeCard(
            kind=ThreeCardKind.UNDERSTANDING,
            title="Goal Understanding",
            bullets=[
                f"Targeting intent: {trigger_stage.payload.get('intent_id')}",
                f"Source: {trigger_stage.payload.get('repo_url')}"
            ],
            confidence=0.95
        )

        # 2. Plan Card
        process_stage = next(s for s in five_stage.stages if s.id == FiveStageId.PROCESS)
        plan_bullets = ["Orchestrating standard migration path"]
        if process_stage.status == FiveStageStatus.SUCCESS:
            plan_bullets.append(f"Incorporate findings from {process_stage.payload.get('rag_count')} knowledge points")
        
        plan = ThreeCard(
            kind=ThreeCardKind.PLAN,
            title="Execution Plan",
            bullets=plan_bullets
        )

        # 3. Execution Contract Card
        deliver_stage = next(s for s in five_stage.stages if s.id == FiveStageId.DELIVER)
        contract = ThreeCard(
            kind=ThreeCardKind.EXECUTION_CONTRACT,
            title="Governance Status",
            bullets=[
                f"Gate Decision: {deliver_stage.payload.get('gate_decision')}",
                "Compliance: VERIFIED" if deliver_stage.status == FiveStageStatus.SUCCESS else "Compliance: PENDING"
            ],
            refs=[evidence_ref] if evidence_ref else []
        )

        return ThreeCardsViewModel(
            run_id=run_id,
            evidence_ref=evidence_ref,
            cards=[understanding, plan, contract]
        )

    @classmethod
    def create_projection(
        cls,
        run_id: str,
        execution_data: Dict[str, Any],
        evidence_ref: Optional[str] = None,
        gate_decision: Optional[str] = None,
        release_allowed: Optional[bool] = None
    ) -> OrchestrationProjection:
        """Creates the full OrchestrationProjection."""
        
        five_stage = cls.project_to_five_stage(run_id, execution_data, evidence_ref)
        three_cards = cls.project_to_three_cards(run_id, five_stage, evidence_ref)
        
        decision = None
        if gate_decision:
            try:
                decision = GateDecision(gate_decision)
            except ValueError:
                pass

        return OrchestrationProjection(
            run_id=run_id,
            evidence_ref=evidence_ref,
            gate_decision=decision,
            release_allowed=release_allowed,
            five_stage=five_stage,
            three_cards=three_cards
        )
