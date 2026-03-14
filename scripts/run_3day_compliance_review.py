#!/usr/bin/env python
"""
3-day compliance backtrace review.

Purpose:
- Enforce recurring governance review cadence (every N days).
- Detect policy backdoors via deterministic file checks.
- Optionally run critical regression tests.
- Emit a traceable report for audit.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_DIR = ROOT / "docs" / "compliance_reviews"


@dataclass
class CheckResult:
    check_id: str
    severity: str  # CRITICAL | HIGH | MEDIUM | LOW
    passed: bool
    summary: str
    evidence: str
    required_change: str
    location: str = ""


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _contains(path: Path, pattern: str) -> bool:
    return re.search(pattern, _read(path), flags=re.MULTILINE | re.DOTALL) is not None


def _find_line(path: Path, pattern: str) -> int | None:
    text = _read(path)
    m = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    if not m:
        return None
    return text.count("\n", 0, m.start()) + 1


def _loc(path: Path, line: int | None) -> str:
    if line is None:
        return str(path)
    return f"{path}:{line}"


def _try_unlink(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except PermissionError:
        # On Windows, file may be opened by editor; skip best-effort cleanup.
        pass


def _try_rmtree(path: Path) -> None:
    try:
        shutil.rmtree(path)
    except (PermissionError, FileNotFoundError):
        # Best-effort cleanup only; do not block report generation.
        pass


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        data = json.loads(_read(path))
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        return None
    return None


def check_guard_skill_docs() -> CheckResult:
    a = ROOT / "docs" / "EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md"
    b = ROOT / "docs" / "EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"
    ok = a.exists() and b.exists()
    return CheckResult(
        check_id="CR-001",
        severity="HIGH",
        passed=ok,
        summary="Execution guard policy docs exist",
        evidence=f"{a} exists={a.exists()}, {b} exists={b.exists()}",
        required_change="Restore A/B policy docs as immutable reference sources",
        location=f"{a} | {b}",
    )


def check_n8n_guard_intercept() -> CheckResult:
    path = ROOT / "skillforge" / "src" / "api" / "routes" / "n8n_orchestration.py"
    required_patterns = [
        r"def enforce_execution_guard\(",
        r"execution_contract: Optional\[dict\]",
        r"compliance_attestation: Optional\[dict\]",
        r"guard_signature: Optional\[str\]",
        r"guard_ok,\s*guard_error,\s*guard_message,\s*guard_required_changes\s*=\s*enforce_execution_guard\(",
        r"blocked_by=\"EXECUTION_GUARD\"",
    ]
    missing = [p for p in required_patterns if not _contains(path, p)]
    ok = not missing
    loc_line = _find_line(path, r"def enforce_execution_guard\(")
    return CheckResult(
        check_id="CR-002",
        severity="CRITICAL",
        passed=ok,
        summary="n8n entrypoints enforce execution guard hard intercept",
        evidence="missing_patterns=" + json.dumps(missing, ensure_ascii=False),
        required_change="Reinstate hard intercept in run_intent/import_external_skill before execution",
        location=_loc(path, loc_line),
    )


def check_forbidden_field_policy() -> CheckResult:
    path = ROOT / "skillforge" / "src" / "api" / "routes" / "n8n_orchestration.py"
    required_fields = ["gate_decision", "release_allowed", "permit_token", "evidence_ref", "permit_id", "run_id"]
    text = _read(path)
    missing = [f for f in required_fields if f'"{f}"' not in text]
    ok = not missing
    loc_line = _find_line(path, r"FORBIDDEN_N8N_FIELDS")
    return CheckResult(
        check_id="CR-003",
        severity="HIGH",
        passed=ok,
        summary="Forbidden n8n override fields remain blocked",
        evidence="missing_fields=" + json.dumps(missing, ensure_ascii=False),
        required_change="Restore forbidden field denylist and rejection evidence flow",
        location=_loc(path, loc_line),
    )


def check_permit_fail_closed_signature() -> CheckResult:
    path = ROOT / "skillforge" / "src" / "skills" / "gates" / "gate_permit.py"
    text = _read(path)
    risky_patterns = [
        r"if algo in \(\"RS256\", \"ES256\"\):\s*return True",
        r"if not key:\s*#.*\n\s*return True",
    ]
    hit_locs: list[str] = []
    for p in risky_patterns:
        ln = _find_line(path, p)
        if ln is not None:
            hit_locs.append(_loc(path, ln))
    hits = hit_locs
    ok = not hits
    return CheckResult(
        check_id="CR-004",
        severity="CRITICAL",
        passed=ok,
        summary="Permit signature verification has no downgrade bypass",
        evidence="risky_pattern_hits=" + json.dumps(hits, ensure_ascii=False),
        required_change="Remove signature downgrade path; enforce hard fail when unverifiable",
        location=", ".join(hits) if hits else _loc(path, _find_line(path, r"def _stub_signature_verifier")),
    )


def check_prod_sample_pollution() -> CheckResult:
    path = ROOT / "skillforge" / "src" / "storage" / "audit_pack_store.py"
    text = _read(path)
    # Accept guarded variants like:
    # env = os.getenv("SKILLFORGE_ENV", "prod").lower()
    # if env in ("dev", "test") and len(self._packs) == 0:
    #     self._create_sample_packs()
    has_env_guard = re.search(
        r"if\s+.*in\s+\(\"dev\",\s*\"test\"\).*\:\s*\n\s*self\._create_sample_packs\(\)",
        text,
        flags=re.MULTILINE,
    )
    unconditional_sample = re.search(
        r"if\s+(?:not\s+self\._packs|len\(self\._packs\)\s*==\s*0)\s*:\s*\n\s*self\._create_sample_packs\(\)",
        text,
        flags=re.MULTILINE,
    )
    ok = bool(has_env_guard) and not bool(unconditional_sample)
    evidence = {
        "has_env_guard": bool(has_env_guard),
        "has_unconditional_sample_creation": bool(unconditional_sample),
    }
    env_line = _find_line(path, r"if\s+.*in\s+\(\"dev\",\s*\"test\"\)")
    bad_line = _find_line(path, r"if\s+(?:not\s+self\._packs|len\(self\._packs\)\s*==\s*0)\s*:")
    loc = _loc(path, env_line or bad_line)
    return CheckResult(
        check_id="CR-005",
        severity="CRITICAL",
        passed=ok,
        summary="Production path does not auto-inject sample data",
        evidence=json.dumps(evidence, ensure_ascii=False),
        required_change="Gate sample creation behind SKILLFORGE_ENV in {dev,test} only",
        location=loc,
    )


def check_registry_dual_track_controls() -> CheckResult:
    path = ROOT / "skillforge" / "src" / "storage" / "registry_store.py"
    text = _read(path)
    signals = [
        "REGISTRY_BACKEND",
        "REGISTRY_DUAL_WRITE",
        "REGISTRY_SHADOW_READ_COMPARE",
    ]
    missing = [s for s in signals if s not in text]
    ok = not missing
    loc_line = _find_line(path, r"REGISTRY_BACKEND|sqlite3")
    return CheckResult(
        check_id="CR-006",
        severity="HIGH",
        passed=ok,
        summary="Registry supports dual-track migration controls",
        evidence="missing_signals=" + json.dumps(missing, ensure_ascii=False),
        required_change="Implement dual-write/shadow-read feature flags before cutover",
        location=_loc(path, loc_line),
    )


def check_l4_skill07_crypto_gate_code() -> CheckResult:
    path = ROOT / "skills" / "p2-final-gate-aggregate-skill" / "aggregate_final_gate.py"
    required_patterns = [
        r"--require-crypto-signature",
        r"def check_crypto_signatures\(",
        r"has_invalid_crypto_signature",
        r"has_invalid_signer_id",
        r"return\s+\"FINAL_FAIL\"",
        r"return\s+\"REQUIRES_CHANGES\"",
    ]
    missing = [p for p in required_patterns if not _contains(path, p)]
    ok = not missing
    loc_line = _find_line(path, r"--require-crypto-signature")
    return CheckResult(
        check_id="CR-008",
        severity="CRITICAL",
        passed=ok,
        summary="L4-SKILL-07 crypto signature fail-closed gate exists in aggregator",
        evidence="missing_patterns=" + json.dumps(missing, ensure_ascii=False),
        required_change="Reinstate --require-crypto-signature and fail-closed decision path in aggregate_final_gate.py",
        location=_loc(path, loc_line),
    )


def check_l4_skill07_signer_allowlist() -> CheckResult:
    path = ROOT / "scripts" / "verify_guard_signature.py"
    required_patterns = [
        r"ALLOWED_SIGNER_IDS",
        r"def validate_signer_id\(",
        r"Invalid signer_id",
        r"has_invalid_signer",
    ]
    missing = [p for p in required_patterns if not _contains(path, p)]
    ok = not missing
    loc_line = _find_line(path, r"ALLOWED_SIGNER_IDS")
    return CheckResult(
        check_id="CR-009",
        severity="CRITICAL",
        passed=ok,
        summary="L4-SKILL-07 signer allowlist and validation are implemented",
        evidence="missing_patterns=" + json.dumps(missing, ensure_ascii=False),
        required_change="Restore ALLOWED_SIGNER_IDS and validate_signer_id fail-closed checks in verify_guard_signature.py",
        location=_loc(path, loc_line),
    )


def check_l4_skill07_evidence_chain() -> CheckResult:
    base = ROOT / "docs" / "2026-02-22" / "verification"
    t83 = base / "T83_execution_report.yaml"
    t84 = base / "T84_gate_decision.json"
    t85 = base / "T85_compliance_attestation.json"
    t86 = base / "L4-SKILL-07_final_gate_decision.json"

    missing_files = [str(p) for p in [t83, t84, t85, t86] if not p.exists()]
    decisions: dict[str, str] = {}
    parse_errors: list[str] = []

    if t84.exists():
        try:
            decisions["T84"] = json.loads(_read(t84)).get("decision", "")
        except Exception as e:  # pragma: no cover - defensive path
            parse_errors.append(f"T84 parse_error={e}")
    if t85.exists():
        try:
            decisions["T85"] = json.loads(_read(t85)).get("decision", "")
        except Exception as e:  # pragma: no cover - defensive path
            parse_errors.append(f"T85 parse_error={e}")
    if t86.exists():
        try:
            decisions["T86"] = json.loads(_read(t86)).get("decision", "")
        except Exception as e:  # pragma: no cover - defensive path
            parse_errors.append(f"T86 parse_error={e}")

    t83_has_expected = t83.exists() and ("task_id: T83" in _read(t83))
    decision_ok = (
        decisions.get("T84") == "ALLOW"
        and decisions.get("T85") == "PASS"
        and decisions.get("T86") == "ALLOW"
    )
    ok = (not missing_files) and t83_has_expected and decision_ok and (len(parse_errors) == 0)

    evidence = {
        "missing_files": missing_files,
        "t83_task_id_ok": t83_has_expected,
        "decisions": decisions,
        "parse_errors": parse_errors,
    }
    return CheckResult(
        check_id="CR-010",
        severity="HIGH",
        passed=ok,
        summary="L4-SKILL-07 triad evidence chain and final gate decisions are complete",
        evidence=json.dumps(evidence, ensure_ascii=False),
        required_change="Restore T83/T84/T85/T86 artifacts and ensure T84=ALLOW, T85=PASS, T86=ALLOW",
        location=str(base),
    )


def check_governance_dispatch_assets() -> CheckResult:
    skill = ROOT / "skills" / "governance-orchestrator-skill" / "SKILL.md"
    registry = ROOT / "configs" / "dispatch_skill_registry.json"
    gate_script = ROOT / "scripts" / "gate_final_decision.py"

    missing_files = [str(p) for p in [skill, registry, gate_script] if not p.exists()]
    registry_has_skill = False
    registry_has_alias = False
    registry_parse_error = ""
    if registry.exists():
        try:
            payload = json.loads(_read(registry))
            skills = payload.get("dispatch_skills", [])
            names = {item.get("name") for item in skills if isinstance(item, dict)}
            registry_has_skill = "governance-orchestrator-skill" in names
            registry_has_alias = "trinity-dispatch-orchestrator-skill" in names
        except Exception as e:  # pragma: no cover - defensive path
            registry_parse_error = str(e)

    ok = (
        len(missing_files) == 0
        and registry_has_skill
        and registry_has_alias
        and registry_parse_error == ""
    )
    evidence = {
        "missing_files": missing_files,
        "registry_has_governance_skill": registry_has_skill,
        "registry_has_trinity_alias": registry_has_alias,
        "registry_parse_error": registry_parse_error,
    }
    return CheckResult(
        check_id="CR-011",
        severity="HIGH",
        passed=ok,
        summary="Governance dispatch core assets and compatibility alias are present",
        evidence=json.dumps(evidence, ensure_ascii=False),
        required_change="Restore governance-orchestrator skill, dispatch registry mapping, and gate_final_decision entrypoint",
        location=f"{skill} | {registry} | {gate_script}",
    )


def check_governance_openai_metadata() -> CheckResult:
    path = ROOT / "skills" / "governance-orchestrator-skill" / "agents" / "openai.yaml"
    ok = path.exists()
    return CheckResult(
        check_id="CR-012",
        severity="MEDIUM",
        passed=ok,
        summary="Governance orchestrator skill has cross-platform openai.yaml metadata",
        evidence=f"{path} exists={ok}",
        required_change="Add skills/governance-orchestrator-skill/agents/openai.yaml with minimal metadata fields",
        location=str(path),
    )


def check_l4p5_evidence_chain() -> CheckResult:
    base = ROOT / "docs" / "2026-02-22" / "verification"
    p93 = base / "T93_gate_decision.json"
    p94 = base / "T94_compliance_attestation.json"
    p98 = base / "T98_gate_decision.json"
    p99 = base / "T99_compliance_attestation.json"
    p100 = base / "T100_execution_report.yaml"
    final_gate = base / "L4P5_final_gate_decision.json"
    required_files = [p93, p94, p98, p99, p100, final_gate]
    missing_files = [str(p) for p in required_files if not p.exists()]

    d93 = (_load_json(p93) or {}).get("decision", "")
    d94 = (_load_json(p94) or {}).get("decision", "")
    d98 = (_load_json(p98) or {}).get("decision", "")
    d99 = (_load_json(p99) or {}).get("decision", "")
    dfg = (_load_json(final_gate) or {}).get("decision", "")
    t100_ok = p100.exists() and ("task_id: T100" in _read(p100))

    decision_ok = (
        d93 == "ALLOW"
        and d94 == "PASS"
        and d98 == "ALLOW"
        and d99 == "PASS"
        and dfg == "ALLOW"
    )
    ok = len(missing_files) == 0 and decision_ok and t100_ok
    evidence = {
        "missing_files": missing_files,
        "decisions": {
            "T93": d93,
            "T94": d94,
            "T98": d98,
            "T99": d99,
            "L4P5": dfg,
        },
        "t100_task_id_ok": t100_ok,
    }
    return CheckResult(
        check_id="CR-013",
        severity="HIGH",
        passed=ok,
        summary="L4P5 triad closure chain and final gate decision are complete",
        evidence=json.dumps(evidence, ensure_ascii=False),
        required_change="Restore T93/T94/T98/T99/T100/L4P5 artifacts and required ALLOW/PASS decisions",
        location=str(base),
    )


def check_t3a_core_artifacts() -> CheckResult:
    base = ROOT / "docs" / "2026-03-08"
    required = [
        base / "execution_receipt.json",
        base / "completion_record.md",
        base / "resume_handoff.md",
        base / "checkpoint" / "state.yaml",
        base / "p2_doc_integration_report.md",
        base / "p3_baseline_inventory.md",
    ]
    missing = [str(p) for p in required if not p.exists()]
    ok = not missing
    return CheckResult(
        check_id="CR-014",
        severity="HIGH",
        passed=ok,
        summary="T3-A core host-absorbed artifacts are present in authoritative repo paths",
        evidence=json.dumps({"missing_files": missing}, ensure_ascii=False),
        required_change="Restore missing T3-A host-absorbed artifacts under docs/2026-03-08 before closeout",
        location=str(base),
    )


def check_t3a_p2_governor_alignment() -> CheckResult:
    path = ROOT / "docs" / "2026-03-08" / "p2_doc_integration_report.md"
    required_patterns = [
        r"skills/lobster-cloud-execution-governor-skill/",
        r"DEPRECATED / DO NOT USE",
        r"skills/governor-skill/",
        r"Authoritative Skill",
    ]
    missing = [p for p in required_patterns if not path.exists() or not _contains(path, p)]
    bad_patterns = []
    if path.exists():
        if _contains(path, r"已删除"):
            bad_patterns.append("claims_deleted_instead_of_deprecated")
        if _contains(path, r"无 governor-skill"):
            bad_patterns.append("claims_missing_governor_skill_dir")
    ok = not missing and not bad_patterns
    return CheckResult(
        check_id="CR-015",
        severity="HIGH",
        passed=ok,
        summary="T3-A P2 report aligns authoritative governor skill and deprecated alias semantics",
        evidence=json.dumps(
            {"missing_patterns": missing, "bad_patterns": bad_patterns},
            ensure_ascii=False,
        ),
        required_change="Rewrite T3-A P2 report so lobster-cloud-execution-governor-skill is authoritative and governor-skill is deprecated, not deleted",
        location=str(path),
    )


def check_t3a_p3_wave_split() -> CheckResult:
    path = ROOT / "docs" / "2026-03-08" / "p3_baseline_inventory.md"
    required_patterns = [
        r"Wave 1",
        r"Wave 2",
        r"audit_repo_skill\.yml",
        r"tombstone_skill\.yml",
        r"defer",
        r"promote_now",
    ]
    missing = [p for p in required_patterns if not path.exists() or not _contains(path, p)]
    banned_patterns = []
    if path.exists():
        if _contains(path, r"无遗留或待处理项"):
            banned_patterns.append("claims_no_remaining_items")
        if _contains(path, r"defer \| 0"):
            banned_patterns.append("claims_zero_defer")
    ok = not missing and not banned_patterns
    return CheckResult(
        check_id="CR-016",
        severity="HIGH",
        passed=ok,
        summary="T3-A P3 baseline reflects Wave 1 promoted items and Wave 2 deferred items",
        evidence=json.dumps(
            {"missing_patterns": missing, "banned_patterns": banned_patterns},
            ensure_ascii=False,
        ),
        required_change="Correct T3-A P3 baseline so Wave 2 deferred items remain visible and not falsely collapsed into promote_now",
        location=str(path),
    )


def check_t3a_state_alignment() -> CheckResult:
    path = ROOT / "docs" / "2026-03-08" / "checkpoint" / "state.yaml"
    required_patterns = [
        r"host_absorb_manual:\s*true",
        r"review_pending:\s*true",
        r"compliance_pending:\s*true",
        r"wave_2:",
        r"audit_repo_skill\.yml",
        r"tombstone_skill\.yml",
        r"disposition:\s*defer",
    ]
    missing = [p for p in required_patterns if not path.exists() or not _contains(path, p)]
    banned_patterns = []
    if path.exists():
        if _contains(path, r"all_promoted:\s*true"):
            banned_patterns.append("all_promoted_true")
        if _contains(path, r"files_inventoried:\s*3"):
            banned_patterns.append("files_inventoried_three")
    ok = not missing and not banned_patterns
    return CheckResult(
        check_id="CR-017",
        severity="MEDIUM",
        passed=ok,
        summary="T3-A checkpoint state aligns with manual host absorb and corrected Wave 2 defer split",
        evidence=json.dumps(
            {"missing_patterns": missing, "banned_patterns": banned_patterns},
            ensure_ascii=False,
        ),
        required_change="Rewrite T3-A checkpoint state to reflect host_absorb_manual and Wave 2 deferred items without stale all_promoted summary",
        location=str(path),
    )


def check_3day_cadence(report_dir: Path, max_gap_days: int) -> CheckResult:
    now = datetime.now(timezone.utc)
    today = now.date()
    report_dir.mkdir(parents=True, exist_ok=True)
    date_re = re.compile(r"^review_(\d{4}-\d{2}-\d{2})\.(md|json)$")
    dates = []
    for p in report_dir.iterdir():
        m = date_re.match(p.name)
        if not m:
            continue
        try:
            dates.append(datetime.strptime(m.group(1), "%Y-%m-%d").date())
        except ValueError:
            continue
    # Also accept latest-mode artifacts and run archive mtimes so cadence
    # still works when cleanup keeps only review_latest.* files.
    for p in [report_dir / "review_latest.md", report_dir / "review_latest.json"]:
        if p.exists():
            dates.append(datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).date())
    runs_root = report_dir / "runs"
    if runs_root.exists():
        for p in runs_root.rglob("review.json"):
            try:
                dates.append(datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).date())
            except OSError:
                continue
    if not dates:
        return CheckResult(
            check_id="CR-007",
            severity="MEDIUM",
            passed=False,
            summary="No prior compliance review report found",
            evidence=f"report_dir={report_dir}",
            required_change=f"Establish recurring review report cadence every {max_gap_days} days",
            location=str(report_dir),
        )
    latest = max(dates)
    gap = (today - latest).days
    ok = gap <= max_gap_days
    return CheckResult(
        check_id="CR-007",
        severity="MEDIUM",
        passed=ok,
        summary="Compliance review cadence is within target window",
        evidence=f"latest_report_date={latest.isoformat()}, gap_days={gap}, max_gap_days={max_gap_days}",
        required_change=f"Run review now and keep cadence <= {max_gap_days} days",
        location=str(report_dir),
    )


def run_pytest_checks() -> list[CheckResult]:
    tests = [
        "skillforge/tests/test_n8n_run_intent_internal_permit.py",
        "skillforge/tests/test_n8n_orchestration.py",
    ]
    results: list[CheckResult] = []
    for test_path in tests:
        cmd = [sys.executable, "-m", "pytest", "-q", test_path]
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        ok = proc.returncode == 0
        out = (proc.stdout or "") + (proc.stderr or "")
        out = out.strip().replace("\r\n", "\n")
        if len(out) > 1200:
            out = out[:1200] + "\n...<truncated>"
        results.append(
            CheckResult(
                check_id=f"CR-T-{Path(test_path).name}",
                severity="HIGH",
                passed=ok,
                summary=f"Regression test: {test_path}",
                evidence=out,
                required_change=f"Fix failing test and restore fail-closed guard behavior in {test_path}",
                location=test_path,
            )
        )
    return results


def collect_checks(report_dir: Path, max_gap_days: int, run_tests: bool) -> list[CheckResult]:
    checks: list[CheckResult] = [
        check_guard_skill_docs(),
        check_n8n_guard_intercept(),
        check_forbidden_field_policy(),
        check_permit_fail_closed_signature(),
        check_prod_sample_pollution(),
        check_registry_dual_track_controls(),
        check_l4_skill07_crypto_gate_code(),
        check_l4_skill07_signer_allowlist(),
        check_l4_skill07_evidence_chain(),
        check_governance_dispatch_assets(),
        check_governance_openai_metadata(),
        check_l4p5_evidence_chain(),
        check_t3a_core_artifacts(),
        check_t3a_p2_governor_alignment(),
        check_t3a_p3_wave_split(),
        check_t3a_state_alignment(),
        check_3day_cadence(report_dir, max_gap_days),
    ]
    if run_tests:
        checks.extend(run_pytest_checks())
    return checks


def is_failure(result: CheckResult) -> bool:
    return not result.passed and result.severity in {"CRITICAL", "HIGH"}


def write_reports(
    report_dir: Path,
    checks: list[CheckResult],
    keep_history: bool,
) -> tuple[Path, Path, Path, Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    d = now.strftime("%Y-%m-%d")
    t = now.strftime("%H%M%SZ")
    ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    if keep_history:
        json_path = report_dir / f"review_{d}.json"
        md_path = report_dir / f"review_{d}.md"
        run_dir = report_dir / "runs" / d / t
        run_dir.mkdir(parents=True, exist_ok=True)
    else:
        # Default mode: keep workspace clean and only retain latest artifacts.
        for old in report_dir.glob("review_*.md"):
            _try_unlink(old)
        for old in report_dir.glob("review_*.json"):
            _try_unlink(old)
        runs_root = report_dir / "runs"
        if runs_root.exists():
            _try_rmtree(runs_root)

        json_path = report_dir / "review_latest.json"
        md_path = report_dir / "review_latest.md"
        run_dir = runs_root / "latest"
        run_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": ts,
        "summary": {
            "total": len(checks),
            "passed": sum(1 for c in checks if c.passed),
            "failed": sum(1 for c in checks if not c.passed),
            "critical_or_high_failed": sum(1 for c in checks if is_failure(c)),
            "overall": "PASS" if all(not is_failure(c) for c in checks) else "FAIL",
        },
        "checks": [c.__dict__ for c in checks],
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    failed = [c for c in checks if not c.passed]
    critical_high_failed = [c for c in failed if c.severity in {"CRITICAL", "HIGH"}]
    top_risks = critical_high_failed[:3]

    lines = [
        f"# Compliance Review {d}",
        "",
        f"- Generated at: `{ts}`",
        f"- Overall: **{payload['summary']['overall']}**",
        f"- Total checks: `{payload['summary']['total']}`",
        f"- Passed: `{payload['summary']['passed']}`",
        f"- Failed: `{payload['summary']['failed']}`",
        f"- Critical/High failed: `{payload['summary']['critical_or_high_failed']}`",
        "",
        "## 结论（先看这里）",
        "",
    ]

    if payload["summary"]["overall"] == "PASS":
        lines.extend(
            [
                "- 当前规范性状态：**可继续发布**。",
                "- 未发现 CRITICAL/HIGH 级阻断项。",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "- 当前规范性状态：**不建议发布**（存在 CRITICAL/HIGH 级问题）。",
                f"- 阻断项数量：`{len(critical_high_failed)}`。",
                "",
            ]
        )

    lines.extend(
        [
            "## Top 风险（需要先修）",
            "",
        ]
    )
    if top_risks:
        for idx, c in enumerate(top_risks, start=1):
            lines.append(f"{idx}. `{c.check_id}` [{c.severity}] {c.summary}")
            lines.append(f"   - 为什么危险：{c.evidence}")
            lines.append(f"   - 建议动作：{c.required_change}")
    else:
        lines.append("1. 无 CRITICAL/HIGH 风险项。")

    lines.extend(
        [
            "",
            "## 48小时执行清单",
            "",
        ]
    )
    if critical_high_failed:
        for c in critical_high_failed:
            lines.append(f"- [ ] 修复 `{c.check_id}`：{c.required_change}")
    else:
        lines.append("- [ ] 维持现状，按 3 天节奏继续巡检。")

    lines.extend(
        [
            "",
            "## 汇总雷达（脚本自动生成）",
            "",
            "| 问题点 | 哪里不对 | 风险级别 | 需要怎么搞 | 完成标准 |",
            "|---|---|---|---|---|",
        ]
    )
    if failed:
        for c in failed:
            completion_standard = (
                "对应检查项结果变为 PASS，且本次审查报告不再出现该失败项"
            )
            lines.append(
                f"| {c.check_id} | {c.summary} | {c.severity} | {c.required_change} | {completion_standard} |"
            )
    else:
        lines.append("| - | 无失败项 | - | 维持现状 | 所有检查持续 PASS |")

    lines.extend(
        [
            "",
            "## 探针定位（失败项代码位置）",
            "",
        ]
    )
    probe_rows = [c for c in checks if not c.passed]
    if probe_rows:
        lines.append("| Check ID | 代码定位 |")
        lines.append("|---|---|")
        for c in probe_rows:
            lines.append(f"| {c.check_id} | `{c.location or 'N/A'}` |")
    else:
        lines.append("- 无失败项，无需探针定位。")

    lines.extend(
        [
            "",
            "## 全量检查明细（审计证据）",
            "",
            "| Check ID | Severity | Result | Summary |",
            "|---|---|---|---|",
        ]
    )
    for c in checks:
        result = "PASS" if c.passed else "FAIL"
        lines.append(f"| {c.check_id} | {c.severity} | {result} | {c.summary} |")
    lines.extend(["", "## Required Changes", ""])
    for c in checks:
        if c.passed:
            continue
        lines.append(f"- `{c.check_id}` ({c.severity}): {c.required_change}")
        lines.append(f"  Evidence: `{c.evidence}`")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    run_md = run_dir / "review.md"
    run_json = run_dir / "review.json"
    shutil.copy2(md_path, run_md)
    shutil.copy2(json_path, run_json)
    return md_path, json_path, run_dir, run_md, run_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run 3-day compliance review checks.")
    parser.add_argument(
        "--report-dir",
        default=str(DEFAULT_REPORT_DIR),
        help="Directory to write review reports (default: docs/compliance_reviews)",
    )
    parser.add_argument(
        "--max-gap-days",
        type=int,
        default=3,
        help="Maximum allowed days since last review report (default: 3)",
    )
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Run critical pytest checks as part of the review",
    )
    parser.add_argument(
        "--allow-fail",
        action="store_true",
        help="Always exit 0 even if critical/high checks fail",
    )
    parser.add_argument(
        "--keep-history",
        action="store_true",
        help="Keep dated reports and per-run archive folders (default: keep latest only)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print extended output paths and URI hints",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report_dir = Path(args.report_dir)
    checks = collect_checks(report_dir=report_dir, max_gap_days=args.max_gap_days, run_tests=args.run_tests)
    md_path, json_path, run_dir, run_md, run_json = write_reports(report_dir, checks, keep_history=args.keep_history)
    md_uri = md_path.resolve().as_uri()
    json_uri = json_path.resolve().as_uri()
    run_dir_uri = run_dir.resolve().as_uri()
    run_md_uri = run_md.resolve().as_uri()
    run_json_uri = run_json.resolve().as_uri()

    critical_failed = [c for c in checks if is_failure(c)]
    print(f"[compliance-review] report_md={md_path}")
    print(f"[compliance-review] report_json={json_path}")
    print(f"[compliance-review] run_dir={run_dir}")
    if args.verbose:
        print(f"[compliance-review] run_md={run_md}")
        print(f"[compliance-review] run_json={run_json}")
        print(f"[compliance-review] open_md={md_uri}")
        print(f"[compliance-review] open_json={json_uri}")
        print(f"[compliance-review] open_run_dir={run_dir_uri}")
        print(f"[compliance-review] open_run_md={run_md_uri}")
        print(f"[compliance-review] open_run_json={run_json_uri}")
    print(f"[compliance-review] total={len(checks)} failed={sum(1 for c in checks if not c.passed)} critical_or_high_failed={len(critical_failed)}")

    if critical_failed and not args.allow_fail:
        for c in critical_failed:
            print(f"[FAIL] {c.check_id} {c.summary} :: {c.evidence}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
