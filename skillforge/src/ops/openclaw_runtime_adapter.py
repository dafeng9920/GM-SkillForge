"""
OpenClaw Runtime Adapter - Governed Intelligence Bridge

This script bridges OpenClaw's internal execution state to the SkillForge Governance Layer.
It monitors OpenClaw JSON logs and:
1. Translates 'toolCall' events into SkillForge AuditPack evidence.
2. Identifies high-risk actions for Phase 2/3 governance.
3. Provides a real-time 'Heartbeat' of agent behavior.

Usage: python openclaw_runtime_adapter.py --log-dir <path_to_logs>
"""

import json
import os
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any, List

# ============================================================================
# Configuration & Constants
# ============================================================================

# Risk keywords that trigger immediate audit logging
HIGH_RISK_KEYWORDS = ["rm ", "delete", "mv ", "chmod", "curl", "wget", "kill"]

# SkillForge storage paths (relative to app root)
AUDIT_PACK_BASE = Path("AuditPack/evidence")

# ============================================================================
# Logic Classes
# ============================================================================

class OpenClawAdapter:
    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        self.last_filename = None
        self.last_position = 0
        self.active_session_id = None

    def find_latest_log(self) -> Optional[Path]:
        """Find the most recent openclaw-*.log file."""
        logs = list(self.log_dir.glob("openclaw-*.log"))
        if not logs:
            return None
        return max(logs, key=lambda p: os.path.getmtime(p))

    def process_line(self, line: str):
        """Parse a single JSON log line and translate to SkillForge events."""
        try:
            data = json.loads(line)
            # OpenClaw log format check
            # Usually: {"0": "message", "_meta": {...}, "time": "..."}
            
            message = data.get("0", "")
            meta = data.get("_meta", {})
            timestamp = data.get("time", datetime.now(timezone.utc).isoformat())

            # 1. Detect Intent / Reasoning
            if "thinking" in line.lower() or "reasoning" in line.lower():
                self._handle_thinking_event(message, timestamp)

            # 2. Detect Tool Calls (The Bridge to G9)
            if "Executing tool" in message or "tool_call" in line:
                self._handle_tool_event(message, timestamp, data)

            # 3. Detect Risk Execution
            for kw in HIGH_RISK_KEYWORDS:
                if kw in line:
                    self._handle_risk_event(kw, line, timestamp)

        except json.JSONDecodeError:
            pass # Skip non-JSON lines if any

    def _handle_thinking_event(self, content: str, ts: str):
        print(f"[{ts}] [THOUGHT] {content[:100]}...")
        # In a real impl, this would write to AuditPack/experience/

    def _handle_tool_event(self, content: str, ts: str, raw: dict):
        print(f"[{ts}] [TOOL] {content}")
        # Transition to Phase 2: Create EvidenceRef for G9 Gate
        evidence_file = AUDIT_PACK_BASE / f"openclaw_tool_{int(time.time())}.json"
        with open(evidence_file, "w", encoding="utf-8") as f:
            json.dump({
                "type": "OPENCLAW_TOOL_CALL",
                "timestamp": ts,
                "detail": content,
                "raw_event": raw,
                "governance_status": "INTERCEPTED_FOR_AUDIT"
            }, f, indent=2)

    def _handle_risk_event(self, keyword: str, line: str, ts: str):
        print(f"[{ts}] [!!! RISK !!!] Detected '{keyword}' in trace")

    def run(self):
        """Main polling loop."""
        print(f"Starting OpenClaw Governance Adapter. Monitoring {self.log_dir}")
        AUDIT_PACK_BASE.mkdir(parents=True, exist_ok=True)

        while True:
            latest = self.find_latest_log()
            if not latest:
                time.sleep(2)
                continue

            # Handle file rotation
            if latest != self.last_filename:
                print(f"Switching to new log file: {latest.name}")
                self.last_filename = latest
                self.last_position = 0

            # Tail the file
            with open(latest, "r", encoding="utf-8") as f:
                f.seek(self.last_position)
                lines = f.readlines()
                for line in lines:
                    self.process_line(line)
                self.last_position = f.tell()

            time.sleep(1)

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-dir", required=True, help="Path to OpenClaw log directory")
    args = parser.parse_args()

    adapter = OpenClawAdapter(args.log_dir)
    try:
        adapter.run()
    except KeyboardInterrupt:
        print("Adapter stopped by user.")
