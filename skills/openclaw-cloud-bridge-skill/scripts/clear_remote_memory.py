#!/usr/bin/env python3
"""
OpenClaw 远端记忆清理任务生成器
生成清理 sessions/ 和 memory/ 的任务合同
"""

import json
import hashlib
import argparse
from datetime import datetime, timezone
from pathlib import Path


def generate_clear_memory_contract(project_dir: str = "/root/openclaw-box"):
    """生成清理记忆的任务合同"""

    task_id = f"clear-memory-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    created_at = datetime.now(timezone.utc).isoformat() + "Z"

    contract = {
        "schema_version": "1.0.0",
        "task_id": task_id,
        "created_at_utc": created_at,
        "objective": "清理 OpenClaw 远端记忆库 (sessions + memory) 以释放空间",
        "relay": {
            "agent": "Antigravity-Gemini",
            "channel": "BlueLobster-Cloud"
        },
        "target": {
            "project_dir": project_dir
        },
        "policy": {
            "fail_closed": True,
            "max_duration_sec": 300,
            "max_commands": 8
        },
        "command_allowlist": [
            # 检查当前状态
            f"cd {project_dir} && du -sh data/agents/main/sessions data/memory",
            f"cd {project_dir} && ls -lh data/agents/main/sessions/*.jsonl | tail -10",

            # 停止服务（安全起见）
            f"cd {project_dir} && docker compose stop openclaw-agent",

            # 备份当前状态
            f"cd {project_dir} && mkdir -p data/.backup/before_clear_{task_id}",
            f"cd {project_dir} && cp -a data/agents/main/sessions data/.backup/before_clear_{task_id}/",
            f"cd {project_dir} && cp -a data/memory data/.backup/before_clear_{task_id}/memory_backup",

            # 清理 sessions
            f"cd {project_dir} && rm -f data/agents/main/sessions/*.jsonl",

            # 清理 memory（保留结构，重置数据库）
            f"cd {project_dir} && rm -f data/memory/main.sqlite*",
            f"cd {project_dir} && mkdir -p data/memory",

            # 重启服务
            f"cd {project_dir} && docker compose start openclaw-agent",
            f"cd {project_dir} && docker compose logs --since 30s openclaw-agent"
        ],
        "acceptance": [
            "sessions directory is empty or contains only reset markers",
            "memory/main.sqlite files are removed",
            "docker compose shows openclaw-agent is running",
            "no EACCES or critical errors in logs"
        ],
        "required_artifacts": [
            "execution_receipt.json",
            "stdout.log",
            "stderr.log"
        ]
    }

    # 计算 contract_sha256
    contract_str = json.dumps(contract, sort_keys=True, ensure_ascii=False)
    contract_sha256 = hashlib.sha256(contract_str.encode()).hexdigest()
    contract["contract_sha256"] = contract_sha256

    return contract, task_id


def main():
    parser = argparse.ArgumentParser(description="生成 OpenClaw 远端记忆清理任务合同")
    parser.add_argument("--project-dir", default="/root/openclaw-box", help="远端项目目录")
    parser.add_argument("--output-dir", default=".tmp/openclaw-dispatch", help="输出目录")

    args = parser.parse_args()

    # 生成合同
    contract, task_id = generate_clear_memory_contract(args.project_dir)

    # 创建输出目录
    output_dir = Path(args.output_dir) / task_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # 写入合同
    contract_path = output_dir / "task_contract.json"
    with open(contract_path, "w", encoding="utf-8") as f:
        json.dump(contract, f, indent=2, ensure_ascii=False)

    # 生成交接说明
    handover_note = f"""# OpenClaw 远端记忆清理任务

## 任务 ID
{task_id}

## 目标
清理 OpenClaw 远端记忆库以释放空间，防止因巨型文件撑爆上下文。

## 执行要求
1. 严格按照 `command_allowlist` 顺序执行
2. 禁止执行任何白名单外的命令
3. 每步执行后记录输出
4. 必须回传所有 required_artifacts

## 验收标准
{chr(10).join(f'- {c}' for c in contract['acceptance'])}

## 合同哈希
{contract['contract_sha256']}

---
生成时间: {contract['created_at_utc']}
"""

    handover_path = output_dir / "handoff_note.md"
    with open(handover_path, "w", encoding="utf-8") as f:
        f.write(handover_note)

    print(f"[OK] 任务合同已生成:")
    print(f"     合同: {contract_path}")
    print(f"     说明: {handover_path}")
    print(f"[NEXT] 将以上两个文件交给 Gemini，要求其按合同执行")


if __name__ == "__main__":
    main()
