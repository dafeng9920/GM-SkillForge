"""
Meta Builder Service for Wave 1 Observability

职责：
1. 组装 ResponseMeta 对象
2. 计算 spec_changed / decision_changed
3. 检测 POLICY_DECISION_DRIFT 信号

约束：
- 不修改任何 spec/turn/store 真值
- 仅做对比和计算
- 信号由开关控制
"""
import os
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.shared.models.response_meta import (
    SpecRef,
    ResponseMeta,
    create_spec_ref,
    create_response_meta,
)
from src.services.orchestration.decision_hash import (
    compute_decision_hash,
    compute_decision_hash_struct,
)


# 开关
def _is_drift_signal_enabled() -> bool:
    return os.environ.get("GM_OS_DRIFT_SIGNAL_ENABLED", "0") == "1"


def _is_meta_enabled() -> bool:
    return os.environ.get("GM_OS_META_ENABLED", "0") == "1"


class MetaBuilder:
    """
    ResponseMeta 构建器

    Usage:
        builder = MetaBuilder()
        meta = builder.build(
            spec_ref=spec_ref,
            decision_payload=turn_data,
            prev_meta=previous_turn_meta,
            evidence_pack_ref="pack-001",
            session_id="session-1",
            turn_id="turn-1",
        )
    """

    def __init__(self):
        self._enabled = _is_meta_enabled()

    def build(
        self,
        spec_ref: SpecRef,
        decision_payload: Dict[str, Any],
        prev_meta: Optional[ResponseMeta] = None,
        evidence_pack_ref: Optional[str] = None,
        session_id: str = "",
        turn_id: str = "",
    ) -> ResponseMeta:
        """
        构建 ResponseMeta

        Args:
            spec_ref: 当前 spec 引用
            decision_payload: 决策负载（用于计算 decision_hash）
            prev_meta: 上一轮的 meta（用于计算 changed 标志）
            evidence_pack_ref: 证据包引用
            session_id: 会话 ID
            turn_id: 轮次 ID

        Returns:
            ResponseMeta 对象
        """
        # 1. 计算 decision_hash
        decision_struct, decision_hash = compute_decision_hash_struct(decision_payload)

        # 2. 生成 trace_id
        trace_id = f"{session_id}:{turn_id}" if session_id and turn_id else str(uuid.uuid4())

        # 3. 计算 changed 标志
        spec_changed = False
        decision_changed = False

        if prev_meta:
            # spec_changed: 比较 spec_hash
            spec_changed = prev_meta.spec_ref.spec_hash != spec_ref.spec_hash

            # decision_changed: 比较 decision_hash
            decision_changed = prev_meta.decision_hash != decision_hash

        # 4. 检测信号
        signals = self._detect_signals(
            spec_changed=spec_changed,
            decision_changed=decision_changed,
            prev_meta=prev_meta,
            curr_decision_hash=decision_hash,
        )

        # 5. 组装 ResponseMeta
        return create_response_meta(
            spec_ref=spec_ref,
            decision_hash=decision_hash,
            spec_changed=spec_changed,
            decision_changed=decision_changed,
            trace_id=trace_id,
            signals=signals,
            evidence_pack=evidence_pack_ref,
        )

    def _detect_signals(
        self,
        spec_changed: bool,
        decision_changed: bool,
        prev_meta: Optional[ResponseMeta],
        curr_decision_hash: str,
    ) -> List[str]:
        """
        检测信号

        当前支持的信号：
        - POLICY_DECISION_DRIFT: spec 不变但 decision 变化
        """
        signals = []

        if not _is_drift_signal_enabled():
            return signals

        # POLICY_DECISION_DRIFT: spec_changed=False 但 decision_changed=True
        if not spec_changed and decision_changed:
            signals.append("POLICY_DECISION_DRIFT")

        return signals

    def build_empty(self, trace_id: str = "") -> ResponseMeta:
        """
        创建空的 ResponseMeta（用于开关关闭或错误情况）
        """
        return ResponseMeta.create_empty(trace_id=trace_id)

    @property
    def enabled(self) -> bool:
        """检查 meta 功能是否启用"""
        return self._enabled


