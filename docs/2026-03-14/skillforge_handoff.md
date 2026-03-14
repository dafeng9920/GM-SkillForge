# GM-SkillForge 项目交接文档（给新账号 / 新会话）

## 0. 这份文档是干什么的
这是一份给“新账号 / 新会话 / 新接手者”的项目交接文档。目标不是做宣传，而是把 GM-SkillForge 当前已经锁死的原则、已经形成的方案、后续落地路径、边界条件、风险点和路线图，尽可能完整地写清楚，让新的账号接手后能快速进入同一认知框架，不再回到 old `new-gm` 的旧路上。

**一句话定位：**
GM-SkillForge 不是去复刻 old GM OS，而是在一个全新仓库里，以 **contracts-first + Gates + EvidenceRef + AuditPack + Revision/at_time/Tombstone** 为骨架，做一个“**意图 → 生成可发布 Skill**”的智能框架与审计闭环。

**北极星：**
`intent + repo@commit + at_time -> EvidenceRef 闭环 -> L3 AuditPack`

---

## 1. 项目总定位

### 1.1 项目不是什么
- 不是拷贝 old `new-gm` / GM OS 的旧实现。
- 不是一个继续膨胀的大一统框架。
- 不是 0day 挖掘平台。
- 不是先做“万能执行引擎”，再补治理。

### 1.2 项目是什么
- 一个 **contracts-first** 的 Skill 审计 / 生成 / 发布治理骨架。
- 一个能把“意图”沉淀成合同、证据和可复核产物的系统。
- 一个把大部分实现层 Skill 化，但把裁决层和证据层内核化的系统。
- 一个未来可以与 **n8n** 闭环集成，由 n8n 负责现实世界编排，而 SkillForge 负责审核、裁决、证据链与放行令牌。

---

## 2. 已经锁定的既定事实（不要改口径）
以下内容在讨论中已经被视为既定事实：

| 模块 | 已完成 / 已定义内容 | 说明 |
|---|---|---|
| `docs/AUDIT_ENGINE_PROTOCOL_v1.md` | 已定义审计协议：`Diagnostic -> Execution -> Evidence`，并区分 `L3/L4/L5` | `L3` 为商业基线；要求 evidence 闭环、provenance、AuditPack 最小文件集合 |
| `orchestration/quality_gate_levels.yml` | 已定义 `L1-L5` 的 MUST/SHOULD/thresholds/required_changes_templates | `L3` 是商业起点 |
| `orchestration/error_policy.yml` | 已定义 8 个固定 Gate 节点及 fail 结构 | fail 结构包含 `error_code/title/reason/next_action/suggested_fixes/required_changes` |
| `orchestration/error_codes.yml` | 已补齐最小错误码注册表方案 | 支持 `category / severity / i18n / UI / validate.py` |
| `tools/rag_index.py` | 已有 `revision / timepoint / tombstone` 思路 | 目标支持 `snapshot(at_time, include_deprecated)` 与 `index(at_time)` 的严格复现 |

### 2.1 固定 8 Gate
1. `intake_repo`
2. `license_gate`
3. `repo_scan_fit_score`
4. `draft_skill_spec`
5. `constitution_risk_gate`
6. `scaffold_skill_impl`
7. `sandbox_test_and_trace`
8. `pack_audit_and_publish`

### 2.2 错误码体系（最小闭环）
最小错误码集已围绕 8 Gate 形成，包含：
- `SF_INTAKE_REPO_FAILED`
- `SF_LICENSE_DENIED`
- `SF_SCAN_FIT_SCORE_LOW`
- `SF_CONTRACT_DRAFT_INVALID`
- `SF_RISK_CONSTITUTION_BLOCKED`
- `SF_SCAFFOLD_GENERATION_FAILED`
- `SF_SANDBOX_TEST_FAILED`
- `SF_PACK_AUDIT_FAILED`
- 通用补充：`SF_VALIDATION_ERROR` / `SF_INTERNAL_ERROR`

