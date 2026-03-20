# TERMINOLOGY_MAP_v1

## 1. 目的

本文件用于统一当前系统中的关键对象、状态、角色、模块、交付物术语。

统一原则：

1. 保留原语义
2. 不偷换角色边界
3. 能回溯到原文档
4. 不借统一命名暗改权责

---

## 2. 对象术语

| 原术语 | 统一术语 | 是否完全等价 | 说明 |
| --- | --- | --- | --- |
| `intent draft` | `IntentDraft` | 是 | 结构化意图草案 |
| `contract draft` / `contract bundle` | `ContractBundle` | 否 | `ContractDraft` 可作为草案状态；正式对象统一写 `ContractBundle` |
| `candidate skill` | `CandidateSkill` | 是 | 候选 skill 本体 |
| `verified candidate` | `Build-Verified Candidate` | 否 | 指 build validation 通过后的 candidate，不等价于 governance validated |
| `build validation report` | `BuildValidationReport` | 是 | 创建侧最小自检报告 |
| `delivery manifest` | `DeliveryManifest` | 是 | 交给打包层的标准输入物 |
| `skill package input` | `DeliveryManifest + package_input_root` | 否 | 包装输入，不是独立主对象 |
| `run record` | `RunRecord` | 是 | 一次运行记录 |
| `release record` | `ReleaseRecord` | 是 | 一次正式发布记录 |
| `audit pack` | `AuditPack` | 是 | 最小审计交付物 |
| `evidence ref` | `EvidenceRef` | 是 | 证据引用对象 |

---

## 3. 状态术语

| 原术语 | 统一术语 | 是否完全等价 | 说明 |
| --- | --- | --- | --- |
| `draft` | `draft` | 是 | 草案态 |
| `candidate` | `candidate` | 是 | 候选态 |
| `validated` | `validated` | 是 | 治理验证通过态 |
| `released` | `released` | 是 | 正式发布态 |
| `deprecated` | `deprecated` | 是 | 已弃用态 |
| `tombstoned` | `tombstoned` | 是 | 已下线保留追溯态 |
| `rejected` | `rejected` | 是 | 草案或候选失败态 |
| `validation_failed` | `validation_failed` | 是 | 治理验证失败态 |
| `build_failed` | `build_failed` | 否 | 创建侧失败态，不属于正式治理状态机 |
| `handed_to_governance` | `handed_to_governance` | 否 | 生产态 handoff 状态，不属于正式发布状态机 |

---

## 4. 角色与模块术语

| 原术语 | 统一术语 | 是否完全等价 | 说明 |
| --- | --- | --- | --- |
| `nl--skill` | `Intent Compiler` | 否 | 模块名保留 `nl--skill`，角色统一定义为 `Intent Compiler` |
| `contract-builder` | `Contract Builder` | 是 | 合同构造模块 |
| `skill-compiler` | `Skill Compiler` | 是 | 候选 skill 编译模块 |
| `validator` | `Validator` | 是 | 治理验证器 |
| `gate-engine` | `Gate Engine` | 是 | 门禁与准入检查器 |
| `release-manager` | `Release Manager` | 是 | 正式发布唯一中心 |
| `revision-manager` | `Revision Manager` | 是 | 修订/废弃/下线管理中心 |
| `orchestrator` | `Orchestration Layer` | 否 | 编排层角色名，模块名可保留 `orchestrator` |
| `n8n` | `n8n Runtime Adapter` | 否 | 编排适配器，不是裁决中心 |
| `skill-creator` | `Packaging / Delivery Layer` | 否 | 模块名保留 `skill-creator`，角色统一定义为后段封装/打包层 |
| `kernel` / `governor` / `deterministic kernel` | `Kernel / Governor` | 是 | 最终裁决中心，可双名并存 |

---

## 5. 权限与写口术语

| 写口 | 统一定义 | 授权写者 |
| --- | --- | --- |
| `released` | 正式发布状态 | `release-manager` / 特定场景下 `revision-manager` |
| `validated` | 治理验证通过状态 | `validator` |
| `gate_result` | 门禁裁决结果 | `gate-engine` |
| `run_state / business_state` | 运行态与业务态 | `state-manager` |
| `evidence_ref / audit_pack` | 证据对象与审计包 | `evidence-collector` |
| `manual_approval` | 人工留痕审批结果 | `admin-review-console` |

---

## 6. 交付术语

| 原术语 | 统一术语 | 是否完全等价 | 说明 |
| --- | --- | --- | --- |
| `Draft` | `Draft Delivery` | 否 | 用户快速可见草案，不是正式交付 |
| `Candidate` | `Candidate Delivery` | 否 | 可 review 的候选交付，不是正式发布 |
| `Released` | `Released Delivery` | 否 | 正式可商用交付 |
| `skill.zip` | `Standard Skill Package` | 否 | 打包产物，不等价于 release decision |

---

## 7. 明确禁止的偷换

- 不得把 `BuildValidationReport` 偷换成 `GovernanceValidation`
- 不得把 `DeliveryManifest` 偷换成 `ReleasePermit`
- 不得把 `skill-creator` 偷换成创建主引擎
- 不得把 `n8n` 偷换成治理中枢
- 不得把 `CandidateSkill` 偷换成正式 `Released Skill`