def build_meta(
    spec_ref: SpecRef,
    decision_payload: Dict[str, Any],
    prev_meta: Optional[ResponseMeta] = None,
    evidence_pack_ref: Optional[str] = None,
    session_id: str = "",
    turn_id: str = "",
) -> ResponseMeta:
    """
    便捷函数：构建 ResponseMeta

    等同于 MetaBuilder().build(...)
    """
    builder = MetaBuilder()
    return builder.build(
        spec_ref=spec_ref,
        decision_payload=decision_payload,
        prev_meta=prev_meta,
        evidence_pack_ref=evidence_pack_ref,
        session_id=session_id,
        turn_id=turn_id,
    )


def build_meta_from_spec_and_turn(
    spec_id: str,
    spec_version: str,
    spec_hash: str,
    turn_data: Dict[str, Any],
    prev_meta: Optional[ResponseMeta] = None,
    evidence_pack_ref: Optional[str] = None,
    session_id: str = "",
    turn_id: str = "",
) -> ResponseMeta:
    """
    便捷函数：从原始参数构建 ResponseMeta

    用于没有现成 SpecRef 对象的场景
    """
    spec_ref = create_spec_ref(spec_id, spec_version, spec_hash)
    return build_meta(
        spec_ref=spec_ref,
        decision_payload=turn_data,
        prev_meta=prev_meta,
        evidence_pack_ref=evidence_pack_ref,
        session_id=session_id,
        turn_id=turn_id,
    )


# ==================== 测试辅助 ====================

def _test_meta_builder():
    """内置自测"""
    from src.shared.models.response_meta import create_spec_ref

    # 创建 spec_ref
    spec1 = create_spec_ref("spec-001", "v1.0", "hash-aaa")
    spec2 = create_spec_ref("spec-001", "v1.0", "hash-aaa")  # 相同
    spec3 = create_spec_ref("spec-001", "v1.1", "hash-bbb")  # 不同

    # 第一轮：无 prev_meta
    turn1 = {"options": [{"id": "fast", "cost": 100}]}
    meta1 = build_meta(spec_ref=spec1, decision_payload=turn1, session_id="s1", turn_id="t1")

    print(f"Turn 1 Meta: {meta1.to_dict()}")
    assert not meta1.spec_changed, "First turn should not have spec_changed"
    assert not meta1.decision_changed, "First turn should not have decision_changed"

    # 第二轮：相同 spec，相同 decision
    turn2 = {"options": [{"id": "fast", "cost": 100}]}
    meta2 = build_meta(spec_ref=spec2, decision_payload=turn2, prev_meta=meta1, session_id="s1", turn_id="t2")

    print(f"Turn 2 Meta: spec_changed={meta2.spec_changed}, decision_changed={meta2.decision_changed}")
    assert not meta2.spec_changed, "Same spec should not trigger spec_changed"
    assert not meta2.decision_changed, "Same decision should not trigger decision_changed"

    # 第三轮：相同 spec，不同 decision
    turn3 = {"options": [{"id": "fast", "cost": 200}]}  # cost 变了
    meta3 = build_meta(spec_ref=spec2, decision_payload=turn3, prev_meta=meta2, session_id="s1", turn_id="t3")

    print(f"Turn 3 Meta: spec_changed={meta3.spec_changed}, decision_changed={meta3.decision_changed}")
    assert not meta3.spec_changed, "Same spec should not trigger spec_changed"
    assert meta3.decision_changed, "Different decision should trigger decision_changed"

    # 第四轮：不同 spec
    turn4 = {"options": [{"id": "fast", "cost": 200}]}
    meta4 = build_meta(spec_ref=spec3, decision_payload=turn4, prev_meta=meta3, session_id="s1", turn_id="t4")

    print(f"Turn 4 Meta: spec_changed={meta4.spec_changed}, decision_changed={meta4.decision_changed}")
    assert meta4.spec_changed, "Different spec should trigger spec_changed"

    print("ALL TESTS PASSED")


if __name__ == "__main__":
    _test_meta_builder()
