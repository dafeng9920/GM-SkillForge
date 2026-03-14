结论：
下面是把“三哈希口径”落成**validate.py 的硬校验（v0）**。跑过这些校验，才允许生成/发布 Permit；否则一律 FAIL（并给 required_changes）。

置信度：0.90

关键风险点：

1. canonicalize 规则实现不一致（不同模块各算各的）导致 hash 抖动
2. keyset 漏字段导致“实质变更不触发 hash”
3. diff/rationale/tombstone 约束不严导致“迭代不可审计”

---

# validate.py 硬校验（<=10 条，直接可实现）

## 1) HashSpec 版本与单一入口（必须）

* 必须存在 `specs/hash_spec_v0.md`（或等价配置 `orchestration/hash_spec.yml`），并声明 `hash_spec_version == v0`。
* `canonicalize()` 只能来自 **一个**模块（如 `tools/canonicalize.py`），禁止多处重复实现（避免分叉）。

**FAIL 条件**：缺失 / 版本不符 / 发现重复 canonicalize 实现（简单做法：grep 关键函数名）。

---

## 2) canonical_json 基础约束（必须）

对三哈希输入对象做 canonicalize 时强制：

* UTF-8
* 递归 `sort_keys=True`
* `separators=(",", ":")`
* 禁止 NaN/Infinity（浮点必须是有限数）
* 数值精度固定（例如阈值类 float 保留 2 位；或统一转 string）

**FAIL 条件**：发现 NaN/Infinity、未排序 key、浮点精度不一致。

---

## 3) “不得进入 keyset”的字段黑名单（必须）

建立黑名单（任一出现在 canonical 输入对象里就 FAIL）：

* `timestamp`, `created_at`, `updated_at`, `duration`, `latency`, `run_id`, `random`, `seed`（除非 seed 明确写入并固定）
* `summary`（DemandSpec）
* `clarifications_needed`
* `reason/next_action`（GateDecision 中的自然语言字段）
* `at_time`（contract keyset 内禁止；可作为输入引用但不得参与 contract_hash）

**FAIL 条件**：黑名单字段未被剔除却参与了 canonical_hash。

---

## 4) demand_hash keyset 完整性（必须）

对 DemandSpec：

* 必须包含：`mode/trigger/sources/transforms/destinations/constraints/acceptance.success_criteria`
* 必须不包含：`summary/clarifications_needed`
* `constraints.secrets` 只能是 “needs_user_key:*” 名称，不得出现疑似密钥内容（长度/格式启发式即可）

**FAIL 条件**：缺字段、含禁字段、疑似 secrets 泄露。

---

## 5) contract_hash keyset 完整性（必须）

对 Constitution Contract：

* 必须包含：`goals(primary, non_goals)/io/controls/quality/risk/gate_plan`
* `gate_plan` 必须是固定 8 Gate 且顺序一致（不可排序）
* `network_policy` 必须明确（deny_by_default 或 allowlist；v0 推荐 deny_by_default）

**FAIL 条件**：缺字段、gate_plan 非法、network_policy 模糊或缺失。

---

## 6) decision_hash 结构与稳定性（必须）

对 GateDecision[]：

* 必须覆盖 8 Gate 且顺序与 gate_plan 一致
* 每个 gate decision 必须含：`gate_name/status/level`；FAIL 时必须含 `error_code`
* `issue_keys/required_changes/evidence_refs` 必须排序后参与 hash
* `evidence_refs` 只允许使用 `evidence_ref_id` 或 `content_hash`，不得内联证据内容

**FAIL 条件**：gate 缺失/乱序、字段缺失、未排序、证据内容被纳入。

---

## 7) 三哈希写入与一致性校验（必须）

产物中必须落地：

* `demand_hash`
* `contract_hash`
* `decision_hash`
  并写入 `audit_pack/manifest.json`（关键字段区）。

同时校验：

* manifest 里的三哈希 == validate.py 现场重算三哈希

**FAIL 条件**：缺失 / 不一致（这类直接 BLOCKER）。

---

## 8) L3 复现判定（必须）

当用户声明 “reproduce/复现模式”（例如命令带 `--reproduce-from <revision>`）时：

* 读取旧 revision 的三哈希
* 现场重跑（或重算）后要求：三哈希完全一致
* 若不一致，必须 FAIL 并输出：差异归因（哪个 hash 变了）+ required_changes

**FAIL 条件**：任一 hash 不一致。

---

## 9) L3 迭代判定（必须）

当检测到三哈希与上一版不同（或显式 `--iterate-from <revision>`）：

* 必须存在：`audit/diffs/{revision_from}_to_{revision_to}/`

  * `demand_diff.json`
  * `contract_diff.json`
  * `decision_diff.json`
* 必须存在：`audit/rationale/{revision_to}.md|json`
* 若替代/撤销旧版：必须存在 `audit/tombstones/{revision_from}.json`

**FAIL 条件**：任一缺失 → 禁止签发 Permit。

---

## 10) Permit 签发前置条件（必须）

Permit 只能在以下都 PASS 后签发：

* L3 AuditPack 最小清单齐全 + checksums 校验通过
* 三哈希写入且可重算一致
* 若迭代：diff+rationale+tombstone 齐全

**FAIL 条件**：任一不满足 → Permit = null（或直接不生成），并返回 error_code（建议用 `SF_PACK_AUDIT_FAILED` / `SF_VALIDATION_ERROR`）。

---

如果你要更进一步“极致不扯皮”，我建议把 **keyset 的字段列表**直接写成机器可读的 `orchestration/hash_keysets.yml`，validate.py 从它生成剔除/包含逻辑，避免未来口径漂移。
