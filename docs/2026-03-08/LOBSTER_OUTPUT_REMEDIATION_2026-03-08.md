# Lobster Output Remediation

## 当前裁决

状态：`REQUIRES_CHANGES`

原因不是主线设计错误，而是 **执行回传与真实落盘不一致**。

当前必须修复的点只有 3 类：

1. 补回 `P1/P4` 核心四件套的真实路径或真实文件
2. 补回 `P2` 的文档接入证据
3. 重做 `P3`，让它真正符合 Wave 2 基线盘点要求

---

## 必修问题

### R1. 核心四件套缺失

应存在但当前未在 `docs/2026-03-08/` 找到：

- `execution_receipt.json`
- `completion_record.md`
- `resume_handoff.md`
- `checkpoint/state.yaml`

允许两种修复方式：

1. 这些文件其实已经存在于别处  
   - 列出真实路径
   - 不得继续伪装在 `docs/2026-03-08/`

2. 这些文件根本没落盘  
   - 明确承认未完成
   - 立即补写到正确位置

### R2. P2 缺少接入证据

必须补一份：

- `docs/2026-03-08/p2_doc_integration_report.md`

内容必须包括：

- 修改/确认的文档路径清单
- 每个文档对应的 skill 引用位置
- 说明没有新建重复 governor skill
- 说明 authoritative path 是：
  - `skills/lobster-cloud-execution-governor-skill/`

### R3. P3 交付不符合任务目标

当前 `p3_baseline_inventory.md` 只列了少量 mainline / promoted 项，不足以构成：

- 剩余 docs-backed non-F1 entries 基线盘点

必须重做为：

- `promote now`
- `keep docs-backed with reason`
- `defer`

三类分类清单

并且每项都要写：

- `intent / contract path`
- `current backing path`
- `disposition`
- `reason`

---

## 修复模式 A：交给小龙虾单兵修

直接发下面这段：

```text
你来修复昨晚执行包的真实性缺口，不新增任务，不扩 scope。

目标：
把当前状态从 REQUIRES_CHANGES 修到 READY FOR REVIEW。

必须修 3 件事：

1. 核心四件套
- 给出 execution_receipt.json / completion_record.md / resume_handoff.md / checkpoint/state.yaml 的真实路径
- 如果不存在，就补写到正确路径
- 不得继续引用不存在的 docs/2026-03-08 路径

2. P2 接入证据
- 新建 docs/2026-03-08/p2_doc_integration_report.md
- 写清楚哪些文档已接入 lobster-cloud-execution-governor-skill
- 写清 authoritative path 是 skills/lobster-cloud-execution-governor-skill/
- 明确没有继续使用 skills/governor-skill/ 作为正式入口

3. P3 重做
- 重写 docs/2026-03-08/p3_baseline_inventory.md
- 按以下三类输出：
  - promote now
  - keep docs-backed with reason
  - defer
- 每项必须有 disposition 和 reason
- 不得只写 hash

禁止：
- 不得新开 P5
- 不得改 review/compliance 结论
- 不得再宣称 FINAL PASS

完成后只回传：
- 修改文件列表
- 每个文件真实路径
- 核心四件套真实位置
- P2 文档接入清单
- P3 分类结果摘要
```

---

## 修复模式 B：AI 军团分片修

### B1. Execution shard

执行者：`小龙虾`

任务：

- 补/确认核心四件套真实路径
- 生成 `p2_doc_integration_report.md`
- 重做 `p3_baseline_inventory.md`

### B2. Review shard

审查者：`Kior-C`

只审 3 件事：

1. 四件套是否真实存在
2. `P2` 是否真的接到了现有 authoritative skill
3. `P3` 是否真正盘点了剩余 docs-backed non-F1 entries

输出：

- `ALLOW / REQUIRES_CHANGES / DENY`
- reasons
- evidence_refs

### B3. Compliance shard

合规官：`Antigravity-2`

只审 3 件事：

1. 是否仍有假落盘路径
2. 是否仍把重复 governor skill 当正式入口
3. 是否仍把“已 promoted / 已 mainline”误报成 Wave 2 待盘点项

输出：

- `PASS / FAIL`
- reasons
- evidence_refs

---

## 通过标准

只有同时满足以下条件，才算修完：

1. 核心四件套真实存在且路径一致
2. `p2_doc_integration_report.md` 存在且证据可核
3. `p3_baseline_inventory.md` 真正完成三类分类盘点
4. 不再出现“播报完成 > 仓库落盘”的情况

---

## 推荐路线

如果你想快：

- 先走 **模式 A**
- 小龙虾先把执行缺口补平
- 再由 `Kior-C + Antigravity-2` 做轻量复审

这样比重新开一整套大编排更快。
