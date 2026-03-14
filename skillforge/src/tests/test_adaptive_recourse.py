import sys
from pathlib import Path
import asyncio
import json

# Add src to sys.path
src_path = str(Path(__file__).parent.parent)
sys.path.insert(0, src_path)

from api.routes.n8n_orchestration import handle_sos, N8NSOSRequest

async def verify_sos_mechanism():
    print("\n" + "="*50)
    print("VERIFYING ADAPTIVE RECOURSE (SOS)")
    print("="*50)

    # 1. Simulate a Timeout Error from n8n
    timeout_request = N8NSOSRequest(
        run_id="RUN-N8N-TEST-001",
        skill_spec_name="reddit_scraper",
        error_context={
            "node": "HTTP Request (network)",
            "message": "Error: 408 Request Timeout"
        }
    )

    print("\nScenario 1: Timeout Error")
    res1 = await handle_sos(timeout_request)
    projection1 = res1.orchestration_projection
    print(f"SOS Status: {projection1.sos_event.status}")
    print(f"Diagnosis: {projection1.sos_event.rationale}")
    print(f"Suggested Action: {projection1.sos_event.suggested_action}")
    
    assert projection1.sos_event.suggested_action == "retry_with_params"

    # 2. Simulate an Unknown Error requiring Human Intervention
    human_request = N8NSOSRequest(
        run_id="RUN-N8N-TEST-002",
        skill_spec_name="reddit_scraper",
        error_context={
            "node": "Data Parser",
            "message": "Critical: Unexpected field structure in JSON response"
        }
    )

    print("\nScenario 2: Unknown Error (Human Intervention)")
    res2 = await handle_sos(human_request)
    projection2 = res2.orchestration_projection
    print(f"SOS Status: {projection2.sos_event.status}")
    print(f"Diagnosis: {projection2.sos_event.rationale}")
    print(f"Instructions: {projection2.sos_event.instructions}")

    assert projection2.sos_event.suggested_action == "human_intervention"

    print("\n" + "="*50)
    print("ADAPTIVE RECOURSE VERIFICATION COMPLETE")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(verify_sos_mechanism())
