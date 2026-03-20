"""
===============================================================================
WARNING: 此脚本超出第 1 批范围，不是 T7 合格交付物
===============================================================================

此脚本包含第 2 批和第 3 批能力的引用：
- DraftSpecGate (第 2 批 - Finding Adjudication)
- ConstitutionRiskGate (第 2 批 - Owner Review)
- GateScaffoldSkill (第 2 批 - Escalation Gate)
- GateSandboxSkill (第 3 批 - Continuous Audit Runtime)
- GatePublishSkill (第 3 批 - AuditPack)

根据 docs/2026-03-15/第1批施工单.md 第 22-27 行：
第 1 批明确不做：
- 不做 Finding Adjudication
- 不做 Owner Review
- 不做 Escalation Gate
- 不做 Continuous Audit Runtime
- 不做 AuditPack

因此此脚本不得作为 T7 的有效交付物或证据。

如需运行第 1 批发现链，请使用：
    python scripts/run_discovery_chain.py

===============================================================================
"""

import sys
import os
import json
import hashlib
import time
from pathlib import Path

# Add src to path
sys.path.append(os.path.abspath("skillforge/src"))

# ============================================================================
# DISABLED: 以下导入超出第 1 批 T7 发现链范围，已被禁用
# ============================================================================
# 第 2 批能力 (Finding Adjudication, Owner Review, Escalation Gate):
# from skills.gates.gate_draft_spec import DraftSpecGate
# from skills.gates.gate_risk import ConstitutionRiskGate
# from skills.gates.gate_scaffold import GateScaffoldSkill
# 第 3 批能力 (Continuous Audit Runtime, AuditPack):
# from skills.gates.gate_sandbox import GateSandboxSkill
# from skills.gates.gate_publish import GatePublishSkill
#
# 第 1 批允许的导入 (仅 T1-T6 发现链):
try:
    from skills.gates.gate_intake import GateIntakeRepo
    from skills.gates.gate_scan import GateRepoScanFitScore
    from skills.gates.gate_intake import intake_repo  # T7: 导入 T1 的便捷函数
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import T1 Gate Skills: {e}")
    print("Ensure you are running from D:\\GM-SkillForge and files exist in skillforge/src/skills/gates/")
    sys.exit(1)

def run_gate(gate_name, gate_class, input_data):
    print(f"\n>>> Running {gate_name}...")
    gate = gate_class()
    
    # Validate Input
    errors = gate.validate_input(input_data)
    if errors:
        print(f"❌ {gate_name} Input Validation Failed: {errors}")
        sys.exit(1)
        
    # Execute
    result = gate.execute(input_data)
    
    # helper to convert if object
    if hasattr(gate, "to_dict"):
        result = gate.to_dict(result)
    elif hasattr(result, "__dataclass_fields__"):
        import dataclasses
        result = dataclasses.asdict(result)
    
    # Validate Output
    out_errors = gate.validate_output(result)
    if out_errors:
        print(f"❌ {gate_name} Output Validation Failed: {out_errors}")
        # print(json.dumps(result, indent=2))
        sys.exit(1)
        
    if result.get("status") == "REJECTED":
        print(f"⛔ {gate_name} REJECTED: {result.get('rejection_reasons')}")
        sys.exit(1)
        
    print(f"✅ {gate_name} PASSED")
    return result

def load_evidence(evidence_refs, key_pattern):
    for ref in evidence_refs:
        # Check source_locator for the key pattern if issue_key check fails or is ambiguous
        if key_pattern in ref.get("issue_key", "") or key_pattern in ref.get("source_locator", ""):
            path = ref.get("source_locator", "").replace("file://", "")
            # Handle potential leading slash variants
            if path.startswith("/"): path = path[1:]
            
            # Try absolute resolution
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                with open(abs_path, "r") as f:
                    return json.load(f)
            elif os.path.exists(path):
                 with open(path, "r") as f:
                    return json.load(f)
    print(f"WARNING: Evidence for '{key_pattern}' not found in {evidence_refs}")
    return {}

