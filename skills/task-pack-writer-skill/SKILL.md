# task-pack-writer-skill

> 版本: v0.1.0  
> 适用阶段: 并行任务批次编排（Txx 批量下发）

---

## 触发词

- `生成任务包`
- `task_dispatch`
- `Txx 任务书`
- `并行任务下发`
- `汇总模板`

---

## 输入

```yaml
input:
  batch_id: string                # 例如 T28-T34
  dispatch_file: string           # task_dispatch_*.md
  task_range: array               # [T28, T29, ...]
  owners: map                     # task -> owner
  objective: string               # 本批次目标
  summary_file: string            # 各小队任务完成汇总_*.md
  output_dir: string              # docs/YYYY-MM-DD/tasks/
```

---

## 步骤

1. 生成 `task_dispatch_*.md`：目标、并行关系、依赖、验收口径。  
2. 为每个任务生成 `Txx_*.md`：背景、范围、交付物、DoD、验证命令。  
3. 在 dispatch 中固定引用 `docs/templates/dispatch_skill_catalog.md`。  
4. 生成或更新批次汇总文档：看板、证据路径、最终判定模板。  
5. 校验命名与路径一致性，确保任务编号连续。  
6. 输出 AI 军团可直接执行的“写回规范”。  

---

## DoD

- 三类文档齐全：dispatch + 全部 Txx + summary。  
- dispatch 已引用 `docs/templates/dispatch_skill_catalog.md`，且保留批次特有映射位。  
- 每个任务含可执行验证命令与明确完成判定。  
- 汇总模板含 `Gate Decision`、`READY_FOR_NEXT_BATCH` 字段。  
- 文档路径与任务编号无冲突。  

---

## 失败处理

| 场景 | 处理 |
|---|---|
| 任务编号重复/断号 | 阻断生成并返回冲突点 |
| owner 缺失 | 用 `UNASSIGNED` 标记并阻断下发 |
| 验收口径不一致 | 统一为单一统计口径后再生成 |
| 汇总文件已存在且结构冲突 | 备份旧版本并生成合并草案 |