### 2.3 validate.py 最小校验逻辑（已明确口径）
- `error_policy.yml` 中所有 `error_code` 都必须存在于 `error_codes.yml`
- `error_codes.yml` 不允许出现未被 policy 引用的特定码（`generic: true` 除外）
- `suggested_fixes.kind` 必须属于稳定枚举
- Gate 节点只能是 8 个固定节点之一
- `code` 字段必须与 key 一致
- `category / severity / http_status` 必须合法

---

## 3. 现阶段代码状态的锚定结论（基于讨论中给出的代码快照）
> 这部分来自讨论中提供的代码现状说明，是用于决策的锚点；本次文档没有重新独立核验仓库文件。

### 3.1 已经足够支撑的能力
- 已有可落地的审计对象模型：`skill_id / revision / artifact / timepoint`
- 已有可执行门禁：`validate.py --all`、`pytest -q`、CI
- 已有可复核证据链框架：`manifest / policy_matrix / provenance / diff / repro_env`
- 已有可持续演进模式：上游 SHA + diff + 重审 + 再发布

### 3.2 当前代码快照对 v0 的真实指向
| 锚点 | 讨论中给出的代码现实 | v0 决策 |
|---|---|---|
| 审计范围 | `gate_engine.py` 主要做合同校验；`sandbox_test.py` 有骨架但实际仍是 mock | v0 只审合同 + 静态，不做真实执行；执行/压力测试后置到 `L4/L5` |
| 首发协议 | `adapters/` 有 `github_fetch / sandbox_runner / registry_client`，没有 MCP/OpenClaw/Dify 适配 | v0 = `GitHub + CLI`；MCP adapter 到 v1 |
| 首发语言 | `repro_env.yml` 固定 `python_version: 3.11`；`scaffold_impl.py` 只生成 Python 模板 | v0 = Python only |
| 最低交付物 | Protocol v1 的必达是 `L1-L3`；`pack_publish.py` 当前生成 `L3 pack` | `L3` = 商用起点 |
| 证据采集 | `evidence.jsonl` 仍偏 mock 元数据；没有真实网页抓取 | v0 不纳入真实抓取；证据以静态分析输出 + provenance 为主 |
| GitHub 输入 | `intake_repo.py` 接受 `repo_url + branch`，没有强制 `commit_sha` | v0 强制 `repo_url + commit_sha` |
| 合法性边界 | 当前没有 `robots.txt` / 登录态限制 | v0 明确：respect robots.txt；禁止登录态/受限内容 |

### 3.3 v0 Scope Lock（已经建议锁死）
- **审计范围：** 合同 + 静态分析 ONLY（不执行）
- **首发协议：** GitHub + CLI（MCP -> v1）
- **首发语言：** Python only
- **最低交付物：** `L3` = 商用起点（`L4/L5` 后置）
- **证据采集：** 静态元数据，不抓真实网页
- **GitHub 输入：** `repo_url + commit_sha` 强制
- **合法性边界：** respect robots.txt + 禁止登录态

---

## 4. 新方向的核心目标：从“审计/打包工具链”升级为“智能框架生成 Skill”
项目后续新增的关键目标，是把 old `new-gm` 中的 GM OS **意图集合**迁移到 SkillForge 新项目里，用新代码实现一个“**意图 -> 生成可发布 Skill**”的智能框架。

### 4.1 迁移的不是旧代码，而是 3 类语义资产
1. **Intent 目录**：GM OS 里到底有哪些意图
2. **Intent 合同**：每个意图的输入 / 输出 / 约束 / 必要证据 / 最低 Level
3. **Intent -> Gate Pipeline 映射**：每个意图经过哪些 Gate，失败对应哪些 `error_code`，必须产出哪些 `EvidenceRef`

### 4.2 迁移成功的判据
同一个：
- `intent_id`
- `repo_url + commit_sha`
- `at_time`

应该能稳定产出：
- 同一逻辑语义的 `GateDecision`
- 可复核的 `EvidenceRef`
- 一份可复现的 `L3 AuditPack`

