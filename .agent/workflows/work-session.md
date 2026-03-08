---
description: SkillForge 开发流程纪律 — Superpowers 过程管控 + SkillForge 合同真相
---

# Work Session Workflow

> Superpowers 管过程纪律，SkillForge contracts 管产物真相，一刀切开。

## Canon of Truth

产品行为的唯一真相来源是本仓库的合同与门禁：
- `schemas/**` — JSON Schema 定义
- `orchestration/**` — issue_catalog.yml、controls catalogs、profiles、policies
- `skillforge/specs/**` — Skill Spec YAML（先 Skill 后代码）
- `contract_tests/**` — 合同测试
- `tools/validate.py --all` — 统一验证入口

任何外部工具（Superpowers、Claude 4.6 等）仅是**开发辅助**，不能重新定义 schema、issue_key 分类、error_code 语义、目录布局或命名约定。

## Non-Negotiable Rules

1. **先验后改**：开始实现或重构前，先跑一遍确认基线：
   ```bash
   python tools/validate.py --all && pytest -q
   ```

2. **变更必须带合同**：任何新功能/变更必须包含：
   - Skill Spec 更新（如需要）
   - Schema / catalog / policy 更新（如需要）
   - 至少 1 个 example JSON 更新或新增
   - contract test 更新（如需要）
   - `validate.py --all` 保持绿色

3. **先 Skill Spec 后代码**：
   - 新模块必须先写 `.skill.yml`，定义 input/output/capabilities/risk_tier
   - 代码实现必须对着 Spec 写
   - 代码产出后，Spec 必须同步更新

4. **不擅自引入新体系**：不引入新框架、不重组目录结构，除非用户明确要求。

5. **薄切片提交**：保持工作小而可验证。

## Workflow Discipline (A → E)

### A) Brainstorm
- 用 ≤5 条要点重述目标和约束
- 识别所需的最小合同变更

### B) Plan
- 写出任务计划，每步都有验收检查
- 明确：哪些是 Skill Spec 变更，哪些是代码变更

### C) Execute
- 实现能让一个验收检查通过的最小变更
- 主控官出任务书，执行者写代码，不越界

### D) Verify
// turbo
```bash
python tools/validate.py --all && pytest -q
```
- 如果失败：修复 → 重跑，不能含糊过去

### E) Report
输出格式：
```
- What I changed:
  - [file list]
- Commands I ran:
  - [exact commands + results]
- What is now passing:
  - [validations/tests]
- Next small step:
  - [one step only]
```

## Role Boundaries

| 角色 | 职责 | 不能做 |
|------|------|--------|
| 主控官 | 出 Mega Prompt、任务书、验收标准 | 不替执行者写实现代码 |
| Claude 4.6 | 产出骨架代码 + Skill Spec | 不能重定义合同体系 |
| 执行军团 | 落盘代码、填充实现、跑测试 | 不能跳过 Spec 直接写代码 |
| 验收者 | 跑 validate + pytest + Spec 一致性检查 | 不能替换执行者角色 |
