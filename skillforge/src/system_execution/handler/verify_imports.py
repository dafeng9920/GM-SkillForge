#!/usr/bin/env python3
"""
Handler Import & Connection Self-Check

验证 Handler 模块的导入和基本连接。

Usage:
    cd skillforge/src && python system_execution/handler/verify_imports.py
"""

import sys
from pathlib import Path


def add_src_to_path():
    """Add src to Python path."""
    src_path = Path(__file__).parent.parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def test_imports():
    """Test basic imports."""
    print("=== Testing Imports ===")

    try:
        from system_execution.handler import (
            HandlerInterface,
            InputAcceptance,
            CallForwarder,
        )
        print("✓ Handler module imports OK")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

    try:
        from system_execution.handler.handler_interface import (
            HandlerInput,
            ForwardTarget,
        )
        print("✓ HandlerInterface types imports OK")
    except ImportError as e:
        print(f"✗ Interface types import failed: {e}")
        return False

    return True


def test_interface_creation():
    """Test interface object creation."""
    print("\n=== Testing Interface Creation ===")

    try:
        from system_execution.handler import (
            InputAcceptance,
            CallForwarder,
        )
        from system_execution.handler.handler_interface import (
            HandlerInput,
        )

        # Create InputAcceptance
        acceptance = InputAcceptance()
        print("✓ InputAcceptance created")

        # Create CallForwarder
        forwarder = CallForwarder(acceptance)
        print("✓ CallForwarder created")

        # Create HandlerInput
        handler_input = HandlerInput(
            request_id="handler-req-001",
            source="api",
            action="query",
            payload={"key": "value"},
            evidence_ref="audit_pack:test123",
        )
        print(f"✓ HandlerInput created: {handler_input}")

        return forwarder, handler_input

    except Exception as e:
        print(f"✗ Interface creation failed: {e}")
        return None, None


def test_forwarding():
    """Test basic forwarding."""
    print("\n=== Testing Forwarding ===")

    forwarder, handler_input = test_interface_creation()
    if forwarder is None or handler_input is None:
        return False

    try:
        # Test validation
        accepted, reasons = forwarder.accept_input(handler_input)
        if accepted:
            print("✓ Input accepted")
        else:
            print(f"✗ Input rejected: {reasons}")
            return False

        # Test forwarding
        target = forwarder.forward_call(handler_input)
        print(f"✓ Forward target: {target.layer}/{target.module}/{target.method}")

        # Test context preparation
        context = forwarder.prepare_forward_context(handler_input)
        print(f"✓ Context prepared with keys: {list(context.keys())}")

        return True

    except Exception as e:
        print(f"✗ Forwarding test failed: {e}")
        return False


def test_boundary_conditions():
    """Test boundary conditions."""
    print("\n=== Testing Boundary Conditions ===")

    try:
        from system_execution.handler import InputAcceptance
        from system_execution.handler.handler_interface import (
            HandlerInput,
        )

        acceptance = InputAcceptance()

        # Test 1: Empty request_id
        input1 = HandlerInput(
            request_id="", source="api", action="query", payload={}
        )
        accepted, _ = acceptance.validate(input1)
        if not accepted:
            print("✓ Empty request_id rejected")
        else:
            print("✗ Empty request_id should be rejected")
            return False

        # Test 2: Unknown source
        input2 = HandlerInput(
            request_id="test", source="unknown", action="query", payload={}
        )
        accepted, _ = acceptance.validate(input2)
        if not accepted:
            print("✓ Unknown source rejected")
        else:
            print("✗ Unknown source should be rejected")
            return False

        # Test 3: Unknown action
        input3 = HandlerInput(
            request_id="test", source="api", action="unknown", payload={}
        )
        accepted, _ = acceptance.validate(input3)
        if not accepted:
            print("✓ Unknown action rejected")
        else:
            print("✗ Unknown action should be rejected")
            return False

        # Test 4: Valid input
        input4 = HandlerInput(
            request_id="test", source="api", action="query", payload={}
        )
        accepted, _ = acceptance.validate(input4)
        if accepted:
            print("✓ Valid input accepted")
        else:
            print("✗ Valid input should be accepted")
            return False

        return True

    except Exception as e:
        print(f"✗ Boundary test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Handler Import & Connection Self-Check")
    print("=" * 50)

    add_src_to_path()

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Interface Creation", test_interface_creation()[0] is not None))
    results.append(("Forwarding", test_forwarding()))
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
