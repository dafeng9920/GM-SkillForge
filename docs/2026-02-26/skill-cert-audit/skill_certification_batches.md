# Skill 认证审计分批清单（2026-02-26）

目标：在不阻塞主线的前提下，先做“最小可用认证审计”，再扩到全量 41 个 Skill。

## P0（立即审计，封板相关）

范围：
1. `wave-gate-orchestrator-skill`
2. `triple-record-validator-skill`
3. `decision-schema-normalizer-skill`
4. `wave-recheck-generator-skill`
5. `dispatch-broadcast-builder-skill`
6. `p0-final-adjudicator-skill`
7. `evidence-freeze-board-skill`
8. `protocol-gate-ci-checker-skill`

目标：
- 快速确认新沉淀 8 个资产具备最小结构与可调用元数据。

通过判据：
- `SKILL.md` 存在
- `agents/openai.yaml` 存在
- 产出机读审计报告（PASS/REQUIRES_CHANGES/DENY）

## P1（本周内）

范围：已有治理主线 Skill（门禁、发布、回滚、CI 验证等）

建议目标：
- 验证字段一致性（name/description/version/frozen_at/default_prompt/tags/owner）
- 校验契约标记和错误语义一致性

## P2（全量补齐）

范围：`skills/` 全部 + `.agents/skills/` 全部

建议目标：
- 全量统一标准化
- 补齐缺失 `openai.yaml`
- 形成年度审计基线报告

## 一键审计命令

```powershell
# 先跑 P0（推荐）
powershell -ExecutionPolicy Bypass -File scripts/run_skill_cert_audit.ps1 -Batch P0

# 需要时再跑 P1/P2/ALL
powershell -ExecutionPolicy Bypass -File scripts/run_skill_cert_audit.ps1 -Batch P1
powershell -ExecutionPolicy Bypass -File scripts/run_skill_cert_audit.ps1 -Batch P2
powershell -ExecutionPolicy Bypass -File scripts/run_skill_cert_audit.ps1 -Batch ALL
```