---

## 5. 推荐的总体结构：把外螺旋压扁，而不是再造大框架
讨论中已经形成的共识是：**外螺旋不要再做成庞大代码架构**，而应该压扁成三层。

### 5.1 三层结构
| 层 | 角色 | 本质 |
|---|---|---|
| Intent Catalog | 表达意图 | 纯数据合同 |
| Orchestration | 组织执行 | 纯配置 / 固定 Gate 流水线 |
| Skills | 实际实现 | 可替换、可升级的策略与能力 |

### 5.2 对新账号最重要的一句
**迁移的是意图语义与合同，不迁移旧代码实现。**

### 5.3 另一个必须记住的口径
**外螺旋 = Intent Catalog（合同）+ Orchestration（配置）+ Skills（实现）**

---

## 6. Intent Catalog 的建议落地方式
建议新增：
- `contracts/intents/<intent_id>.yml`

### 6.1 每个 intent 合同建议至少包含
- `intent_id`
- `summary`
- `inputs_schema`
- `required_gates`
- `minimum_level`
- `required_evidence`
- `outputs`

### 6.2 最小输入口径
最小稳定输入建议固定为：
- `repo_url`
- `commit_sha`
- 可选：`entry_path` / `manifest_path` / 其他辅助字段

### 6.3 建议先落地的核心 intents
- `audit_repo_skill`
- `generate_skill_from_repo`
- `upgrade_skill_revision`
- `tombstone_skill`
- `cognition_10d_output`（见后文第 11 节）

### 6.4 必要映射文件
建议补：
- `docs/INTENT_MIGRATION_MAP.md`
- 或 `orchestration/intent_map.yml`

它至少应记录：
- old GM OS intent -> 新 `intent_id`
- 经过的 Gate
- 失败时的 `error_code`
- L3 必须产出的 `EvidenceRef`

---

## 7. 能 Skill 化到什么程度？
### 7.1 结论
**可以 Skill 化 80%–90%，但不能 100% Skill 化。**

如果真的把裁决权也交给 Skill，自然会掉进：
- Skill 自己审自己
- Skill 自己给自己放行
- Skill 自己解释自己的证据

这会直接毁掉治理可信度。

### 7.2 防回退原则
**Skill 可以负责生成、分析、建议和补全；但不能负责最终裁决。**

---

## 8. 最小微内核（TCB）边界：什么绝不能交给 Skill
讨论里已经把这个边界锁得很清楚。

### 8.1 宪法不是内核代码；宪法是内核依据的规则集
- **宪法（Constitution / Policy）** = 版本化的规则文本或配置
- **内核（Kernel / TCB）** = 可信裁决、证据、复现、边界控制的执行体

### 8.2 内核最小职责（4 个核心动作）
1. 读取 Intent 合同
2. 执行固定 8 Gate 流程
3. 记录 Evidence（hash + locator + provenance）
4. 组装并校验 `L3 AuditPack`

### 8.3 内核还必须补齐的 3 个底座能力
1. **validate.py**：对 contracts / policy / error codes / fix kinds / nodes / schemas 做硬校验
2. **确定性 Intake**：强制 `repo_url + commit_sha`，把 submodule / LFS / ignore 策略写进 provenance，并参与 `Revision` 计算
3. **RAG at_time / Tombstone 口径执行**：snapshot / index 的严格复现规则由内核锁死

### 8.4 可直接复制的一句话
**Skill 做“生成 / 分析 / 建议”，内核做“裁决 / 证据 / 复现 / 边界”。**

---

## 9. Skill 该负责什么
以下能力建议全部 Skill 化：
- `scan_skill_shape`：识别“什么叫 skill” + 计算 fit_score
- `static_denylist_scan`：静态危险模式扫描（规则版本化）
- `spec_drafter_<intent>`：意图 -> 合同草案
- `scaffold_python`：Python 模板生成
- `pack_builder_helper`：协助清点 pack 文件与证据引用

