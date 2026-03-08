"""
Spec Projections - 投影适配器

职责：
- 从 OrchestrationSpec (SSOT) 投影为 IntentMap / TaskSpecV01Frozen
- 纯函数，只读，可重复计算
- 禁止反向写回 Spec

约束：
- 投影结果必须 frozen（不可变）
- 必须 deep copy，不得共享引用
"""

from typing import Any
from copy import deepcopy


def project_intent_map(spec: Any) -> Any:
    """
    从 OrchestrationSpec 投影为 IntentMap

    Args:
        spec: OrchestrationSpec 实例

    Returns:
        IntentMap 实例（frozen，不可变）
    """
    from src.shared.models.orchestration_turn import IntentMap

    # Deep copy 所有字段
    intent_map = IntentMap(
        user_goal=spec.intent.user_goal,
        deliverable=spec.intent.deliverable,
        constraints=deepcopy(spec.intent.constraints),
        inputs=deepcopy(spec.inputs.collected),
        risk_level=spec.intent.risk_level,
    )

    # 标记为投影生成（用于 SSOT_VIOLATION guard）
    object.__setattr__(intent_map, "_from_projection", True)

    return intent_map


def project_taskspec_v01(spec: Any) -> Any:
    """
    从 OrchestrationSpec 投影为 TaskSpecV01Frozen

    Args:
        spec: OrchestrationSpec 实例

    Returns:
        TaskSpecV01Frozen 实例（frozen，不可变）
    """
    from src.shared.models.task_spec_v01_frozen import (
        TaskSpecV01Frozen,
        TaskType,
        TimeHorizon,
        AutomationLevel,
    )

    # 映射 task_type 字符串到枚举
    task_type_str = spec.contract.task_type.lower()
    task_type_map = {
        "creative": TaskType.CREATIVE,
        "automation": TaskType.AUTOMATION,
        "analysis": TaskType.ANALYSIS,
        "operational": TaskType.OPERATIONAL,
        "unknown": TaskType.OPERATIONAL,
    }
    task_type = task_type_map.get(task_type_str, TaskType.OPERATIONAL)

    # 映射 horizon 字符串到枚举
    horizon_str = spec.contract.horizon.lower()
    horizon_map = {
        "short": TimeHorizon.SINGLE_RUN,
        "single_run": TimeHorizon.SINGLE_RUN,
        "medium": TimeHorizon.MULTI_STEP,
        "multi_step": TimeHorizon.MULTI_STEP,
        "long": TimeHorizon.LONG_LIVED,
        "long_lived": TimeHorizon.LONG_LIVED,
    }
    horizon = horizon_map.get(horizon_str, TimeHorizon.SINGLE_RUN)

    # 映射 automation_level 字符串到枚举
    automation_str = spec.contract.automation_level.lower()
    automation_map = {
        "full_auto": AutomationLevel.FULL_AUTO,
        "auto": AutomationLevel.FULL_AUTO,
        "assisted": AutomationLevel.ASSISTED,
        "semi_auto": AutomationLevel.ASSISTED,
        "human_required": AutomationLevel.HUMAN_REQUIRED,
        "manual": AutomationLevel.HUMAN_REQUIRED,
    }
    automation_level = automation_map.get(automation_str, AutomationLevel.ASSISTED)

    # 构造 TaskSpecV01Frozen
    task_spec = TaskSpecV01Frozen(
        task_id=spec.spec_id,  # 复用 spec_id 作为 task_id
        user_input=spec.raw_user_input,
        task_type=task_type,
        automation_level=automation_level,
        inputs_missing=deepcopy(spec.inputs.missing),
        extracted_params=deepcopy(spec.inputs.collected),
        horizon=horizon,
        human_in_loop=deepcopy(spec.contract.human_in_loop),
        derivation_method="projection_from_spec_v2",
    )

    # 标记为投影生成
    object.__setattr__(task_spec, "_from_projection", True)

    return task_spec


def is_from_projection(obj: Any) -> bool:
    """检查对象是否由投影生成"""
    return getattr(obj, "_from_projection", False)
