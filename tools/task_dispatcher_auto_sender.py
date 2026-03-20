import argparse
import json
from pathlib import Path


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_message(kind: str, payload: dict) -> str:
    if kind in {"review", "compliance"}:
        env = payload["task_envelope"]
        return (
            f"接收任务: {env['task_id']}\n"
            f"模块: {env['module']}\n"
            f"角色: {env['role']}\n"
            f"执行单元: {env['assignee']}\n"
            f"写回路径:\n"
            f"- execution: {env['writeback']['execution_report']}\n"
            f"- review: {env['writeback']['review_report']}\n"
            f"- compliance: {env['writeback']['compliance_attestation']}\n"
            f"下一跳: {env.get('next_hop', 'none')}\n"
        )
    if kind == "final_gate":
        return (
            f"主控终验输入已就绪: {payload['task_id']}\n"
            f"模块: {payload['module']}\n"
            f"状态: {payload['state']}\n"
            f"execution: {payload['execution_report']}\n"
            f"review: {payload['review_report']}\n"
            f"compliance: {payload['compliance_attestation']}\n"
        )
    if kind == "escalation":
        esc = payload["escalation"]
        return (
            f"升级到主控官: {esc['task_id']}\n"
            f"当前状态: {esc['current_state']}\n"
            f"触发原因: {esc['trigger']}\n"
            f"阻断原因: {esc['blocking_reason']}\n"
            f"证据: {esc['evidence_ref']}\n"
        )
    return "unsupported dispatch payload"


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal auto dispatch sender for relay outputs.")
    parser.add_argument("--relay-output-dir", required=True)
    parser.add_argument("--dispatch-dir", required=True)
    args = parser.parse_args()

    relay_dir = Path(args.relay_output_dir)
    dispatch_dir = Path(args.dispatch_dir)
    dispatch_dir.mkdir(parents=True, exist_ok=True)

    packets = []

    patterns = [
        ("review", "*_review_envelope.json"),
        ("compliance", "*_compliance_envelope.json"),
        ("final_gate", "*_final_gate_input.json"),
        ("escalation", "*_escalation_pack.json"),
    ]

    for kind, pattern in patterns:
        for src in relay_dir.glob(pattern):
            payload = json.loads(src.read_text(encoding="utf-8"))
            task_id = payload.get("task_id") or payload.get("task_envelope", {}).get("task_id") or payload.get("escalation", {}).get("task_id")
            packet = {
                "dispatch_packet": {
                    "task_id": task_id,
                    "kind": kind,
                    "source_file": str(src),
                    "payload_file": str(src),
                }
            }
            packet_path = dispatch_dir / f"{task_id}_{kind}_dispatch_packet.json"
            msg_path = dispatch_dir / f"{task_id}_{kind}_dispatch_message.txt"
            write_json(packet_path, packet)
            write_text(msg_path, build_message(kind, payload))
            packets.append({
                "task_id": task_id,
                "kind": kind,
                "packet": str(packet_path),
                "message": str(msg_path),
            })

    write_json(dispatch_dir / "dispatch_summary.json", {"count": len(packets), "packets": packets})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