### 9.1 Skill 不应负责的内容
- `GateDecision` 最终 PASS / FAIL
- `Level` 判定
- `AuditPack` 最小清单闭环判定
- `at_time / tombstone` 口径裁决

---

## 10. 推荐的 v0 运行形态
建议统一 CLI 入口：

`skillforge run <intent_id> --repo <url> --commit <sha> --at-time <t>`

### 10.1 这条主链路意味着什么
内核只负责：
- 读取合同
- 跑 Gate
- 写 Evidence
- 组装 `L3 pack`
- 写 RAG index

其余一律交给 Skills/策略插件。

### 10.2 v0 最关键的工程补齐项
1. **Repo Intake 确定性**
2. **“什么叫 skill”识别规则 + fit score 阈值**
3. **静态扫描规则版本化**
4. **Evidence 容器真实化**
5. **RAG 版本化复现闭环的回归测试**

---

## 11. 一个新增且必须记住的迁移目标：10阶高维认知输出
讨论中额外确认：old `new-gm` 上的 **“10阶高维认知输出”** 是一个非常重要的老意图，不能丢。

### 11.1 迁移要求
- 迁移同款意图到 GM-SkillForge
- 尽可能把原实现翻译成一个 **可审计的 Skill**
- 仍然必须满足：
  - contracts-first
  - EvidenceRef 可落地
  - `L3 AuditPack` 兼容

### 11.2 新账号要理解的重点
这不是“把一段旧代码搬过来”，而是把这个高价值意图重新表达为：
- 一个新的 `intent_id`
- 一个明确的输入/输出合同
- 一个对应的 spec drafter / scaffold / evidence 方案
- 一个能进入 L5 总体路线图的正式组成部分

---

## 12. n8n 的角色：它可以全包干活，但不能拥有裁决权
后续闭环中，n8n 是重要外部层，而且很可能会比 old `new-gm` 更强。

### 12.1 最终分工口径（必须锁死）
- **n8n = Orchestrator（全包干活）**
- **SkillForge = Governor（只做审核裁决 + 证据链 + 放行令牌）**

### 12.2 n8n 可以负责什么
- 抓 GitHub repo
- checkout / submodule / LFS / 打包快照
- 跑 CI
- 开 PR / 合并
- 打 tag / create release
- 同步 registry
- 通知 Slack / Email
- 重试 / 队列 / 补偿 / 人工审批 / 编排

### 12.3 SkillForge 必须独占什么
- 8 Gate 裁决
- Level 判定
- EvidenceRef 写入与 hash
- `L3 AuditPack` 达标检查
- `RAG(at_time / tombstone)` 口径
- **签发 / 撤销 publish permit（放行令牌）**

### 12.4 关键闭环流程（推荐）
1. **n8n 抓取仓库（GitHub Intake）**
   - 获取 `repo_url + commit_sha`
   - clone / checkout / 打包快照
2. **SkillForge 复核式 Intake**
   - 校验 `commit_sha`
   - 计算 `snapshot_hash / revision`
   - 写 provenance
3. **SkillForge 执行 8 Gate**
   - 产 `GateDecision + EvidenceRef + L3 AuditPack`
4. **SkillForge 签发 publish permit**
   - 绑定 `intent_id + repo@commit + revision + audit_pack_hash + expiration`
5. **n8n 负责发布与通知**
   - 没有 permit 就不允许发布/打 tag/release

### 12.5 3 条防绕过硬规则
1. **发布必须有 permit**
2. **证据与 AuditPack 由 SkillForge 产出且不可变**
3. **输入必须确定性：`repo_url + commit_sha + at_time`**

### 12.6 为什么会比 old new-gm 更好
- 编排、连接器、人工审批、通知、重试等复杂度交给 n8n
- 可复核审计、证据链、历史复现、放行判断交给 SkillForge
- 两边职责清晰，互相制衡，闭环更稳

---

## 13. 宪法最高层、核心 Skill、n8n 分层策略（给新账号的极短记忆版）
### 13.1 宪法最高层
- 不可被 Skill 或 n8n 越权修改
- 作为 `constitution_risk_gate` 与发布/下架策略依据
- 版本化后写入 provenance / AuditPack

