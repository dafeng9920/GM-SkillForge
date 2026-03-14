# Repo Triage

## 当前判断

当前仓库不是“小范围未提交”，而是 **主线资产 + 新增子系统 + 历史快照 + 临时产物** 混在同一工作树里。

这会直接带来 4 个风险：

1. 关键脚本和关键报告容易在 merge/reorg 时漂移或短暂消失
2. 主仓 authoritative path 容易和运行时 / workspace path 混淆
3. 重复 skill / 重复 docs 会制造错误入口
4. 后续任何清理动作都可能误伤正在使用的主线

## 当前最需要保护的主线

以下内容应视为 **一级保留**，近期整理时不得误删：

- `scripts/`
- `skills/`
- `docs/compliance_reviews/`
- `docs/2026-03-07/`
- `docs/2026-03-08/`
- `skillforge/src/` 中当前实际使用的主线代码
- `.tmp/openclaw-dispatch/` 中正在跑的任务上下文

## 已跟踪修改

当前已跟踪且有变动的文件只有这几类：

- `docs/2026-03-07/L4_MINI_云端小龙虾执行臂定义.md`
- `docs/compliance_reviews/review_latest.md`
- `docs/compliance_reviews/review_latest.json`
- `docs/compliance_reviews/runs/latest/review.md`
- `docs/compliance_reviews/runs/latest/review.json`

这说明：

- 主线已跟踪修改并不多
- 真正“脏”的主要来源是 **大量未跟踪新增**

## 未跟踪内容分类

### A. 主线候选（应保留并后续纳入）

这些明显是当前系统继续演进所需的资产：

- `contracts/`
- `orchestration/`
- `permits/`
- `core/`
- `db/`
- `skillforge/src/api/`
- `skillforge/src/skills/`
- `skillforge/src/tests/`
- `scripts/run_3day_compliance_review.py`
- `scripts/run_skill_5layer_audit.py`
- `scripts/run_l3_gap_closure.py`
- `skills/lobster-cloud-execution-governor-skill/`
- `skills/cloud-lobster-closed-loop-skill/`
- `skills/budget-guard-skill/`
- `skills/openclaw-*` 系列
- `docs/2026-03-07/`
- `docs/2026-03-08/`

### B. 领域子系统候选（先逻辑剥离，不急于全量纳入）

这些更像独立垂直域：

- `adapters/quant/`
- `export-seo/`
- `pseo/`
- `quant-system/`
- `ui/app/src/pages/strategy/`
- `ui/app/src/components/FiveStageTracer.tsx`
- `ui/app/src/components/ThreeCardSummary.tsx`
- `ui/app/src/components/MissionCommandCenter.tsx`

当前建议：

- 先保留
- 但不要和主线治理/云端执行混着一起推进
- 后续单独做“逻辑剥离”或“子系统归档”

### C. 历史快照 / 归档候选

这些明显更像历史材料、阶段验证或快照：

- `docs/2026-02-22/`
- `docs/2026-02-25/verification/`
- `docs/2026-02-26/l4-n8n-execution/evidence_pass_snapshot/`
- `docs/2026-02-26/l4-n8n-execution/verification/`
- `reports/l3_gap_closure/`
- `reports/l5-*`
- `skillforge-spec-pack/reports/`
- `evidence_pass_snapshot.zip`
- 各类旧 gate / execution / compliance 快照

当前建议：

- 归档保留
- 不要参与当前主线整理
- 后续统一做 archive policy

### D. 噪音 / 临时产物候选

这些当前不像主线核心资产，应重点警惕：

- `Audit_Report_Final.html`
- `Audit_Report_genesismind_ai.html`
- `Audit_Report_indiajobsdekho.json`
- `lobster-p2a.tar.gz`
- `skillforge_src.tar.gz`
- 根目录零散 `patch_*`, `test_regex*`, `bulk_patch_imports.py` 等临时脚本

这些不一定立即删除，但不能再让它们和主线入口混在一起。

## 已发现的重复 / 冲突风险

### 1. governor skill 重复风险

当前已有 authoritative skill：

- `skills/lobster-cloud-execution-governor-skill/`

但还出现了重复目录：

- `skills/governor-skill/`

这会制造两个问题：

- 文档引用容易指错
- 执行者容易误以为要新建第二个 governor skill

当前建议：

- `lobster-cloud-execution-governor-skill` 作为 authoritative
- `skills/governor-skill/` 标记为 **重复候选，待人工审查**
- 已执行的安全整理动作：
  - 将 `skills/governor-skill/SKILL.md` 改为 `DEPRECATED / DO NOT USE` 占位入口
  - 明确重定向到 `skills/lobster-cloud-execution-governor-skill/`

### 2. 巡检探针曾经漂移

已确认：

- `scripts/run_3day_compliance_review.py` 目前又回来了
- `docs/compliance_reviews/review_latest.*` 也恢复了

这说明：

- probe 链已恢复
- 但此前确实发生过漂移

因此 probe 链应视为一级基础设施，后续需要单独保护。

## 今日建议动作

今天不要做“大清仓”，只做最小收敛：

1. **冻结一级主线**
- `scripts/`
- `skills/`
- `docs/compliance_reviews/`
- `docs/2026-03-07/`
- `docs/2026-03-08/`

2. **标记重复项**
- `skills/governor-skill/` 进入待审列表

3. **不清理历史快照**
- 所有 `docs/2026-02-*`、`reports/*` 先不动

4. **不删除噪音，只记录**
- 先盘点，不做 destructive 清理

## 明日建议动作

明天按以下顺序推进：

1. 审核小龙虾夜间产物并冻结封口
2. 确认 `skills/governor-skill/` 是否废弃
3. 为关键治理脚本和报告建立“一级基础设施”清单
4. 再进入 `GM 多Agent编排层最小设计草案`

## 结论

当前仓库确实很脏，但不是“坏掉”，而是：

**还没有完成主线、归档、实验、临时产物的边界分层。**

当前最优策略不是大清洗，而是：

**先分诊、先冻结主线、先避免误删，再回到主线开发。**
