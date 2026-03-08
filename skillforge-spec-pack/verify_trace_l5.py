
import sys
from skillforge.src.orchestration.engine import PipelineEngine

def verify_trace():
    engine = PipelineEngine()
    # Provide a fixed run_id to test G3 (Traceability)
    run_id = "test-run-l5-g3"
    
    # Register a mock node for 'intent_parse' to allow Path A to start
    class MockNode:
        node_id = "intent_parse"
        def validate_input(self, i): return []
        def execute(self, i): return {"intent": "test"}
        def validate_output(self, o): return []

    engine.register_node(MockNode())

    # Run pipeline in 'nl' mode
    result = engine.run({
        "mode": "nl",
        "natural_language": "test",
        "branch": "main",
        "options": {
            "target_environment": "python",
            "intended_use": "automation",
            "visibility": "private",
            "sandbox_mode": "moderate"
        }
    }, run_id=run_id)

    print(f"Status: {result.get('status')}")
    print(f"RunID (Output): {result.get('run_id')}")
    
    # Check trace events
    events = result.get('trace_events', [])
    if not events:
        print("ERROR: No trace events found!")
        sys.exit(1)
        
    first_event = events[0]
    print(f"TraceID (First Event): {first_event.get('trace_id')}")
    print(f"RunID (First Event): {first_event.get('run_id')}")

    # G3 Check: RunID matches
    if result.get('run_id') != run_id:
        print("FAIL: Output RunID mismatch")
        sys.exit(1)
    if first_event.get('run_id') != run_id:
        print("FAIL: Event RunID mismatch")
        sys.exit(1)
        
    print("G3 PASSED: run_id propagated correctly")

if __name__ == "__main__":
    verify_trace()
