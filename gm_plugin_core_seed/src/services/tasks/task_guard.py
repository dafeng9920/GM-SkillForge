"""
Task Guard - 串线保护

Wave9: 并发骨架 - task_id guard 辅助函数
检查 task 上下文，防止请求串到错误的 task
"""
import os
from fastapi import HTTPException
from typing import Optional

from src.services.tasks.task_store_sqlite import get_task_store
from src.shared.models.task_inbox import create_task, TaskStatus
from src.services.beidou.beidou_emitter import emit_task_event


def _is_concurrency_guard_enabled() -> bool:
    """检查并发保护开关是否开启"""
    return os.environ.get("GM_OS_CONCURRENCY_GUARD_ENABLED", "0") == "1"


def check_task_context(
    task_id: Optional[str] = None,
    user_input: Optional[str] = None,
) -> Optional[str]:
    """
    检查 task 上下文

    Args:
        task_id: 请求中的 task_id（可选）
        user_input: 用户输入（用于生成默认任务标题）

    Returns:
        task_id if valid

    Raises:
        HTTPException: 当 guard 失败时（409 Conflict）
    """
    if not _is_concurrency_guard_enabled():
        return task_id  # guard 关闭，不检查

    store = get_task_store()
    active = store.get_active()

    # Case A: 无 active_task
    if not active:
        if task_id:
            # 显式指定 task_id，激活它
            task = store.get(task_id)
            if task:
                store.activate(task_id)
                emit_task_event(task_id, "ACTIVATED")
                return task_id

        # 无 active 且无 task_id：自动创建新任务
        title = (user_input or "New Task")[:100]
        new_task = create_task(title)
        new_task.status = TaskStatus.ACTIVE
        store.save(new_task)
        emit_task_event(new_task.task_id, "ACTIVATED")
        return new_task.task_id

    # Case B: 有 active_task
    if task_id:
        if task_id == active.task_id:
            # 匹配，继续
            return task_id
        else:
            # 不匹配：入 inbox + 409
            title = (user_input or "New Task")[:100]
            new_task = create_task(title)
            store.save(new_task)
            emit_task_event(new_task.task_id, "ENQUEUED")
            emit_task_event(task_id, "CONTEXT_MISSING", payload={"reason": "mismatch"})

            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "GATE.TASK_CONTEXT.MISMATCH",
                    "message": f"Task ID mismatch. Active: {active.task_id}, Provided: {task_id}",
                    "active_task_id": active.task_id,
                    "new_task_id": new_task.task_id,
                    "_meta": {
                        "signals": ["TASK_CONTEXT_MISMATCH"],
                        "task_guard": True,
                        "recoverable": True,
                    }
                }
            )
    else:
        # 无 task_id：入 inbox + 409
        title = (user_input or "New Task")[:100]
        new_task = create_task(title)
        store.save(new_task)
        emit_task_event(new_task.task_id, "ENQUEUED")
        emit_task_event(active.task_id, "CONTEXT_MISSING")

        raise HTTPException(
            status_code=409,
            detail={
                "error_code": "GATE.TASK_CONTEXT.MISSING",
                "message": "请选择任务上下文",
                "active_task_id": active.task_id,
                "new_task_id": new_task.task_id,
                "inbox_count": len(store.list_inbox()) + 1,
                "_meta": {
                    "signals": ["TASK_CONTEXT_MISSING"],
                    "task_guard": True,
                    "recoverable": True,
                }
            }
        )
