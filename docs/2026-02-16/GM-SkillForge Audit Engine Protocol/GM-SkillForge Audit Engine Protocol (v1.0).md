# GM-SkillForge Audit Engine Protocol (v1.0)
**File:** `docs/AUDIT_ENGINE_PROTOCOL_v1.md`  
**Anchor Time:** 2026-02-16 11:00 (Asia/Singapore, UTC+8)

> 本协议定义 GM-SkillForge 的“可复核审计”技术栈、流程、边界与验收规则。  
> 目标是把“审计”从口号变成**可执行条款 + 可复现证据 + 可自动判定的 pass/fail**。  
> 本协议为 SkillForge **contracts-first** 体系服务，不依赖旧 GM OS 代码；未来 GM OS 仅作为可插拔 policy provider。

---

## 0. Scope & Non-Goals

### 0.1 Scope（本协议覆盖）
- 对 GitHub / ClawHub（OpenClaw Skills 市集）来源的 Skill/Tool 仓库进行：
  - **诊断（Diagnostic）**：静态扫描 + 合同/控制项 lint
  - **实测（Execution）**：可选的沙箱 smoke / 基准测试（按等级分层）
  - **取证（Evidence）**：生成审计包（Audit Pack）与证据链（Evidence Chain）
- 审计结论必须**可复核**（具备复现所需的输入、环境、证据、指标与版本信息）

### 0.2 Non-Goals（明确不做）
- 不承诺发现高级 0day / 漏洞挖掘（我们做“工程可复核审计”，非渗透测试）
- 不做全网爬虫式“无限自动化”导入（v1 仅支持明确来源与可复现快照）
- 不以“SEO/GEO 文案”作为审计标准的一部分（GEO 价值是副产品，不进入验收）

---

## 1. Terms & Alignment (Single Vocabulary)

> 以下术语必须与 `orchestration/error_policy.yml`、`orchestration/quality_gate_levels.yml` 中一致。

- **Skill**：可被某 Agent 协议加载/调用的能力包（含 schema/policies/examples/tests/可选代码）
- **Upstream**：审计对象来源（`github|clawhub|local`），必须可定位到具体版本
- **Revision**：同一 `skill_id` 的一次可复现快照（带 `effective_at`）
- **Gate**：门禁节点（pass/fail + error_code + next_action）
- **Quality Level**：质量等级（L1-L5，阈值与 required_changes 由 `quality_gate_levels.yml` 定义）
- **Issue Key**：标准化问题枚举（来自 `orchestration/issue_catalog.yml`）
- **Evidence Ref**：证据引用指针（每个 finding 必须可追溯到 evidence 容器）
- **Audit Pack**：审计输出包（L3/L4/L5 的必备文件集合）
- **Tombstone**：逻辑删除记录（保留审计链但在“当前面”与检索中不再呈现）

---

## 2. Operating Model: Contracts-First Orchestrator

### 2.1 Audit Kernel（审计内核）
- 审计内核为：**SkillForge Orchestrator（nodes + gates + policy runners）**
- 不依赖旧 GM OS 实现代码；仅允许引用“理念/口径”
- Policy 以版本化规则集存在（例如 `policies/` 或 `orchestration/*policy*.yml`），并产出 `policy_matrix.json`

✅ **PASS 条件**
- 审计执行与结论能在没有旧 GM OS 代码的情况下复现
- 所有门禁结果使用统一的 `error_code` 与 `next_action`

❌ **FAIL 条件**
- 任何关键判断依赖“外部不可控黑箱”（未记录版本/输入/证据）
- 输出不符合 error_policy 的统一格式

---

## 3. Pipeline: Diagnostic → Execution → Evidence

### 3.1 Stage D: Diagnostic（诊断阶段）
**目标：** 在不执行任意不可信代码的前提下，识别合同缺失、控制边界问题、静态风险。

**输入：**
- `upstream_ref`（source/id/version/fetched_at/license_hint）
- 可复现仓库快照（repo snapshot）

