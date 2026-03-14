
# v0-L5 规范索引（执行版）

> 当前状态（2026-03-04）：`V0_SEAL=GRANTED`  
> 封板决议：`docs/2026-03-04/verification/V0_SEAL_BOARD_2026-03-04.md`  
> 机器决议：`docs/2026-03-04/verification/V0_SEAL_DECISION_2026-03-04.json`

## 目的

统一 `v0-L5` 目录的使用口径，避免“战略文档直接驱动编码”导致目标错位。  
本索引用于 `PR2/PR3` 分发与验收映射。

---

## A. 可直接用于落地（Normative Sources）

以下 4 份是**执行规范源**，可以直接映射到代码任务：

1. [“三哈希口径”落成validate.py 的硬校验（v0）.md](d:/GM-SkillForge/docs/2026-03-04/v0-L5/“三哈希口径”落成validate.py%20的硬校验（v0）.md)  
用途：`validate` 硬校验规则、FAIL 条件、Permit 前置门禁。

2. [Manifest Schema v0（YAML 规范模板）.md](d:/GM-SkillForge/docs/2026-03-04/v0-L5/Manifest%20Schema%20v0（YAML%20规范模板）.md)  
用途：Skill manifest 字段、能力边界、静态探测规则映射。

3. [GM-SkillForge v0 封板范围声明（10 个必须模块）.md](d:/GM-SkillForge/docs/2026-03-04/v0-L5/GM-SkillForge%20v0%20封板范围声明（10%20个必须模块）.md)  
用途：v0 范围控制、模块封板清单、缺失项识别。

4. [Gap Analysis v0 模板（可喂给 AI 修复 & 可被审计复核）.md](d:/GM-SkillForge/docs/2026-03-04/v0-L5/Gap%20Analysis%20v0%20模板（可喂给%20AI%20修复%20&%20可被审计复核）.md)  
用途：迭代修复输入结构、审计复核结构（diff/rationale/tombstone）。

---

## B. 战略参考（Informative, 非直接编码源）

以下文档用于战略对齐与路线说明，**不得直接作为编码输入规范**：

1. [14天架构.md](d:/GM-SkillForge/docs/2026-03-04/v0-L5/14天架构.md)
2. [V0----LM.md](d:/GM-SkillForge/docs/2026-03-04/v0-L5/V0----LM.md)
3. [官网首页 3 个 Bullet（中英双语）.md](d:/GM-SkillForge/docs/2026-03-04/v0-L5/官网首页%203%20个%20Bullet（中英双语）.md)
4. [第一道红线.md](d:/GM-SkillForge/docs/2026-03-04/v0-L5/第一道红线.md)

---

## C. PR 任务映射

## PR2：Permit + 交付完整性 Gate

输入规范源：
- 三哈希硬校验文档
- Manifest Schema v0
- v0 封板范围声明

落地产物（建议）：
- `scripts/validate_*` 扩展：Permit 绑定三哈希校验
- `orchestration/` 增加 Delivery Completeness Gate 配置
- `docs/2026-03-04/verification/` 增加 PR2 三权记录

验收口径（必须）：
- 无 Permit 或 Permit 未绑定三哈希 -> `FAIL`
- 交付清单缺任一项（Blueprint/Skill/n8n/Evidence/AuditPack/Permit）-> `FAIL`

## PR3：Diff / Rationale / Tombstone

输入规范源：
- 三哈希硬校验文档
- Gap Analysis v0 模板
- v0 封板范围声明

落地产物（建议）：
- `audit/diffs/`
- `audit/rationale/`
- `audit/tombstones/`
- 相关校验脚本（缺任一即 FAIL）

验收口径（必须）：
- 三哈希变化但无 diff/rationale/tombstone -> `FAIL`
- 迭代裁决必须可回溯到 revision 与 evidence refs

---

## D. 分发规则（避免错位）

1. 任务书必须声明“规范来源文件路径”。  
2. 若任务引用 B 类战略文档，必须同时绑定 A 类规范文档。  
3. Final Gate 发现“战略文档直驱编码且无 A 类绑定”时，直接 `REQUIRES_CHANGES`。  

---

## E. 一句话执行口径

先锁规范源，再分发任务；先过三权记录，再给 Final Gate。  
