#!/usr/bin/env python3
"""
API Layer Import Verification Script

Verifies that all API layer modules can be imported correctly.
Path: skillforge/src/system_execution/api/
"""

from __future__ import annotations
import sys
from pathlib import Path

# Add skillforge/src to path (works from any location)
script_dir = Path(__file__).resolve()
src_dir = script_dir.parent.parent  # system_execution
skillforge_src = src_dir.parent  # skillforge/src
sys.path.insert(0, str(skillforge_src))


def check_no_external_protocols() -> tuple[bool, list[str]]:
    """Check that no external web frameworks are imported."""
    # Check actual Python source files for import statements
    api_dir = script_dir.parent
    issues: list[str] = []

    for py_file in api_dir.glob("*.py"):
        if py_file.name == "verify_imports.py":
            continue  # Skip this test file

        content = py_file.read_text(encoding='utf-8')

        # Check for actual import statements (not comments)
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Skip comments and empty lines
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue

            # Check for forbidden imports (import statements only)
            forbidden_imports = [
                'import fastapi', 'from fastapi',
                'import flask', 'from flask',
                'import django', 'from django',
                'import aiohttp', 'from aiohttp',
                'import requests', 'from requests',
                'import http', 'from http',
            ]

            for forbidden in forbidden_imports:
                if forbidden in line:
                    issues.append(f"{py_file.name}:{i}: {forbidden}")

    return len(issues) == 0, issues


def verify_imports() -> bool:
    """Verify all imports work correctly."""
    print("=" * 50)
    print("API LAYER IMPORT VERIFICATION")
    print("=" * 50)
    print(f"Path: {script_dir.parent}")
    print("=" * 50)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Import api_interface
    try:
        from system_execution.api.api_interface import (
            ApiInterface,
            ApiRequest,
            ApiResponse,
            RequestContext,
        )
        print("✓ api_interface imports: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"✗ api_interface imports: FAIL - {e}")
        tests_failed += 1

    # Test 2: Import request_adapter
    try:
        from system_execution.api.request_adapter import RequestAdapter
        print("✓ request_adapter imports: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"✗ request_adapter imports: FAIL - {e}")
        tests_failed += 1

    # Test 3: Import response_builder
    try:
        from system_execution.api.response_builder import ResponseBuilder
        print("✓ response_builder imports: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"✗ response_builder imports: FAIL - {e}")
        tests_failed += 1

    # Test 4: Import package __init__
    try:
        from system_execution.api import (
            ApiInterface,
            ApiRequest,
            ApiResponse,
            RequestContext,
            RequestAdapter,
            ResponseBuilder,
        )
        print("✓ package __init__ imports: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"✗ package __init__ imports: FAIL - {e}")
        tests_failed += 1

    # Test 5: Create ApiRequest
    try:
        from system_execution.api.api_interface import ApiRequest
        req = ApiRequest(
            request_id="test",
            request_type="governance_query",
            payload={"test": True}
        )
        print(f"✓ ApiRequest creation: PASS - {req.request_id}")
        tests_passed += 1
    except Exception as e:
        print(f"✗ ApiRequest creation: FAIL - {e}")
        tests_failed += 1

    # Test 6: Create RequestContext
    try:
        from system_execution.api.api_interface import RequestContext
        ctx = RequestContext(
            request_id="test",
            source="api",
            intent="governance_query"
        )
        print(f"✓ RequestContext creation: PASS - {ctx.request_id}")
        tests_passed += 1
    except Exception as e:
        print(f"✗ RequestContext creation: FAIL - {e}")
        tests_failed += 1

    # Test 7: RequestAdapter validation
    try:
        from system_execution.api import RequestAdapter
        from system_execution.api.api_interface import ApiRequest

        adapter = RequestAdapter()
        req = ApiRequest(
            request_id="test",
            request_type="governance_query",
            payload={}
        )
        accepted, _ = adapter.validate_request_structure(req)
        if accepted:
            print("✓ RequestAdapter validation: PASS")
            tests_passed += 1
        else:
            print("✗ RequestAdapter validation: FAIL - request rejected")
            tests_failed += 1
    except Exception as e:
        print(f"✗ RequestAdapter validation: FAIL - {e}")
        tests_failed += 1

    # Test 8: ResponseBuilder
    try:
        from system_execution.api import ResponseBuilder

        builder = ResponseBuilder()
        resp = builder.build_accepted("test", {"route_target": {"layer": "handler"}})
        if resp.status == "accepted":
            print("✓ ResponseBuilder build_accepted: PASS")
            tests_passed += 1
        else:
            print(f"✗ ResponseBuilder build_accepted: FAIL - status={resp.status}")
            tests_failed += 1
    except Exception as e:
        print(f"✗ ResponseBuilder build_accepted: FAIL - {e}")
        tests_failed += 1

    # Test 9: Verify no external protocols (hard constraint check)
    try:
        clean, issues = check_no_external_protocols()
        if clean:
            print("✓ External protocol check: PASS (no web framework imports)")
            tests_passed += 1
        else:
            print(f"✗ External protocol check: FAIL - found {len(issues)} issues:")
            for issue in issues:
                print(f"    - {issue}")
            tests_failed += 1
    except Exception as e:
        print(f"✗ External protocol check: FAIL - {e}")
        tests_failed += 1

    # Summary
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Imports: {'PASS' if tests_passed >= 4 else 'FAIL'}")
    print(f"Interface Creation: {'PASS' if tests_passed >= 6 else 'FAIL'}")
    print(f"Request/Response: {'PASS' if tests_passed >= 8 else 'FAIL'}")
    print(f"Constraints: {'PASS' if tests_failed == 0 else 'FAIL'}")
    print()

    if tests_failed == 0:
        print("✓ All checks passed")
        return True
    else:
        print(f"✗ {tests_failed} checks failed")
        return False


if __name__ == "__main__":
    success = verify_imports()
    sys.exit(0 if success else 1)
