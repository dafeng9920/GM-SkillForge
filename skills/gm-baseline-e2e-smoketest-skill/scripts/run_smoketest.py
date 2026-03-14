#!/usr/bin/env python3
import argparse
import copy
import json
import pathlib
import time
import uuid
from datetime import datetime, timezone


SKILL_ID = "gm.baseline.e2e-smoketest"
SKILL_VERSION = "0.1.0"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_trace(step: int, name: str, ok: bool, detail: str = "") -> dict:
    row = {"step": step, "name": name, "ok": ok}
    if detail:
        row["detail"] = detail
    return row


def detect_compliance_flag(task_payload: dict) -> bool:
    probes = json.dumps(task_payload, ensure_ascii=False).lower()
    markers = ["file", "write", "network", "http", "api", "request", "curl"]
    return any(token in probes for token in markers)


def execute_payload(task_payload: dict) -> tuple[dict, list[str]]:
    action = str(task_payload.get("action", "noop")).strip().lower()
    artifacts = ["stdout.log"]

    if action == "noop":
        return {"message": "noop executed"}, artifacts

    if action == "sum":
        numbers = task_payload.get("numbers")
        if not isinstance(numbers, list) or not numbers:
            raise ValueError("task_payload.numbers must be a non-empty list for action=sum")
        total = 0
        for item in numbers:
            if not isinstance(item, (int, float)):
                raise ValueError("numbers must be numeric")
            total += item
        return {"sum": total, "count": len(numbers)}, artifacts

    raise ValueError(f"unsupported action: {action}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run gm.baseline.e2e-smoketest")
    parser.add_argument("--input", required=True, help="Input JSON path")
    parser.add_argument("--output", default="", help="Output JSON path")
    parser.add_argument("--log-dir", default=".tmp/gm-smoketest", help="Log directory")
    args = parser.parse_args()

    started = time.perf_counter()
    run_id = f"run-{uuid.uuid4().hex[:12]}"
    trace = []
    failure_category = ""
    reason = "ok"
    status = "success"
    replayable = True
    output_payload = {"artifacts": ["stdout.log"], "metrics": {"elapsed_ms": 0}}
    input_snapshot = {}
    compliance_flag = False

    try:
        input_data = read_json(pathlib.Path(args.input))
        input_snapshot = copy.deepcopy(input_data)
        validation_mode = str(input_data.get("validation_mode", "strict")).strip().lower() or "strict"

        # Step 1 - Prepare
        if not isinstance(input_data, dict) or not input_data:
            raise ValueError("input must be a non-empty JSON object")
        if "task_payload" not in input_data or not isinstance(input_data["task_payload"], dict) or not input_data["task_payload"]:
            raise ValueError("task_payload must be a non-empty object")
        if validation_mode not in {"strict", "loose"}:
            raise ValueError("validation_mode must be strict or loose")
        trace.append(make_trace(1, "prepare", True))

        # Step 2 - Execute
        timeout_ms = int(input_data.get("timeout_ms", 0) or 0)
        compliance_flag = detect_compliance_flag(input_data["task_payload"])
        result_body, artifacts = execute_payload(input_data["task_payload"])
        if timeout_ms > 0:
            elapsed_preview = int((time.perf_counter() - started) * 1000)
            if elapsed_preview > timeout_ms:
                raise TimeoutError(f"execution exceeded timeout_ms={timeout_ms}")
        trace.append(make_trace(2, "execute", True))

        # Step 3 - Package Result
        output_payload = {
            "artifacts": artifacts if artifacts else ["stdout.log"],
            "metrics": {"elapsed_ms": max(1, int((time.perf_counter() - started) * 1000))},
            "result": result_body
        }
        if not output_payload["artifacts"]:
            raise ValueError("artifacts cannot be empty")
        trace.append(make_trace(3, "package_result", True))

        # Step 4 - Acceptance Validation
        acceptance_pass = (
            status == "success"
            and len(trace) >= 3
            and len(output_payload["artifacts"]) > 0
            and int(output_payload["metrics"]["elapsed_ms"]) > 0
            and (validation_mode != "strict" or replayable is True)
        )
        if acceptance_pass:
            trace.append(make_trace(4, "acceptance_validation", True))
            acceptance_report = {
                "result": "PASS",
                "reason": "All acceptance rules satisfied",
                "replayable": True,
                "diff_summary": ""
            }
        else:
            status = "fail"
            failure_category = "ACCEPTANCE_MISMATCH"
            reason = "Acceptance rules not satisfied"
            trace.append(make_trace(4, "acceptance_validation", False, reason))
            acceptance_report = {
                "result": "FAIL",
                "reason": reason,
                "replayable": validation_mode != "strict",
                "failure_category": failure_category,
                "diff_summary": "acceptance rules failed"
            }

    except TimeoutError as ex:
        status = "fail"
        reason = str(ex)
        failure_category = "EXECUTION_TIMEOUT"
        replayable = False
        trace.append(make_trace(max(1, len(trace) + 1), "execute", False, reason))
        trace.append(make_trace(max(2, len(trace) + 1), "acceptance_validation", False, reason))
        output_payload["metrics"]["elapsed_ms"] = max(1, int((time.perf_counter() - started) * 1000))
        acceptance_report = {
            "result": "FAIL",
            "reason": reason,
            "replayable": False,
            "failure_category": failure_category,
            "diff_summary": "timeout"
        }
    except ValueError as ex:
        status = "fail"
        reason = str(ex)
        failure_category = "INPUT_INVALID" if "input" in reason or "task_payload" in reason or "validation_mode" in reason else "OUTPUT_SCHEMA_ERROR"
        replayable = False
        if not trace:
            trace.append(make_trace(1, "prepare", False, reason))
        trace.append(make_trace(max(2, len(trace) + 1), "acceptance_validation", False, reason))
        output_payload["metrics"]["elapsed_ms"] = max(1, int((time.perf_counter() - started) * 1000))
        acceptance_report = {
            "result": "FAIL",
            "reason": reason,
            "replayable": False,
            "failure_category": failure_category,
            "diff_summary": "validation error"
        }
    except Exception as ex:  # noqa: BLE001
        status = "fail"
        reason = str(ex)
        failure_category = "UNKNOWN_EXCEPTION"
        replayable = False
        if not trace:
            trace.append(make_trace(1, "prepare", False, "unexpected exception"))
        trace.append(make_trace(max(2, len(trace) + 1), "acceptance_validation", False, reason))
        output_payload["metrics"]["elapsed_ms"] = max(1, int((time.perf_counter() - started) * 1000))
        acceptance_report = {
            "result": "FAIL",
            "reason": reason,
            "replayable": False,
            "failure_category": failure_category,
            "diff_summary": "unexpected exception"
        }

    elapsed_ms = max(1, int((time.perf_counter() - started) * 1000))
    output_payload["metrics"]["elapsed_ms"] = elapsed_ms

    result = {
        "run_id": run_id,
        "skill": {"id": SKILL_ID, "version": SKILL_VERSION},
        "status": status,
        "input_snapshot": input_snapshot,
        "execution_trace": trace,
        "output_payload": output_payload,
        "acceptance_report": acceptance_report,
        "compliance_flag": compliance_flag
    }

    out_path = pathlib.Path(args.output) if args.output else pathlib.Path(args.log_dir) / run_id / "result.json"
    write_json(out_path, result)

    log_path = pathlib.Path(args.log_dir) / "runs.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_entry = {
        "run_id": run_id,
        "skill_id": SKILL_ID,
        "skill_version": SKILL_VERSION,
        "execution_timestamp": now_utc(),
        "elapsed_ms": elapsed_ms,
        "acceptance_result": acceptance_report["result"]
    }
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    print(json.dumps({"run_id": run_id, "status": status, "acceptance": acceptance_report["result"], "output": str(out_path)}, ensure_ascii=False))
    return 0 if acceptance_report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

