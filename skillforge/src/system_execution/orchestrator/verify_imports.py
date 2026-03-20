#!/usr/bin/env python3
"""
Orchestrator Import & Connection Self-Check

验证 Orchestrator 模块的导入和基本连接。

Usage:
    cd skillforge/src && python system_execution/orchestrator/verify_imports.py
"""

import sys
from pathlib import Path


def add_src_to_path():
    """Add src to Python path."""
    # Script at: skillforge/src/system_execution/orchestrator/verify_imports.py
    # Need to add: skillforge/src/ to path
    src_path = Path(__file__).parent.parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def test_imports():
    """Test basic imports."""
    print("=== Testing Imports ===")

    try:
        from system_execution.orchestrator import (
            InternalRouter,
            AcceptanceBoundary,
            OrchestratorInterface,
        )
        print("✓ Orchestrator module imports OK")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

    try:
        from system_execution.orchestrator.orchestrator_interface import (
            RoutingContext,
            RouteTarget,
        )
        print("✓ OrchestratorInterface types imports OK")
    except ImportError as e:
        print(f"✗ Interface types import failed: {e}")
        return False

    return True


def test_interface_creation():
    """Test interface object creation."""
    print("\n=== Testing Interface Creation ===")

    try:
        from system_execution.orchestrator import (
            AcceptanceBoundary,
            InternalRouter,
        )
        from system_execution.orchestrator.orchestrator_interface import (
            RoutingContext,
        )

        # Create AcceptanceBoundary
        acceptance = AcceptanceBoundary()
        print("✓ AcceptanceBoundary created")

        # Create InternalRouter
        router = InternalRouter(acceptance)
        print("✓ InternalRouter created")

        # Create RoutingContext
        context = RoutingContext(
            request_id="test-req-001",
            source="api",
            intent="skill_execution",
            evidence_ref="audit_pack:test123",
        )
        print(f"✓ RoutingContext created: {context}")

        return router, context

    except Exception as e:
        print(f"✗ Interface creation failed: {e}")
        return None, None


def test_routing():
    """Test basic routing."""
    print("\n=== Testing Routing ===")

    router, context = test_interface_creation()
    if router is None or context is None:
        return False

    try:
        # Test validation
        accepted, reasons = router.validate_acceptance(context)
        if accepted:
            print("✓ Request accepted")
        else:
            print(f"✗ Request rejected: {reasons}")
            return False

        # Test routing
        target = router.route_request(context)
        print(f"✓ Route target: {target.layer}/{target.module}/{target.action}")

        # Test context preparation
        enriched = router.prepare_context(context)
        print(f"✓ Context prepared with keys: {list(enriched.keys())}")

        return True

    except Exception as e:
        print(f"✗ Routing test failed: {e}")
        return False


def test_boundary_conditions():
    """Test boundary conditions."""
    print("\n=== Testing Boundary Conditions ===")

    try:
        from system_execution.orchestrator import AcceptanceBoundary
        from system_execution.orchestrator.orchestrator_interface import (
            RoutingContext,
        )

        acceptance = AcceptanceBoundary()

        # Test 1: Empty request_id
        ctx1 = RoutingContext(request_id="", source="api")
        accepted, _ = acceptance.validate(ctx1)
        if not accepted:
            print("✓ Empty request_id rejected")
        else:
            print("✗ Empty request_id should be rejected")
            return False

        # Test 2: Unknown source
        ctx2 = RoutingContext(request_id="test", source="unknown")
        accepted, _ = acceptance.validate(ctx2)
        if not accepted:
            print("✓ Unknown source rejected")
        else:
            print("✗ Unknown source should be rejected")
            return False

        # Test 3: Valid request
        ctx3 = RoutingContext(request_id="test", source="api")
        accepted, _ = acceptance.validate(ctx3)
        if accepted:
            print("✓ Valid request accepted")
        else:
            print("✗ Valid request should be accepted")
            return False

        return True

    except Exception as e:
        print(f"✗ Boundary test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Orchestrator Import & Connection Self-Check")
    print("=" * 50)

    add_src_to_path()

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Interface Creation", test_interface_creation()[0] is not None))
    results.append(("Routing", test_routing()))
    results.append(("Boundary Conditions", test_boundary_conditions()))

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{name}: {status}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n✓ All checks passed")
        return 0
    else:
        print("\n✗ Some checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