**动作：**
- D1. Repo Intake（拉取快照 + provenance 记录）
- D2. Repo Scan & Fit Score（识别是否为“可审计 skill”）
- D3. Contract Lint（schemas/examples/policies/tests 的一致性）
- D4. Static Scan（semgrep + rulepack，输出原始日志）

**输出：**
- `static_analysis.log(.gz)`（原始扫描日志）
- `policy_matrix.json`（规则判定矩阵，含 findings 与 required_changes）
- `manifest.json`（本次审计产物与关键文件指纹清单的一部分；或后置到 Audit Pack）

✅ **PASS 条件（最小）**
- 能生成 `policy_matrix.json` + `static_analysis.log`，且 findings 全部绑定 `issue_key` 与 `evidence_ref`
- Contract Lint 无结构性错误（L1 级要求）

❌ **FAIL 条件**
- 无法定位 upstream 版本（缺 commit/tag）
- issue_key 不在 issue_catalog 中
- evidence_ref 指向不存在的证据

---

### 3.2 Stage E: Execution（实测阶段，按等级分层）
**原则：** v1 绝不把 L5 的重压测写成通用必做；按 L3/L4/L5 分层。

#### L3 Execution（SHOULD）
- 可选：smoke test（短时、低成本）
- 目标：验证“可运行基本路径”与“错误处理边界”
- 默认策略：**不强制执行不可信代码**；仅对符合 Fit Score 的对象启用

✅ PASS（L3 实测）
- smoke 运行成功或可解释失败（失败必须给出 error_code + next_action）
- 生成最小运行记录（run_trace 摘要）

#### L4 Execution（SHOULD for L4）
- 基准：20~100 次测试向量（可复跑）
- 工具：pytest-benchmark（或等价工具）
- 输出：`harness_benchmark.json`

✅ PASS（L4 实测）
- P95/成功率/错误分布可被复跑验证（基于固定向量/seed）

#### L5 Execution（MUST for L5）
- 大样本（1000+）+ 长时（例如 1~4h）仅对“精品/重点对象”启用
- 必须输出：benchmark + vectors_meta + 可复跑命令

✅ PASS（L5 实测）
- success_rate、p95_latency、resource_peaks 满足 `quality_gate_levels.yml` 的阈值
- 允许标注“本机基准，不外推云端”，但必须可复跑

---

### 3.3 Stage X: Evidence（取证阶段）
**目标：** 生成可复核审计包（Audit Pack），建立证据链闭环。

**Evidence 容器（MUST, L3+）**
- `evidence.jsonl` 或 `evidence/` 目录（推荐 JSONL）
- 每条 evidence 记录必须包含：
  - `evidence_ref`（唯一）
  - `type`（scan_log|code_span|runtime_event|http_sample|...）
  - `sha256`
  - `source`（file/path/line range 或 run_trace pointer）
  - `created_at`
  - `payload` 或 `payload_hash`（可脱敏）

✅ PASS
- `policy_matrix.json` 中每个 finding 的 evidence_ref 都能在 evidence 容器中找到

---

## 4. Boundaries & Safety Defaults (Hard Limits)

> 所有边界必须以“可测上限 + 默认保守值”表达，不写死硬件猜测。

### 4.1 Compute Limits（默认保守值）
- 默认并发：`max_concurrency_default = 4`
- 默认单次 smoke 超时：`timeout_s = 120`
- 默认单次 L4 基准测试：`max_runs = 100`
- L5 长时测试：**仅在明确启用 L5 时**允许（并记录耗时与资源）

✅ PASS：每次审计必须输出 `repro_env.yml` 或 `Dockerfile` 记录限制值  
❌ FAIL：未设置限制，导致不可控资源消耗

### 4.2 Isolation（隔离边界，MUST for any execution）
- Docker / 容器隔离优先
- 源码卷只读挂载
- 默认网络策略：deny by default（除非 allowlist）

✅ PASS：执行阶段输出含隔离参数的环境快照  
❌ FAIL：执行阶段能访问局域网/本机敏感路径（未声明/未阻断）

### 4.3 Data Boundary（证据精度与脱敏）
- 默认不打包真实敏感数据
- 若包含真实 URL/响应片段，必须脱敏或 hash，并在 vectors_meta 标注 dataset_type