### 13.2 核心 Skill（v0 最小集）
- `scan_skill_shape`
- `static_denylist_scan`
- `spec_drafter_<intent>`
- `scaffold_python`
- `pack_builder_helper`

### 13.3 n8n 分层策略
- n8n 只做编排，不做治理
- n8n 每个关键动作都调用 SkillForge 的接口
- n8n 不内建 PASS/FAIL 逻辑

---

## 14. 路线图口径：终点不变，但内容加宽
讨论中又新增了一条非常重要的路线图结论：

### 14.1 路线图状态
- 最高终点仍然是 **L5**
- 当前整体认知大约在 **L2.5**
- 但新增了“迁移 old new-gm 原有架构意图并实现”的计划

### 14.2 路线图如何变化
- **不改终点、不改层级**
- 只是把“迁移意图 + 实现意图”平摊进 `L5` 的总体架构里
- 结果还是 `L5`，但内容宽度和丰富度大很多

### 14.3 L4.5 的新职责
- 在 **L4.5** 就开始把 `n8n` 融入实现闭环
- 到 `L5` 做最终验收收官

### 14.4 可以直接记的一句话
**L5 仍是终点；n8n 从 L4.5 开始融入；意图迁移不是额外支线，而是平摊进 L5 总体架构。**

---

## 15. 对新账号最重要的“不要跑偏”清单
### 15.1 不要做的事
- 不要回去拷 old `new-gm` 的旧代码
- 不要把外螺旋重新做成大框架
- 不要让 Skill 自己决定 PASS/FAIL
- 不要让 n8n 自己判断是否发布
- 不要接受 `latest` 这种非确定性输入
- 不要在 v0 就把真实执行 / 压测 / 网页抓取全部拉进来

### 15.2 一旦有人想“又堆回框架层”，就用这句卡死范围
**intent + repo@commit + at_time -> EvidenceRef 闭环 -> L3 AuditPack**

---

## 16. 对新账号的最短口径摘要（五句话记忆版）
1. GM-SkillForge 是一个全新仓库，不复刻 old GM OS，而是把“意图”重建为合同、证据和可发布 Skill。  
2. 系统骨架是 `contracts-first + 8 Gates + EvidenceRef + AuditPack + Revision/at_time/Tombstone`。  
3. 大部分能力都可以 Skill 化，但裁决层不能：内核必须掌握 Gate、Evidence、L3 AuditPack、validate、确定性 Intake、RAG 复现口径。  
4. n8n 后续将作为 Orchestrator 接入，负责 GitHub 抓取、发布、通知与编排；SkillForge 只做审核、证据链和放行令牌。  
5. 最终终点仍是 `L5`；从 `L4.5` 开始融入 n8n；“10阶高维认知输出”等 old new-gm 核心意图也要迁移进来，并翻译成可审计 Skill。

---

## 17. 给 Codex / 新账号的启动顺序建议
1. 先确认 **宪法最高层 + 内核边界 + n8n 不越权**
2. 再确认 **Intent Catalog + intent_map**
3. 再落地 **核心 Skill 最小集**
4. 再补 **deterministic intake + evidence.jsonl + fit score + denylist rules**
5. 最后把 **n8n 接口与 publish permit** 接进 `L4.5 -> L5`

---

## 18. 结论
这条路已经不是“再做一个框架”，而是在做一个：

- 可审计
- 可追责
- 可复现
- 可持续演进
- 可把现实世界编排外包给 n8n
- 同时又不会失去治理边界

的 Skill 工厂与审计治理系统。

**最终总口径：**
- **迁移的是意图语义与合同，不迁移旧代码实现。**
- **外螺旋压扁为：Intent Catalog + Orchestration + Skills。**
- **SkillForge 内核负责治理与裁决，n8n 负责现实世界执行与编排。**
- **L5 终点不变，L4.5 融入 n8n，整体一路走穿到底。**
