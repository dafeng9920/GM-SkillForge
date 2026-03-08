"""
SemgrepRunner — subprocess wrapper for semgrep static analysis.
Falls back to mock results if semgrep is not installed.

Usage:
    runner = SemgrepRunner(ruleset="p/python")
    result = runner.analyze("/path/to/code")

    # Access findings
    for finding in result.findings:
        print(f"{finding.rule_id}: {finding.message}")

    # Access raw output
    print(result.raw_output)
"""
from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Finding:
    """A single finding from static analysis."""

    rule_id: str
    severity: str  # "error", "warning", "info"
    message: str
    location: dict[str, Any]  # {"file": str, "line": int, "column": int}
    evidence_id: str = ""  # Assigned when added to evidence chain

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "message": self.message,
            "location": self.location,
            "evidence_id": self.evidence_id,
        }


@dataclass
class AnalysisResult:
    """Result from semgrep analysis."""

    findings: list[Finding] = field(default_factory=list)
    raw_output: str = ""
    tool_version: str = "unknown"
    exit_code: int = 0
    error_message: str = ""
    analyzed_at: str = ""
    target_path: str = ""


class SemgrepRunner:
    """
    Wrapper for semgrep static analysis tool.

    Runs semgrep on a target path and returns structured results.
    Falls back to mock results if semgrep is not installed.
    """

    def __init__(self, ruleset: str = "p/python"):
        """
        Initialize SemgrepRunner.

        Args:
            ruleset: Semgrep ruleset to use (e.g., "p/python", "p/security-audit")
        """
        self.ruleset = ruleset
        self._version: str | None = None

    def _get_version(self) -> str:
        """Get semgrep version, cache result."""
        if self._version is not None:
            return self._version

        try:
            result = subprocess.run(
                ["semgrep", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                self._version = result.stdout.strip()
            else:
                self._version = "unknown"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self._version = "not-installed"

        return self._version

    def analyze(self, target_path: str) -> AnalysisResult:
        """
        Run semgrep on target_path.

        Args:
            target_path: Path to the code to analyze

        Returns:
            AnalysisResult with findings, raw output, and metadata.
            Returns mock results if semgrep is not installed.
        """
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        try:
            result = subprocess.run(
                ["semgrep", "--json", "--config", self.ruleset, target_path],
                capture_output=True,
                text=True,
                timeout=120,
            )
            return self._parse_output(result, target_path, timestamp)
        except FileNotFoundError:
            # semgrep not installed → return mock
            return self._mock_result(target_path, timestamp)
        except subprocess.TimeoutExpired:
            return AnalysisResult(
                findings=[],
                raw_output="",
                tool_version=self._get_version(),
                exit_code=-1,
                error_message="semgrep execution timed out after 120 seconds",
                analyzed_at=timestamp,
                target_path=target_path,
            )

    def _parse_output(
        self,
        result: subprocess.CompletedProcess,
        target_path: str,
        timestamp: str,
    ) -> AnalysisResult:
        """Parse semgrep JSON output into AnalysisResult."""
        raw_output = result.stdout
        findings: list[Finding] = []

        try:
            data = json.loads(raw_output) if raw_output else {}
            results = data.get("results", [])

            for r in results:
                extra = r.get("extra", {})

                finding = Finding(
                    rule_id=r.get("check_id", "unknown"),
                    severity=extra.get("severity", "info"),
                    message=extra.get("message", r.get("message", "No message")),
                    location={
                        "file": r.get("path", ""),
                        "line": r.get("start", {}).get("line", 0),
                        "column": r.get("start", {}).get("col", 0),
                    },
                )
                findings.append(finding)

        except json.JSONDecodeError:
            # If JSON parsing fails, return empty findings but preserve raw output
            pass

        return AnalysisResult(
            findings=findings,
            raw_output=raw_output,
            tool_version=self._get_version(),
            exit_code=result.returncode,
            error_message=result.stderr if result.returncode != 0 else "",
            analyzed_at=timestamp,
            target_path=target_path,
        )

    def _mock_result(self, target_path: str, timestamp: str) -> AnalysisResult:
        """Generate mock results when semgrep is not installed."""
        mock_findings = [
            Finding(
                rule_id="python.lang.security.audit.dangerous-subprocess-use",
                severity="warning",
                message="Potential shell injection via subprocess with shell=True",
                location={"file": f"{target_path}/example.py", "line": 42, "column": 5},
            ),
            Finding(
                rule_id="python.lang.best-practice.print-used",
                severity="info",
                message="print() function used in production code",
                location={"file": f"{target_path}/example.py", "line": 10, "column": 1},
            ),
        ]

        mock_raw_output = json.dumps({
            "results": [
                {
                    "check_id": f.rule_id,
                    "path": f.location["file"],
                    "start": {"line": f.location["line"], "col": f.location["column"]},
                    "extra": {"severity": f.severity, "message": f.message},
                }
                for f in mock_findings
            ],
            "errors": [],
            "stats": {"total_time": 0.5},
        })

        return AnalysisResult(
            findings=mock_findings,
            raw_output=mock_raw_output,
            tool_version="mock-0.0.0",
            exit_code=0,
            error_message="[MOCK] semgrep not installed, using mock results",
            analyzed_at=timestamp,
            target_path=target_path,
        )
