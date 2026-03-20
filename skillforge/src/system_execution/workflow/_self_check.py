"""
Workflow Self-Check - 最小导入/连接自检

> PREPARATION 级别自检脚本
> T1 返工: 路径已从 system_execution_preparation 迁移到 system_execution

检查内容:
1. 模块导入是否正确
2. 协议类型是否定义
3. 无运行时依赖
4. 连接接口是否完整
5. 正确的模块路径
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Tuple


# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class SelfCheckResult:
    """自检结果"""
    def __init__(self) -> None:
        self.passed: List[str] = []
        self.failed: List[Tuple[str, str]] = []  # (check_name, reason)
        self.warnings: List[str] = []

    def add_pass(self, check_name: str) -> None:
        self.passed.append(check_name)

    def add_fail(self, check_name: str, reason: str) -> None:
        self.failed.append((check_name, reason))

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def print_report(self) -> None:
        """打印自检报告"""
        print("=" * 60)
        print("Workflow Self-Check Report (T1 返工)")
        print("=" * 60)
        print()

        # Passed checks
        if self.passed:
            print("✓ PASSED:")
            for check in self.passed:
                print(f"  ✓ {check}")
            print()

        # Failed checks
        if self.failed:
            print("✗ FAILED:")
            for check, reason in self.failed:
                print(f"  ✗ {check}: {reason}")
            print()

        # Warnings
        if self.warnings:
            print("⚠ WARNINGS:")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")
            print()

        # Summary
        total = len(self.passed) + len(self.failed)
        passed_count = len(self.passed)
        print("=" * 60)
        print(f"Summary: {passed_count}/{total} checks passed")
        print("=" * 60)


def check_imports() -> SelfCheckResult:
    """检查模块导入 (新路径)"""
    result = SelfCheckResult()

    # 检查 workflow 模块导入 - 新路径
    try:
        from skillforge.src.system_execution.workflow import (
            WorkflowContext,
            WorkflowEntry,
            StageResult,
            WorkflowOrchestrator,
        )
        result.add_pass("Workflow module imports (new path)")
    except ImportError as e:
        result.add_fail("Workflow module imports", str(e))
        return result

    # 检查各子模块 - 新路径
    try:
        from skillforge.src.system_execution.workflow.entry import WorkflowEntry
        result.add_pass("WorkflowEntry imported (new path)")
    except ImportError as e:
        result.add_fail("WorkflowEntry import", str(e))

    try:
        from skillforge.src.system_execution.workflow.orchestration import WorkflowOrchestrator
        result.add_pass("WorkflowOrchestrator imported (new path)")
    except ImportError as e:
        result.add_fail("WorkflowOrchestrator import", str(e))

    return result


def check_protocols() -> SelfCheckResult:
    """检查协议类型定义"""
    result = SelfCheckResult()

    try:
        from skillforge.src.system_execution.workflow.entry import WorkflowContext
        result.add_pass("WorkflowContext protocol defined")
    except ImportError as e:
        result.add_fail("WorkflowContext protocol", str(e))

    try:
        from skillforge.src.system_execution.workflow.orchestration import StageResult
        result.add_pass("StageResult protocol defined")
    except ImportError as e:
        result.add_fail("StageResult protocol", str(e))

    return result


def check_no_runtime_deps() -> SelfCheckResult:
    """检查无运行时依赖"""
    result = SelfCheckResult()

    # 检查方法是否会抛出 NotImplementedError
    try:
        from skillforge.src.system_execution.workflow.entry import WorkflowEntry

        entry = WorkflowEntry()
        # 尝试调用 route 方法，应该抛出 NotImplementedError
        try:
            from skillforge.src.system_execution.workflow.entry import WorkflowContext
            # 创建一个简单的 context 对象进行测试
            class MockContext:
                request_id = "test"
                payload = {}
                metadata = None

            entry.route(MockContext())  # type: ignore
            result.add_fail("Runtime enforcement", "route() should raise NotImplementedError")
        except NotImplementedError:
            result.add_pass("Runtime enforcement (route raises NotImplementedError)")
    except Exception as e:
        result.add_fail("Runtime enforcement check", str(e))

    return result


def check_file_structure() -> SelfCheckResult:
    """检查文件结构"""
    result = SelfCheckResult()

    workflow_dir = Path(__file__).parent

    required_files = [
        "__init__.py",
        "entry.py",
        "orchestration.py",
        "WORKFLOW_RESPONSIBILITIES.md",
        "CONNECTIONS.md",
        "_self_check.py",
    ]

    for file_name in required_files:
        file_path = workflow_dir / file_name
        if file_path.exists():
            result.add_pass(f"File exists: {file_name}")
        else:
            result.add_fail(f"File exists: {file_name}", "File not found")

    return result


def check_module_path() -> SelfCheckResult:
    """检查模块路径是否正确"""
    result = SelfCheckResult()

    workflow_dir = Path(__file__).parent
    expected_path = "skillforge/src/system_execution/workflow"
    actual_path = str(workflow_dir).replace("\\", "/")

    if actual_path.endswith(expected_path):
        result.add_pass(f"Correct module path: {expected_path}")
    else:
        result.add_fail("Module path verification", f"Expected {expected_path}, got {actual_path}")

    return result


def main() -> int:
    """运行自检"""
    print("Running Workflow Self-Check (T1 返工 - 新路径)...")
    print()

    final_result = SelfCheckResult()

    # 运行各项检查
    for check_fn in [check_imports, check_protocols, check_no_runtime_deps, check_file_structure, check_module_path]:
        check_result = check_fn()
        final_result.passed.extend(check_result.passed)
        final_result.failed.extend(check_result.failed)
        final_result.warnings.extend(check_result.warnings)

    # 打印报告
    final_result.print_report()

    # 返回退出码
    return 0 if not final_result.failed else 1


if __name__ == "__main__":
    sys.exit(main())