---

## 5. Upstream Intake & Provenance (Reproducibility Core)

### 5.1 Upstream Ref（MUST）
- `source`: github|clawhub|local
- `id`: repo url / clawhub slug
- `version`: commit sha / tag（强烈建议 commit）
- `fetched_at`
- `license_hint`（可选）
- `snapshot_hash`（快照指纹）

✅ PASS：`original_repo_snapshot.json` 必须包含上述字段  
❌ FAIL：仅记录 URL，不记录版本或快照 hash

### 5.2 Revision Model（MUST）
- 每次审计生成一个 revision（event-sourcing，不覆盖历史）
- 支持 tombstone（逻辑删除）与 at-time 复现
- 必须支持：`snapshot(at_time)` 与 `index(at_time)`

---

## 6. Audit Pack Spec (L3 as Commercial Baseline)

> v1 的“可商用起点”默认以 **L3 Audit Pack** 为基线。  
> L4/L5 在质量门禁允许时扩展。

### 6.1 L3 Audit Pack（MUST）
- `manifest.json`
- `policy_matrix.json`
- `static_analysis.log(.gz)`
- `original_repo_snapshot.json`
- `source_lineage.diff`（若有加固/适配；否则允许为空并说明）
- `repro_env.yml` 或 `Dockerfile`
- `evidence.jsonl`（或 evidence/）

✅ PASS：以上文件齐全，且 hash 可校验  
❌ FAIL：缺任一 MUST 文件

### 6.2 L4/L5 Additional（按 quality_gate_levels.yml）
- L4：`harness_benchmark.json`
- L5：`stress_test_vectors.csv` + `vectors_meta.json` + 长时基准/资源曲线（可选图表，但 JSON 必须）

---

## 7. Pass/Fail Decision & Error Policy Binding

### 7.1 Decision Source of Truth
- Quality Level 的最终裁决只来自：
  - `quality_gate_levels.yml`（阈值/必需项）
  - `error_policy.yml`（失败原因 + 解锁路径 next_action）
  - `issue_catalog.yml`（问题枚举）

### 7.2 Failure Output（MUST）
任何 Gate FAIL 必须输出：
- `error_code`（来自 error_codes.yml）
- `title`（短）
- `reason`（可读）
- `next_action`（可执行步骤）
- `suggested_fixes[]`（kind 枚举，便于 UI 一致与国际化）
- `required_changes`（模板化，能直接转为 PR checklist）

---

## 8. Minimal MVP Targets (v1 Deliverable)

### v1 必达（MUST）
- 支持 Upstream：`github`（必做）+ `clawhub`（可选 adapter）
- 支持 Quality：L1-L3 全链路跑通（contracts + static + evidence + L3 pack）
- 支持 Revision：add-revision / snapshot(at_time) / index(at_time) / tombstone

### v1 可选（SHOULD）
- L4：benchmark + 20~100 向量
- 生成 HTML 报告页（展示层，不参与门禁）

---

## 9. Acceptance Checklist (Protocol Compliance)

以下条目任何一条不满足，即判定协议未落地：

1. ✅ Upstream 可复现：repo + commit/tag + fetched_at + snapshot_hash
2. ✅ evidence 闭环：policy findings 的 evidence_ref 可查
3. ✅ contracts-first：schemas/examples/tests/policies 一致性可自动校验
4. ✅ error_policy 对齐：fail 必含 error_code + next_action + suggested_fixes.kind
5. ✅ revision/timepoint：snapshot --include-deprecated 可用；index --at-time 可用
6. ✅ tombstone 生效：tombstone 后“当前面”与检索面不再呈现（但历史仍可复现）
7. ✅ L3 Audit Pack：MUST 文件齐全且 hash 可校验

---

## 10. Notes (Implementation Guidance)

- Prometheus/全链路 telemetry：后置到 v2（避免拖慢 v1）
- Playwright：仅在“browser/control 类 skill”进入 L4/L5 时启用
- L5 长时压测：默认关闭；只有明确标记“精品对象”才开启

---
**End of Protocol v1.0**
