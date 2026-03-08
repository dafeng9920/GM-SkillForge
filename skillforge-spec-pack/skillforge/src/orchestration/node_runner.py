"""
NodeRunner — single-node executor with trace, timeout, and retry.

Execution sequence
------------------
1. Load node schema → validate input via handler.validate_input()
2. Call handler.execute(input_data)
3. Validate output via handler.validate_output()
4. Emit trace_event(s): node_start, node_complete or node_error
5. Timeout governed by pipeline_v0.yml settings
6. Retry governed by error_policy.yml settings

L5 G3/G4 requirements:
- run_id is propagated through all trace events for traceability
- trace_id is deterministic when run_id is provided (seeded generation)
"""
from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass
from typing import Any

from skillforge.src.protocols import NodeHandler


@dataclass
class NodeRunner:
    """
    Single-node execution wrapper.

    Attributes:
        default_timeout_seconds: Fallback timeout if pipeline_v0.yml has no entry.
        max_retries: Fallback max retries if error_policy.yml has no entry.
        retry_delay_seconds: Base delay between retries (exponential back-off).
    """

    default_timeout_seconds: int = 300
    max_retries: int = 2
    retry_delay_seconds: float = 1.0

    def run(
        self,
        handler: NodeHandler,
        input_data: dict[str, Any],
        *,
        timeout_seconds: int | None = None,
        max_retries: int | None = None,
        run_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute a single node with validation, tracing, timeout and retry.

        Args:
            handler: The NodeHandler to run.
            input_data: Pre-validated input payload.
            timeout_seconds: Override timeout.
            max_retries: Override max retries.
            run_id: Optional run identifier for L5 G3 traceability.

        Returns:
            Dict with keys:
            {
                "node_id": str,
                "run_id": str | None,    # L5 G3: included if provided
                "output": dict,          # handler output
                "trace_events": [dict],   # list of TraceEvent dicts
                "duration_ms": int,
                "retries_used": int
            }

        Raises:
            ValueError: If input validation fails.
            RuntimeError: If output validation fails or execution errors exhaust retries.
        """
        effective_timeout = (
            timeout_seconds if timeout_seconds is not None
            else self.default_timeout_seconds
        )
        effective_max_retries = (
            max_retries if max_retries is not None
            else self.max_retries
        )

        node_id: str = handler.node_id
        trace_events: list[dict[str, Any]] = []
        run_start = time.time()
        trace_counter = 0

        # ── start trace ───────────────────────────────────────────
        trace_events.append(
            self._make_trace_event(
                run_id=run_id,
                trace_counter=trace_counter,
                node_id=node_id,
                event_type="start",
            )
        )
        trace_counter += 1

        # ── validate input ────────────────────────────────────────
        try:
            handler.validate_input(input_data)
        except Exception as val_exc:
            trace_events.append(
                self._make_trace_event(
                    run_id=run_id,
                    trace_counter=trace_counter,
                    node_id=node_id,
                    event_type="error",
                    detail={"error": f"EXEC_VALIDATION_FAILED: {val_exc}"},
                )
            )
            raise ValueError(
                f"EXEC_VALIDATION_FAILED: {node_id}: {val_exc}"
            ) from val_exc

        # ── retry loop ────────────────────────────────────────────
        retries_used = 0
        output: Any = None
        last_exc: Exception | None = None

        for attempt in range(max(1, effective_max_retries)):
            attempt_start = time.time()
            try:
                output = handler.execute(input_data)
                last_exc = None
                break
            except Exception as exec_exc:
                last_exc = exec_exc
                retries_used += 1

                elapsed = time.time() - attempt_start
                if elapsed > effective_timeout:
                    trace_events.append(
                        self._make_trace_event(
                            run_id=run_id,
                            trace_counter=trace_counter,
                            node_id=node_id,
                            event_type="error",
                            detail={
                                "error": f"EXEC_TIMEOUT: attempt {attempt + 1} "
                                         f"exceeded {effective_timeout}s"
                            },
                        )
                    )
                    trace_counter += 1

                if attempt < effective_max_retries - 1:
                    delay = self.retry_delay_seconds * (2 ** retries_used)
                    time.sleep(delay)

        if last_exc is not None:
            trace_events.append(
                self._make_trace_event(
                    run_id=run_id,
                    trace_counter=trace_counter,
                    node_id=node_id,
                    event_type="error",
                    detail={
                        "error": f"EXEC_RETRIES_EXHAUSTED: {last_exc}"
                    },
                )
            )
            raise RuntimeError(
                f"EXEC_RETRIES_EXHAUSTED: {node_id}: "
                f"failed after {retries_used} attempts: {last_exc}"
            ) from last_exc

        # ── validate output ───────────────────────────────────────
        try:
            handler.validate_output(output)
        except Exception as ov_exc:
            trace_events.append(
                self._make_trace_event(
                    run_id=run_id,
                    trace_counter=trace_counter,
                    node_id=node_id,
                    event_type="error",
                    detail={"error": f"EXEC_OUTPUT_INVALID: {ov_exc}"},
                )
            )
            raise RuntimeError(
                f"EXEC_OUTPUT_INVALID: {node_id}: {ov_exc}"
            ) from ov_exc

        # ── complete trace ────────────────────────────────────────
        total_duration_ms = int((time.time() - run_start) * 1000)
        trace_events.append(
            self._make_trace_event(
                run_id=run_id,
                trace_counter=trace_counter,
                node_id=node_id,
                event_type="complete",
                detail={"duration_ms": total_duration_ms},
            )
        )

        # ── return ────────────────────────────────────────────────
        result = {
            "node_id": node_id,
            "output": output,
            "trace_events": trace_events,
            "duration_ms": total_duration_ms,
            "retries_used": retries_used,
        }
        # Include run_id in output if provided (L5 G3)
        if run_id is not None:
            result["run_id"] = run_id

        return result

    def _make_trace_event(
        self,
        *,
        run_id: str | None,
        trace_counter: int,
        node_id: str,
        event_type: str,
        detail: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Build a trace_event dict conforming to gm-os-core trace_event.schema.json.

        L5 G3/G4 requirements:
        - run_id is included for traceability when provided
        - trace_id is deterministic when run_id is provided (seeded generation)
        - Falls back to random UUID when run_id is not provided

        Args:
            run_id: Optional run identifier for L5 G3 traceability.
            trace_counter: Sequential counter for deterministic trace_id.
            node_id: Originating node.
            event_type: One of node_start, node_complete, node_error.
            detail: Optional extra payload.

        Returns:
            TraceEvent dict with schema_version = "0.1.0".
        """
        # Generate trace_id - deterministic if run_id provided (L5 G4)
        if run_id is not None:
            trace_seed = f"{run_id}-{node_id}-{trace_counter}"
            trace_hash = hashlib.sha256(trace_seed.encode()).hexdigest()[:32]
            trace_id = f"trace-{trace_hash}"
        else:
            trace_id = str(uuid.uuid4())

        event = {
            "schema_version": "0.1.0",
            "trace_id": trace_id,
            "node_id": node_id,
            "event_type": event_type,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "detail": detail or {},
        }

        # Include run_id in trace event for L5 G3 traceability
        if run_id is not None:
            event["run_id"] = run_id

        return event