def main():
    # ============================================================================
    # DISABLED: 此 main 函数已被禁用，因为它调用第 2/3 批能力
    # ============================================================================
    print("=" * 76)
    print("ERROR: 此脚本已被禁用")
    print("=" * 76)
    print()
    print("此脚本 run_batch1_e2e.py 调用第 2 批和第 3 批能力，超出 T7 第 1 批范围。")
    print()
    print("第 1 批 T7 发现链的正确运行方式是:")
    print("    python scripts/run_discovery_chain.py \\")
    print("        --intent-id AUDIT_REPO_SKILL \\")
    print("        --repo-url https://github.com/genesismind-bot/GM-SkillForge \\")
    print("        --commit-sha abc123def456 \\")
    print("        --skill-dir skillforge/src/skills/quant")
    print()
    print("如需运行第 2/3 批功能，请等待后续批次实施完成。")
    print("=" * 76)
    sys.exit(1)

    # 以下代码已被禁用（保留供第 2/3 批参考）：
    DISABLED_CODE_BLOCK = """
    # ... (G1 setup omitted for brevity in diff, assume it exists) ...
    # G1 execution (T7 适配: 添加 intent_id)
    g1_input = {
        "intent_id": "AUDIT_REPO_SKILL",  # T1 新增：必须是白名单中的 intent_id
        "repo_url": "https://github.com/genesismind-bot/GM-SkillForge.git",  # 修复：使用有效 URL 而非 file:///
        "commit_sha": "a1b2c3d4e5f678901234567890abcdef12345678",
        "at_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    g1_result = run_gate("G1 Intake", GateIntakeRepo, g1_input)
    print(f"DEBUG G1 Result: {json.dumps(g1_result, indent=2, default=str)}")

    # ---------------------------------------------------------
    # 2. Scan (Fit Score)
    # ---------------------------------------------------------
    # G1 likely produced a manifest evidence
    manifest = load_evidence(g1_result.get("evidence_refs", []), "manifest")

    # Parse repo path correctly
    repo_url_clean = g1_input["repo_url"].replace("file:///", "")
    # Handle Windows drive letter potentially missing colon if urlparse used (but here simple replace)
    # If D:/GM-SkillForge, dirname is D:/ if no trailing slash.
    # We want the folder itself.
    repo_path = repo_url_clean

    g2_input = {
        "files": manifest.get("files", []),  # Extract from manifest if possible
        "intake_manifest": manifest,        # Pass full manifest
        "repo_path": repo_path
    }
    g2_result = run_gate("G2 Scan", GateRepoScanFitScore, g2_input)
    print(f"DEBUG G2 Result: {json.dumps(g2_result, indent=2, default=str)}")

    # ---------------------------------------------------------
    # 3. Draft Spec (Generate YAML) - 第 2 批能力
    # ---------------------------------------------------------
    scan_report = load_evidence(g2_result.get("evidence_refs", []), "scan_report")

    g3_input = {
        "scan_report": scan_report,
        "context": "Migrating ExperienceCapture to proper Skill"
    }
    g3_result = run_gate("G3 Draft Spec", DraftSpecGate, g3_input)  # 第 2 批
    print(f"DEBUG G3 Result: {json.dumps(g3_result, indent=2, default=str)}")

    # ---------------------------------------------------------
    # 4. Risk Check (Constitution) - 第 2 批能力
    # ---------------------------------------------------------
    spec_yaml = g3_result.get("skill_spec") or load_evidence(g3_result.get("evidence_refs", []), "spec")

    g4_input = {
        "skill_spec": spec_yaml,
        "constitution_ref": "AuditPack/constitution/v1.json"
    }
    g4_result = run_gate("G4 Risk Check", ConstitutionRiskGate, g4_input)  # 第 2 批
    print(f"DEBUG G4 Result: {json.dumps(g4_result, indent=2, default=str)}")

    # ---------------------------------------------------------
    # 5. Scaffold (Simulate Generator -> Gate Validator) - 第 2 批能力
    # ---------------------------------------------------------
    # The GateScaffoldSkill expects the ACTION to have happened.
    # We simulate the "Scaffold Agent" here.

    skill_code_path = "skillforge/src/skills/auto_drafted_skill.py"
    os.makedirs(os.path.dirname(skill_code_path), exist_ok=True)
    with open(skill_code_path, "w") as f:
        f.write("# Auto-generated skill\\ndef main():\\n    print('Hello World')\\nif __name__ == '__main__':\\n    main()")

    scaffold_payload = {
        "files_generated": [skill_code_path],
        "manifest": {
            "skill_id": "auto-drafted-skill",
            "version": "0.1.0",
            "checksum": "123456"
        }
    }

    g5_input = {
        "scaffold_skill_impl": scaffold_payload,
        "constitution_risk_gate": { "decision": "PASSED" }
    }
    g5_result = run_gate("G5 Scaffold", GateScaffoldSkill, g5_input)  # 第 2 批
    print(f"DEBUG G5 Result: {json.dumps(g5_result, indent=2, default=str)}")

    # ---------------------------------------------------------
    # 6. Sandbox (Simulate Tester -> Gate Validator) - 第 3 批能力
    # ---------------------------------------------------------
    # G5 Scaffold output should contain code_ref
    # We simulate "Sandbox Agent" executing tests.

    sandbox_payload = {
        "test_results": {
            "suites": [
                {
                    "name": "test_auto_drafted_skill",
                    "tests": 1,
                    "failures": 0,
                    "errors": 0,
                    "cases": [
                        {"name": "test_main", "status": "PASSED", "duration": 0.01}
                    ]
                }
            ],
            "summary": {"passed": 1, "failed": 0, "total": 1}
        },
        "coverage": {
            "total": 100,
            "covered": 100,
            "missed": 0,
            "report_path": "coverage.xml"
        },
        "logs": "Sandbox execution completed successfully.",
        "success": True
    }

    g6_input = {
        "sandbox_test_and_trace": sandbox_payload,
        "scaffold_skill_impl": g5_input["scaffold_skill_impl"]
    }
    g6_result = run_gate("G6 Sandbox", GateSandboxSkill, g6_input)  # 第 3 批
    print(f"DEBUG G6 Result: {json.dumps(g6_result, indent=2, default=str)}")

    # ---------------------------------------------------------
    # 7. Publish (Simulate Pack Assembler -> Gate Validator) - 第 3 批能力
    # ---------------------------------------------------------
    # Simulate "Pack Assembler Agent" creating L3 AuditPack

    audit_pack_payload = {
        "audit_id": f"AUDIT-{int(time.time())}",
        "skill_id": "auto-drafted-skill",
        "version": "0.1.0",
        "quality_level": "L3",
        "files": {
            "manifest": "manifest.json",
            "policy_matrix": "policy.json"
        }
    }

    pack_publish_payload = {
        "audit_pack": audit_pack_payload,
        "publish_result": {
            "status": "published",
            "registry_url": "http://skill-registry.local/packages/auto-drafted-skill"
        }
    }

    g7_input = {
        "pack_audit_and_publish": pack_publish_payload,
        "sandbox_test_and_trace": { "gate_decision": "PASSED", "success": True },
        # Pass all prior evidences for chaining
        "intake_repo": g1_result,
        "repo_scan_fit_score": g2_result, # Note: G2 result in script is g2_result input to G3
        "constitution_risk_gate": g4_result,
        "scaffold_skill_impl": g5_result,
        "sandbox_test_and_trace": g6_result
    }

    g7_result = run_gate("G7 Publish", GatePublishSkill, g7_input)  # 第 3 批
    print(f"DEBUG G7 Result: {json.dumps(g7_result, indent=2, default=str)}")

    print("\\n✅ Batch 1 E2E Dry-Run COMPLETED SUCCESSFULLY")
    """

if __name__ == "__main__":
    main()
