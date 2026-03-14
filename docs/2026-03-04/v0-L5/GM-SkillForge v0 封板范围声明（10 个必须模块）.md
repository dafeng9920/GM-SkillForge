结论：
下面是你要的 **v0 封板范围声明**：只保留“必须实现的 10 个文件/模块”，其余一律视为 v1/L4（禁止做、禁止扩域）。这 10 个模块一旦落地，你就拥有：**NL（受限）→ Demand DSL → Contract → 8 Gate → Evidence → L3 AuditPack → Permit** 的最小闭环，并且三权分立可执行。

置信度：0.87

关键风险点：

1. 你/团队在实现时忍不住扩域（加更多模式/更多 IR）导致封板破坏
2. Permit/三哈希未强制进发布链（n8n/云端绕过）导致治理失效
3. EvidenceRef 产出不可信（hash/append-only没落地）导致“审计”形同虚设

---

# GM-SkillForge v0 封板范围声明（10 个必须模块）

## 冻结目标（v0 只做这一句）

> **受限 NL 输入 → 生成 Demand DSL（四件套）→ 编译 Constitution Contract → 8 Gate 裁决 → EvidenceRef 闭环 → L3 AuditPack → Permit 签发**
> **复现口径只认三哈希（demand/contract/decision）**，迭代必须 diff+rationale+tombstone。

---

## 10 个必须实现的文件/模块（缺一不封板）

### 1) `contracts/dsl/demand_dsl_v0.schema.yml`

**目的**：Demand DSL 的机器可读 schema（四件套：DemandSpec/AssetRefs/TestSpec/ControlSpec）。
**封板验收**：schema 校验通过；拒绝不符合字段/版本的输入。

---

### 2) `orchestration/hash_keysets.yml`

**目的**：机器可读声明：哪些字段进入 `demand_hash/contract_hash/decision_hash`，哪些字段必须剔除。
**封板验收**：validate 可从此文件生成包含/剔除逻辑；禁止口径漂移。

---

### 3) `tools/canonicalize.py`

**目的**：全项目唯一 canonical_json 实现（排序、数组稳定排序、剔除禁字段）。
**封板验收**：三哈希由此单点计算；禁止多处重复实现。

---

### 4) `tools/hash_calc.py`

**目的**：输入 Demand DSL + GateDecision，输出三哈希并写入 manifest/permit。
**封板验收**：同一输入对象重算一致；hash 写入路径固定。

---

### 5) `core/demand_parser_lite.py`

**目的**：受限 NL → Demand DSL（只支持 4 种 mode + blocking 澄清≤3）。
**执行边界**：不做 DDD 全量解构；不做自由规划。
**封板验收**：20 条样本 ≥80% 能落到某个 mode；缺槽位必须产澄清问题而不是瞎猜。

---

### 6) `core/dsl_validator.py`

**目的**：对 Demand DSL 做硬校验（ref 必须带 version、controls 必须明确、tests 原子化）。
**封板验收**：任何缺失/模糊 → FAIL（给 required_changes）。

---

### 7) `core/contract_compiler.py`

**目的**：将 Demand DSL 编译为 `Constitution Contract v0`（用于 Gate 裁决）。
**封板验收**：contract_hash 的 keyset 字段齐全且稳定；禁止把 blueprint_ir/plan_spec 混入。

---

### 8) `core/gate_engine.py`

**目的**：固定 8 Gate 顺序执行，产出 `GateDecision[]`（PASS/FAIL + issue_keys + evidence_refs + required_changes）。
**执行边界**：v0 不执行不受控代码；只允许静态+tests-only/dry-run。
**封板验收**：每 Gate 至少 1 条 EvidenceRef；FAIL 必须有 error_code + next_action。

---

### 9) `core/evidence_store.py`

**目的**：EvidenceRef 写入与不可变约束（hash + locator + tool_revision），append-only。
**封板验收**：EvidenceRef 可被独立复核（hash 对得上）；禁止执行层写“最终证据”。

---

### 10) `core/pack_and_permit.py`

**目的**：组装 L3 AuditPack（manifest/decisions/policy_matrix/checksums）+ Permit 签发（绑定三哈希 + audit_pack_hash + revision）。
**封板验收**：

* 交付完整性清单缺一 FAIL
* checksums 可重算一致
* Permit 未签发则禁止发布（至少在接口层返回 permit=null）

---

# v0 明确禁止（全部划到 v1/L4，不许做）

* Architecture Blueprint IR / PlanSpec 的自动生成与强制约束（可以留模板文件，但不进入门禁）
* 多 Agent 自治、动态规划、复杂状态机
* 真实外部系统执行（除 tests-only/dry-run）
* “无限生成”或无配额 API
* 任意绕过 Permit 的发布链路

---

# v0 最终封板验收（黑箱）

给定一条受限 NL 输入：

* 能落到 Demand DSL（或问≤3个澄清）
* 编译出 Contract
* 8 Gate 跑完
* evidence.jsonl 闭环
* 产 L3 AuditPack（checksums ok）
* 签发 Permit（绑定三哈希）

=> 即封板成功。

---

