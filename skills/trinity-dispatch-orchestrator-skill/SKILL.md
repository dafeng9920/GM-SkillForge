# trinity-dispatch-orchestrator-skill

> 版本: v1.0.0  
> 适用阶段: 三权分立任务编排、重跑、审计固化

---

## 触发词

- `TRINITY_DISPATCH_ORCHESTRATOR`
- `三权分立调度`
- `task_dispatch 编排`
- `可转发提示词`
- `任务追责映射`

---

## 输入

```yaml
input:
  date: string                   # YYYY-MM-DD
  job_id: string                 # 唯一任务批次 ID
  title: string                  # 调度标题
  dispatch_path: string          # docs/{date}/task_dispatch_*.md
  prompts_path: string           # docs/{date}/tasks/*_PROMPTS.md
  verification_dir: string       # docs/{date}/verification
  task_ids: array                # [T90, T91, ...]
  owners:
    execution: map               # task -> executor_name
    review: map                  # task -> reviewer_name
    compliance: map              # task -> compliance_name
```

---

## 核心产物

1. 调度单：`task_dispatch_*.md`（每个 `Txx` 绑定实名）
2. 可转发提示词：`*_PROMPTS.md`（按角色分发）
3. 验证目录约束：`verification/Txx_*.{yaml,json}`

---

## 落盘路径约定

先读：`references/path_conventions.md`

- 调度单固定放：`docs/{date}/task_dispatch_*.md`
- 提示词固定放：`docs/{date}/tasks/*_PROMPTS.md`
- 验证产物固定放：`docs/{date}/verification/`

命名口径：

- `Txx_execution_report.yaml`
- `Txx_gate_decision.json`
- `Txx_compliance_attestation.json`
- `*_final_gate_decision.json`

---

## 执行流程

1. 用模板生成骨架：
   - `python skills/trinity-dispatch-orchestrator-skill/scripts/create_dispatch_pack.py ...`
2. 填充任务实名映射与依赖关系。
3. 运行结构校验：
   - `python skills/trinity-dispatch-orchestrator-skill/scripts/validate_dispatch_pack.py ...`
4. 校验通过后，再向执行军团分发提示词。

---

## DoD

- 每个 `Txx` 都有实名 `Execution/Review/Compliance` 绑定。
- 调度单、提示词、验证目录三者路径一致。
- 任务编号、依赖、输出文件命名无冲突。
- 存在 Final Gate 产物路径定义。

---

## 快速命令

```bash
python skills/trinity-dispatch-orchestrator-skill/scripts/create_dispatch_pack.py \
  --date 2026-02-22 \
  --job-id L4P5-UPGRADE-20260222-001 \
  --title "L4 -> L4.5 升级清单" \
  --dispatch-path docs/2026-02-22/task_dispatch_l4_5_upgrade.md \
  --prompts-path docs/2026-02-22/tasks/L4P5_UPGRADE_PROMPTS.md

python skills/trinity-dispatch-orchestrator-skill/scripts/validate_dispatch_pack.py \
  --date 2026-02-22 \
  --dispatch docs/2026-02-22/task_dispatch_l4_5_upgrade.md \
  --prompts docs/2026-02-22/tasks/L4P5_UPGRADE_PROMPTS.md
```

