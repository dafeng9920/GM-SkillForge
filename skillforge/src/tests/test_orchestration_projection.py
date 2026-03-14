import sys
from pathlib import Path
import os

# Add src to sys.path to allow imports before they are parsed
src_path = str(Path(__file__).parent.parent)
sys.path.insert(0, src_path)

from api.models.orchestration_models import OrchestrationProjection
from orchestration.projection_service import ProjectionService

def test_projection_service():
    print("Testing ProjectionService...")
    
    execution_data = {
        "intent_id": "test_intent",
        "repo_url": "https://github.com/test/repo",
        "commit_sha": "abc123def456",
        "requester_id": "user_123",
        "gate_decision": "ALLOW",
        "rag_results": [
            {"id": "doc1", "score": 0.9},
            {"id": "doc2", "score": 0.8}
        ],
        "release_allowed": True
    }
    
    run_id = "RUN-TEST-001"
    evidence_ref = "EV-TEST-001"
    
    projection = ProjectionService.create_projection(
        run_id=run_id,
        execution_data=execution_data,
        evidence_ref=evidence_ref,
        gate_decision="ALLOW",
        release_allowed=True
    )
    
    assert projection.run_id == run_id
    assert projection.evidence_ref == evidence_ref
    assert len(projection.five_stage.stages) == 5
    assert len(projection.three_cards.cards) == 3
    
    print("ProjectionService test: PASS")
    
    # Verify stages
    trigger = projection.five_stage.stages[0]
    assert trigger.id == "trigger"
    assert trigger.status == "success"
    
    process = projection.five_stage.stages[2]
    assert process.id == "process"
    assert "2 relevant findings" in process.summary
    
    # Verify cards
    understanding = projection.three_cards.cards[0]
    assert understanding.kind == "understanding"
    assert "test_intent" in understanding.bullets[0]
    
    print("Stage and Card verification: PASS")

if __name__ == "__main__":
    try:
        test_projection_service()
    except Exception as e:
        print(f"Tests failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
