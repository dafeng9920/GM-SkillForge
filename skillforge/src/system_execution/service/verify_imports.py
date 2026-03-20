"""
Service Layer - 导入/连接自检脚本

验证 Service 层与 Orchestrator 层的连接状态。
"""

from __future__ import annotations

import sys
from pathlib import Path


def check_service_imports() -> tuple[bool, list[str]]:
    """
    检查 Service 层导入状态。

    Returns:
        (success, issues) 元组
    """
    issues: list[str] = []

    # 1. 检查 Service 层导入
    try:
        from skillforge.src.system_execution.service import (
            ServiceInterface,
            BaseService,
        )
        print("✓ Service 层导入 OK")
        print(f"  - ServiceInterface: {ServiceInterface}")
        print(f"  - BaseService: {BaseService}")
    except ImportError as e:
        issues.append(f"Service 层导入失败: {e}")
        print(f"✗ Service 层导入失败: {e}")
        return False, issues

    # 2. 检查 ServiceInterface 实例化
    try:
        service = BaseService()
        print("✓ BaseService 实例化 OK")
    except Exception as e:
        issues.append(f"BaseService 实例化失败: {e}")
        print(f"✗ BaseService 实例化失败: {e}")
        return False, issues

    # 3. 检查服务信息获取
    try:
        info = service.get_service_info()
        print(f"✓ get_service_info() OK: {info}")
    except Exception as e:
        issues.append(f"get_service_info() 失败: {e}")
        print(f"✗ get_service_info() 失败: {e}")
        return False, issues

    # 4. 检查上下文验证
    try:
        # 有效上下文
        valid_context = {
            "request_id": "test-123",
            "source": "api",
            "intent": "skill_execution",
            "route_target": {
                "layer": "service",
                "module": "skill_service",
                "action": "execute"
            },
            "routing_decision": "internal_router"
        }
        valid, reasons = service.validate_context(valid_context)
        if valid:
            print(f"✓ validate_context(有效) 通过")
        else:
            issues.append(f"validate_context(有效) 失败: {reasons}")
            print(f"✗ validate_context(有效) 失败: {reasons}")

        # 无效上下文
        invalid_context = {}
        valid, reasons = service.validate_context(invalid_context)
        if not valid:
            print(f"✓ validate_context(无效) 正确拒绝: {reasons}")
        else:
            issues.append("validate_context(无效) 应该拒绝但通过了")
            print(f"✗ validate_context(无效) 应该拒绝但通过了")
    except Exception as e:
        issues.append(f"validate_context() 异常: {e}")
        print(f"✗ validate_context() 异常: {e}")
        return False, issues

    # 5. 检查只读依赖声明
    try:
        deps = service.get_read_dependencies()
        print(f"✓ get_read_dependencies() OK: {deps}")
    except Exception as e:
        issues.append(f"get_read_dependencies() 失败: {e}")
        print(f"✗ get_read_dependencies() 失败: {e}")
        return False, issues

    # 6. 检查与 Orchestrator 层的连接（如果存在）
    try:
        from skillforge.src.system_execution.orchestrator import (
            InternalRouter,
            AcceptanceBoundary,
        )
        from skillforge.src.system_execution.orchestrator.orchestrator_interface import (
            RoutingContext,
        )
        print("✓ Orchestrator 层导入 OK")

        # 模拟完整的连接流程
        router = InternalRouter(AcceptanceBoundary())
        context = RoutingContext(
            request_id="test-conn-123",
            source="api",
            intent="skill_execution",
            evidence_ref="audit_pack:test123"
        )

        # Orchestrator 处理
        accepted, _ = router.validate_acceptance(context)
        if accepted:
            print("✓ Orchestrator.acceptance 验证通过")
        else:
            issues.append("Orchestrator.acceptance 验证失败")
            print("✗ Orchestrator.acceptance 验证失败")

        target = router.route_request(context)
        print(f"✓ Orchestrator.route_request: {target}")

        enriched = router.prepare_context(context)
        print(f"✓ Orchestrator.prepare_context: {enriched.keys()}")

        # Service 接收
        service_valid, service_reasons = service.validate_context(enriched)
        if service_valid:
            print("✓ Service 接收 Orchestrator 上下文成功")
        else:
            issues.append(f"Service 拒绝 Orchestrator 上下文: {service_reasons}")
            print(f"✗ Service 拒绝 Orchestrator 上下文: {service_reasons}")

    except ImportError as e:
        print(f"⚠ Orchestrator 层导入失败（可能未实现）: {e}")
    except Exception as e:
        issues.append(f"Orchestrator 连接测试异常: {e}")
        print(f"✗ Orchestrator 连接测试异常: {e}")

    return len(issues) == 0, issues


def check_constraints() -> tuple[bool, list[str]]:
    """
    检查硬约束是否满足。

    Returns:
        (compliant, violations) 元组
    """
    violations: list[str] = []

    from skillforge.src.system_execution.service import BaseService

    service = BaseService()
    info = service.get_service_info()

    # 约束 1: 无业务逻辑实现
    if info.get("has_business_logic", True):
        violations.append("约束违反: has_business_logic 应为 False")
    else:
        print("✓ 约束 1: 无业务逻辑实现")

    # 约束 2: 只读 frozen
    if not info.get("reads_frozen_only", False):
        violations.append("约束违反: reads_frozen_only 应为 True")
    else:
        print("✓ 约束 2: 只读 frozen 对象")

    # 约束 3: 接受上下文
    if not info.get("accepts_context", False):
        violations.append("约束违反: accepts_context 应为 True")
    else:
        print("✓ 约束 3: 接受 orchestrator 上下文")

    return len(violations) == 0, violations


def main():
    """运行所有自检。"""
    print("=" * 60)
    print("Service Layer - 导入/连接自检")
    print("=" * 60)

    print("\n[1] 导入检查")
    print("-" * 40)
    import_success, import_issues = check_service_imports()

    print("\n[2] 硬约束检查")
    print("-" * 40)
    constraint_success, constraint_violations = check_constraints()

    # 汇总结果
    print("\n" + "=" * 60)
    print("自检结果汇总")
    print("=" * 60)

    all_issues = import_issues + constraint_violations

    if len(all_issues) == 0:
        print("✓ 所有检查通过")
        return 0
    else:
        print(f"✗ 发现 {len(all_issues)} 个问题:")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
