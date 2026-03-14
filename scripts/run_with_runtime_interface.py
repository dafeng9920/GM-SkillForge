#!/usr/bin/env python3
"""
Run With Runtime Interface - 统一接口执行包装器

目的：让真实任务执行流开始使用 RunRequest / RunResult / ArtifactManifest

这是最小改造路径的接入点：
1. 不破坏现有主链
2. 不大规模重构
3. 只是一个轻量级包装器，可以集成到任何执行流中

Usage:
    # 方式1：命令行调用
    python scripts/run_with_runtime_interface.py \
        --task-id TASK-MAIN-02 \
        --executor Antigravity-1 \
        --objective "接入统一接口" \
        --command "echo test"

    # 方式2：作为模块调用
    from scripts.run_with_runtime_interface import run_with_runtime_interface
    result = run_with_runtime_interface(
        task_id="TASK-MAIN-02",
        executor="Antigravity-1",
        objective="接入统一接口",
        command=["echo", "test"]
    )

    # 方式3：在现有脚本中集成
    from scripts.run_with_runtime_interface import RuntimeExecutionWrapper
    wrapper = RuntimeExecutionWrapper("TASK-MAIN-02", "Antigravity-1")
    request = wrapper.create_request("接入统一接口")
    wrapper.start_run()
    # ... 执行逻辑 ...
    result = wrapper.complete_run(status=RunStatus.SUCCESS)
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Optional

# 添加项目路径
PROJECT_ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入统一接口
from core.runtime_interface import (
    RunRequest,
    RunResult,
    ArtifactManifest,
    RuntimeSession,
    RunStatus,
    ArtifactKind,
    EvidenceRef,
)


# =============================================================================
# RuntimeExecutionWrapper - 执行包装器
# =============================================================================

class RuntimeExecutionWrapper:
    """
    执行包装器 - 将统一接口接入实际执行流

    这是一个轻量级包装器，可以：
    1. 包装任何命令执行
    2. 自动生成 RunRequest / RunResult / ArtifactManifest
    3. 与现有主链无缝集成
    """

    def __init__(
        self,
        task_id: str,
        executor: str,
        output_dir: Optional[pathlib.Path] = None,
    ):
        """
        初始化执行包装器

        Args:
            task_id: 任务标识
            executor: 执行者标识
            output_dir: 输出目录（默认为 dropzone/{task_id}）
        """
        self.task_id = task_id
        self.executor = executor
        self.output_dir = output_dir or pathlib.Path(f"dropzone/{task_id}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 创建 RuntimeSession
        self.session = RuntimeSession(
            task_id=task_id,
            executor=executor,
            base_path=PROJECT_ROOT,
        )

        # 记录执行命令
        self.executed_commands: list[str] = []

    def create_request(
        self,
        objective: str,
        parameters: Optional[dict[str, Any]] = None,
        constraints: Optional[dict[str, Any]] = None,
        contract_ref: Optional[str] = None,
        permit_ref: Optional[str] = None,
    ) -> RunRequest:
        """创建执行请求"""
        request = self.session.create_request(
            objective=objective,
            parameters=parameters or {},
            constraints=constraints or {},
            contract_ref=contract_ref,
            permit_ref=permit_ref,
        )

        # 保存请求到文件
        self._save_json("run_request.json", request.to_dict())
        return request

    def start_run(self) -> str:
        """开始执行"""
        started_at = self.session.start_run()
        return started_at

    def run_command(
        self,
        command: list[str] | str,
        cwd: Optional[pathlib.Path] = None,
        env: Optional[dict[str, str]] = None,
    ) -> subprocess.CompletedProcess:
        """
        执行命令并记录

        Args:
            command: 要执行的命令（列表或字符串）
            cwd: 工作目录
            env: 环境变量

        Returns:
            subprocess.CompletedProcess
        """
        if isinstance(command, str):
            command_str = command
            command = ["sh", "-c", command]
        else:
            command_str = " ".join(command)

        print(f"[EXEC] {command_str}")
        self.executed_commands.append(command_str)

        result = subprocess.run(
            command,
            cwd=cwd or PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

        # 记录输出
        if result.stdout:
            print(f"[STDOUT] {result.stdout[:200]}...")
        if result.stderr:
            print(f"[STDERR] {result.stderr[:200]}...")

        return result

    def add_artifact(
        self,
        path: str,
        kind: ArtifactKind = ArtifactKind.OTHER,
        content_hash: Optional[str] = None,
    ) -> None:
        """添加工件到清单"""
        manifest = self.session.manifest
        if manifest is None:
            manifest = self.session.create_manifest()

        # 计算文件 hash
        if content_hash is None:
            file_path = pathlib.Path(path)
            if file_path.exists():
                import hashlib
                content = file_path.read_bytes()
                content_hash = "sha256:" + hashlib.sha256(content).hexdigest()

        manifest.add_artifact(path, kind, content_hash)

    def add_evidence(
        self,
        path: str,
        content_hash: Optional[str] = None,
    ) -> None:
        """添加证据到清单"""
        manifest = self.session.manifest
        if manifest is None:
            manifest = self.session.create_manifest()

        # 计算文件 hash
        if content_hash is None:
            file_path = pathlib.Path(path)
            if file_path.exists():
                import hashlib
                content = file_path.read_bytes()
                content_hash = "sha256:" + hashlib.sha256(content).hexdigest()

        manifest.add_evidence(path, content_hash)

    def complete_run(
        self,
        status: RunStatus,
        summary: str = "",
        exit_code: Optional[int] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        save_manifest: bool = True,
    ) -> RunResult:
        """
        完成执行，生成结果

        Args:
            status: 执行状态
            summary: 执行摘要
            exit_code: 退出码
            error_code: 错误码
            error_message: 错误消息
            save_manifest: 是否保存清单

        Returns:
            RunResult
        """
        result = self.session.complete_run(
            status=status,
            summary=summary,
            executed_commands=self.executed_commands,
            exit_code=exit_code,
            error_code=error_code,
            error_message=error_message,
        )

        # 保存结果
        self._save_json("run_result.json", result.to_dict())

        # 保存清单
        if save_manifest and result.manifest:
            self._save_json("artifact_manifest.json", result.manifest.to_dict())

        return result

    def _save_json(self, filename: str, data: dict[str, Any]) -> None:
        """保存 JSON 到输出目录"""
        output_path = self.output_dir / filename
        output_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"[SAVED] {output_path}")


# =============================================================================
# 便捷函数
# =============================================================================

def run_with_runtime_interface(
    task_id: str,
    executor: str,
    objective: str,
    command: list[str] | str,
    parameters: Optional[dict[str, Any]] = None,
    constraints: Optional[dict[str, Any]] = None,
    contract_ref: Optional[str] = None,
    permit_ref: Optional[str] = None,
    output_dir: Optional[pathlib.Path] = None,
) -> RunResult:
    """
    使用统一接口执行命令

    这是主链任务执行的标准入口点。

    Args:
        task_id: 任务标识
        executor: 执行者标识
        objective: 执行目标
        command: 要执行的命令
        parameters: 执行参数
        constraints: 约束条件
        contract_ref: 合同引用
        permit_ref: 许可引用
        output_dir: 输出目录

    Returns:
        RunResult
    """
    wrapper = RuntimeExecutionWrapper(task_id, executor, output_dir)

    # 创建请求
    wrapper.create_request(
        objective=objective,
        parameters=parameters,
        constraints=constraints,
        contract_ref=contract_ref,
        permit_ref=permit_ref,
    )

    # 开始执行
    wrapper.start_run()

    # 执行命令
    proc = wrapper.run_command(command)

    # 完成执行
    if proc.returncode == 0:
        result = wrapper.complete_run(
            status=RunStatus.SUCCESS,
            summary=f"命令执行成功: {command}",
            exit_code=proc.returncode,
        )
    else:
        result = wrapper.complete_run(
            status=RunStatus.FAILURE,
            summary=f"命令执行失败: {command}",
            exit_code=proc.returncode,
            error_code="COMMAND_FAILED",
            error_message=proc.stderr or "命令执行失败",
        )

    return result


# =============================================================================
# CLI 入口点
# =============================================================================

def main() -> int:
    """CLI 入口点"""
    parser = argparse.ArgumentParser(
        description="Run With Runtime Interface - 统一接口执行包装器"
    )
    parser.add_argument("--task-id", required=True, help="任务标识")
    parser.add_argument("--executor", required=True, help="执行者标识")
    parser.add_argument("--objective", required=True, help="执行目标")
    parser.add_argument(
        "--command",
        required=True,
        help="要执行的命令（字符串或列表，用空格分隔）"
    )
    parser.add_argument("--contract-ref", help="合同引用")
    parser.add_argument("--permit-ref", help="许可引用")
    parser.add_argument(
        "--output-dir",
        type=pathlib.Path,
        help="输出目录（默认: dropzone/{task_id}）"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只生成请求，不执行命令"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("RUN WITH RUNTIME INTERFACE")
    print("=" * 60)
    print(f"Task ID: {args.task_id}")
    print(f"Executor: {args.executor}")
    print(f"Objective: {args.objective}")
    print(f"Command: {args.command}")
    print("=" * 60)
    print()

    # 解析命令
    command_parts = args.command.split()
    command: list[str] | str = command_parts if len(command_parts) > 1 else args.command

    if args.dry_run:
        # 只创建请求
        wrapper = RuntimeExecutionWrapper(args.task_id, args.executor, args.output_dir)
        wrapper.create_request(
            objective=args.objective,
            contract_ref=args.contract_ref,
            permit_ref=args.permit_ref,
        )
        print("\n[DRY RUN] 请求已创建，未执行命令")
        return 0

    # 执行
    result = run_with_runtime_interface(
        task_id=args.task_id,
        executor=args.executor,
        objective=args.objective,
        command=command,
        contract_ref=args.contract_ref,
        permit_ref=args.permit_ref,
        output_dir=args.output_dir,
    )

    # 输出结果
    print()
    print("=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"Status: {result.status.value}")
    print(f"Summary: {result.summary}")
    print(f"Exit Code: {result.exit_code}")
    print(f"Executed Commands: {len(result.executed_commands)}")
    print()

    return 0 if result.is_success else 1


if __name__ == "__main__":
    sys.exit(main())
