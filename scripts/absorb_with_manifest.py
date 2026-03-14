#!/usr/bin/env python3
"""
Absorb with Manifest - 使用统一接口的 absorb 扩展

目的：让真实执行入口（absorb流程）开始使用统一接口

这是对现有 absorb.sh 的最小扩展：
1. 读取 dropzone manifest.json
2. 使用 ArtifactManifest 记录工件
3. 复制文件到 docs 根目录
4. 生成 RunResult 记录执行结果

与现有 absorb.sh 的区别：
- 现有：只复制文件，输出简单的 JSON
- 扩展：使用 ArtifactManifest 和 RunResult 记录执行过程

Usage:
    python scripts/absorb_with_manifest.py REAL-TASK-002
    python scripts/absorb_with_manifest.py REAL-TASK-002 --output-dir docs/2026-03-11
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import sys
from datetime import datetime, timezone
from typing import Any

# 添加项目路径
PROJECT_ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入统一接口
from core.runtime_interface import (
    ArtifactManifest,
    ArtifactKind,
    RunResult,
    RunStatus,
    EvidenceRef,
)


def calculate_file_hash(path: pathlib.Path) -> str:
    """计算文件的 SHA256 hash"""
    content = path.read_bytes()
    return "sha256:" + hashlib.sha256(content).hexdigest()


def absorb_with_manifest(
    task_id: str,
    dropzone_root: pathlib.Path,
    docs_root: pathlib.Path,
    executor: str = "absorb_with_manifest.py",
) -> RunResult:
    """
    使用统一接口执行 absorb

    Args:
        task_id: 任务标识
        dropzone_root: dropzone 根目录
        docs_root: docs 根目录
        executor: 执行者标识

    Returns:
        RunResult
    """
    started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    task_root = dropzone_root / task_id
    manifest_path = task_root / "manifest.json"

    # 读取 manifest
    if not manifest_path.exists():
        return RunResult.failure_result(
            task_id=task_id,
            run_id=f"{task_id}-ABSORB",
            executor=executor,
            started_at=started_at,
            finished_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            error_code="MANIFEST_NOT_FOUND",
            error_message=f"manifest.json not found: {manifest_path}",
        )

    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))

    # 创建 ArtifactManifest（使用统一接口）
    artifact_manifest = ArtifactManifest(
        task_id=task_id,
        run_id=f"{task_id}-ABSORB",
        schema_version="runtime_interface_v0.1",
        env=manifest_data.get("env", {}),
    )

    # 目标目录
    dest_root = docs_root / task_id
    dest_root.mkdir(parents=True, exist_ok=True)

    # 复制 artifacts
    artifacts = manifest_data.get("artifacts", [])
    for rel_path in artifacts:
        src = (task_root / rel_path).resolve()
        dest = (dest_root / rel_path).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

        # 使用统一接口记录工件
        artifact_manifest.add_artifact(
            path=rel_path,
            kind=_infer_artifact_kind(rel_path),
            content_hash=calculate_file_hash(dest),
            size_bytes=dest.stat().st_size,
        )

    # 复制 evidence
    evidence = manifest_data.get("evidence", [])
    for rel_path in evidence:
        src = (task_root / rel_path).resolve()
        dest = (dest_root / rel_path).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

        # 使用统一接口记录证据
        artifact_manifest.add_evidence(
            path=rel_path,
            content_hash=calculate_file_hash(dest),
            size_bytes=dest.stat().st_size,
        )

    # 保存 ArtifactManifest（使用统一接口格式）
    manifest_output = dest_root / "artifact_manifest.json"
    manifest_output.write_text(
        json.dumps(artifact_manifest.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # 创建 RunResult（使用统一接口）
    finished_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    result = RunResult(
        task_id=task_id,
        run_id=f"{task_id}-ABSORB",
        executor=executor,
        status=RunStatus.SUCCESS,
        started_at=started_at,
        finished_at=finished_at,
        schema_version="runtime_interface_v0.1",
        executed_commands=[f"absorb_with_manifest.py {task_id}"],
        exit_code=0,
        summary=f"Absorbed {len(artifacts)} artifacts and {len(evidence)} evidence items",
        manifest=artifact_manifest,
        evidence_refs=[
            EvidenceRef(
                issue_key=task_id,
                source_locator=str(dest_root),
                content_hash=calculate_file_hash(manifest_output),
                tool_revision="runtime_interface_v0.1",
                timestamp=finished_at,
                kind="FILE",
            )
        ],
    )

    # 保存 RunResult（使用统一接口格式）
    result_output = dest_root / "run_result.json"
    result_output.write_text(
        json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return result


def _infer_artifact_kind(path: str) -> ArtifactKind:
    """根据文件路径推断工件类型"""
    path_lower = path.lower()
    if "blueprint" in path_lower or "design" in path_lower:
        return ArtifactKind.BLUEPRINT
    elif "contract" in path_lower:
        return ArtifactKind.CONTRACT
    elif path_lower.endswith((".py", ".js", ".ts", ".sh", ".yml", ".yaml")):
        return ArtifactKind.CODE
    elif "test" in path_lower:
        return ArtifactKind.TEST
    elif "config" in path_lower or path_lower.endswith((".json", ".yaml", ".yml", ".toml")):
        return ArtifactKind.CONFIG
    elif path_lower.endswith((".md", ".txt", ".rst")):
        return ArtifactKind.DOCUMENTATION
    else:
        return ArtifactKind.OTHER


def main() -> int:
    """CLI 入口点"""
    parser = argparse.ArgumentParser(
        description="Absorb with Manifest - 使用统一接口的 absorb 扩展"
    )
    parser.add_argument("task_id", help="任务标识")
    parser.add_argument(
        "--dropzone-root",
        type=pathlib.Path,
        default=pathlib.Path("dropzone"),
        help="dropzone 根目录"
    )
    parser.add_argument(
        "--docs-root",
        type=pathlib.Path,
        default=pathlib.Path("docs"),
        help="docs 根目录"
    )
    parser.add_argument(
        "--executor",
        default="absorb_with_manifest.py",
        help="执行者标识"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("ABSORB WITH MANIFEST")
    print("=" * 60)
    print(f"Task ID: {args.task_id}")
    print(f"Dropzone Root: {args.dropzone_root}")
    print(f"Docs Root: {args.docs_root}")
    print("=" * 60)
    print()

    # 执行 absorb（使用统一接口）
    result = absorb_with_manifest(
        task_id=args.task_id,
        dropzone_root=args.dropzone_root,
        docs_root=args.docs_root,
        executor=args.executor,
    )

    # 输出结果
    print()
    print("=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"Status: {result.status.value}")
    print(f"Summary: {result.summary}")
    print(f"Artifacts: {len(result.manifest.artifacts) if result.manifest else 0}")
    print(f"Evidence: {len(result.manifest.evidence) if result.manifest else 0}")
    print()

    if result.manifest:
        print("[Artifact Manifest]")
        print(f"  Output: {args.docs_root}/{args.task_id}/artifact_manifest.json")
        print(f"  Schema Version: {result.manifest.schema_version}")
        print()

    print("[Run Result]")
    print(f"  Output: {args.docs_root}/{args.task_id}/run_result.json")
    print(f"  Schema Version: {result.schema_version}")
    print()

    return 0 if result.is_success else 1


if __name__ == "__main__":
    sys.exit(main())
