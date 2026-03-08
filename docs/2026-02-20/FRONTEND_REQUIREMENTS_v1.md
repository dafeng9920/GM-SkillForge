# 前端功能需求规格 v1.7

> 文档版本: v1.7
> 创建日期: 2026-02-20
> 更新日期: 2026-02-20
> 状态: DRAFT

本文档整理后端已实现的功能，明确需要在前端展示的功能列表，作为前端开发的参考依据。

---

## 1. 前端功能 ↔ 后端接口对照表（总览）

> 📌 **核心映射表**：每个前端功能对应的后端 API 接口

### 1.1 完整映射表

| 前端页面/功能 | 前端路由 | 后端 API 端点 | 方法 | 后端状态 | 前端状态 | 优先级 |
|--------------|---------|--------------|------|---------|---------|--------|
| **L4 工作台** | `/workbench` | | | | | |
| ├─ 10维认知分析 | `/divergence` | `/api/v1/cognition/generate` | POST | Implemented | ✅ 已连接 | P0 |
| ├─ 采用工作项 | `/work` | `/api/v1/work/adopt` | POST | Implemented | ✅ 已连接 | P0 |
| ├─ 执行工作项 | `/work` | `/api/v1/work/execute` | POST | Implemented | ⚠️ 部分 | P0 |
| ├─ 工作项详情 | `/work-items/:id` | `/governance/work-items/{id}` | GET | Planned | ❌ 未开发 | P1 |
| └─ 更新工作项 | `/work-items/:id` | `/governance/work-items/{id}` | PATCH | Planned | ❌ 未开发 | P1 |
| **N8N 控制中心** | `/n8n` | | | | | |
| ├─ 执行意图 | `/n8n/run-intent` | `/api/v1/n8n/run_intent` | POST | Implemented | ❌ 未开发 | **P0** |
| ├─ AuditPack浏览 | `/n8n/audit-packs` | `/api/v1/n8n/fetch_pack` | POST | Implemented | ❌ 未开发 | P1 |
| ├─ RAG查询 | `/n8n/rag-query` | `/api/v1/n8n/query_rag` | POST | Implemented | ❌ 未开发 | P1 |
| └─ 健康检查 | `/n8n/health` | `/api/v1/n8n/health` | GET | Implemented | ❌ 未开发 | P2 |
| **技能管理** | `/skills` | | | | | |
| ├─ 外部技能导入 | `/skills/import` | `/api/v1/n8n/import_external_skill` | POST | Implemented | ❌ 未开发 | **P0** |
| └─ 技能注册表 | `/skills/registry` | *(内部服务)* | - | Internal | ❌ 未开发 | P2 |
| **治理中心** | `/governance` | | | | | |
| ├─ Gate仪表盘 | `/governance/gates` | *(内部服务)* | - | Internal | ❌ 未开发 | P1 |
| ├─ 许可证管理 | `/governance/permits` | *(GatePermit)* | - | Internal | ❌ 未开发 | P0 |
| └─ 工作项列表 | `/governance/work-items` | `/governance/work-items` | GET | Planned | ❌ 未开发 | P1 |
| **历史记录** | `/history` | | | | | |
| ├─ 认知历史 | `/history/cognition` | `/cognition/10d/{commit_sha}` | GET | Planned | ❌ 未开发 | P2 |
| └─ 审计日志 | `/history/audit` | *(AuditPackStore)* | - | Internal | ❌ 未开发 | P2 |
| **系统** | | | | | | |
| └─ 健康检查 | `/health` | `/api/v1/health` | GET | Implemented | ✅ 可用 | P2 |

### 1.2 统计摘要

| 统计项 | 数量 | 口径说明 |
|-------|------|---------|
| 后端 API 端点（已实现） | 9 | 当前代码可直接调用 |
| 后端能力（Planned/Internal） | 4 | 规划接口 + 内部服务 |
| 前端已连接 | 4 | 已完成前后端对接 |
| 前端部分实现 | 1 | 仅部分链路可用 |
| 前端未开发 | 8 | 尚未完成前端页面/交互 |
| **P0 优先级** | 6 | 按功能项统计 |
| **P1 优先级** | 5 | 按功能项统计 |
| **P2 优先级** | 2 | 按功能项统计 |

后端状态定义:
- `Implemented`: 已在 API 路由中实现并可调用
- `Planned`: 文档规划，当前未暴露路由
- `Internal`: 内部能力/服务，非直接 REST 端点

### 1.3 优先级定义

- **P0 (Critical)**: 核心工作流必须，阻塞主流程
- **P1 (High)**: 重要功能，影响用户体验
- **P2 (Medium)**: 增强功能，提升可观测性
- **P3 (Low)**: 锦上添花，后续迭代

---

## 2. 详细功能 ↔ 接口映射

### 2.1 L4 核心功能

### 2.1 已连接的功能

| 前端功能 | API 端点 | 方法 | 请求参数 | 响应字段 | 前端状态 |
|---------|----------|------|---------|---------|---------|
| 10维认知分析 | `/api/v1/cognition/generate` | POST | `repo_url`, `commit_sha`, `context` | `cognition_data`, `dimensions[10]` | ✅ 已连接 |
| 采用工作项 | `/api/v1/work/adopt` | POST | `reason_card`, `repo_url`, `commit_sha` | `work_item`, `permit_id`, `blocked_state` | ✅ 已连接 |
| 执行工作项 | `/api/v1/work/execute` | POST | `work_item_id`, `permit_token` | `execution_result`, `release_allowed` | ⚠️ 部分实现 |
| 健康检查 | `/api/v1/health` | GET | - | `status`, `version` | ✅ 可用 |

### 2.2 待开发的 L4 功能

| 前端功能 | 前端路由 | API 端点 | 方法 | 请求参数 | 响应字段 | 优先级 |
|---------|---------|----------|------|---------|---------|--------|
| 工作项详情页 | `/work-items/:id` | `/governance/work-items/{id}` | GET | `id` (path) | `work_item` 完整对象 | P1 |
| 更新工作项 | `/work-items/:id/edit` | `/governance/work-items/{id}` | PATCH | `id`, `updates` | 更新后的 `work_item` | P1 |
| 认知历史查询 | `/history/cognition` | `/cognition/10d/{commit_sha}` | GET | `commit_sha` | `cognition_data`, `cached_at` | P2 |

### 2.3 前端组件需求

**工作项管理页面** (P1)
- 工作项列表视图
- 工作项详情页
- 工作项状态更新表单
- 工作项历史记录

**认知历史页面** (P2)
- 按 commit_sha 查询历史评估
- 评估对比视图
- 评估趋势图表

---

## 3. N8N 编排功能 ↔ 接口映射

### 3.1 N8N API 端点映射表

| 前端功能 | 前端路由 | API 端点 | 方法 | 请求参数 | 关键响应字段 | 前端状态 | 优先级 |
|---------|---------|----------|------|---------|------------|---------|--------|
| **执行意图** | `/n8n/run-intent` | `/api/v1/n8n/run_intent` | POST | `repo_url`, `commit_sha`, `at_time`, `intent_id`, `requester_id`, `tier` | `run_id`, `gate_decision`, `release_allowed`, `evidence_ref` | ❌ 未开发 | **P0** |
| **AuditPack浏览** | `/n8n/audit-packs` | `/api/v1/n8n/fetch_pack` | POST | `run_id`, `evidence_ref`, `at_time` | `pack`, `replay_pointer`, `fetched_at` | ❌ 未开发 | P1 |
| **RAG查询** | `/n8n/rag-query` | `/api/v1/n8n/query_rag` | POST | `query`, `at_time`, `repo_url`, `commit_sha`, `top_k` | `results[]`, `replay_pointer` | ❌ 未开发 | P1 |
| **外部技能导入** | `/skills/import` | `/api/v1/n8n/import_external_skill` | POST | `repo_url`, `commit_sha`, `external_skill_ref`, `requester_id` | `quarantine_id`, `permit_id`, `registry_entry_id`, `pipeline_state` | ❌ 未开发 | **P0** |
| **健康检查** | `/n8n/health` | `/api/v1/n8n/health` | GET | - | `status`, `routes[]` | ❌ 未开发 | P2 |

### 3.2 执行意图 - 详细映射

**API**: `POST /api/v1/n8n/run_intent`

| 前端组件 | 字段名 | 类型 | 必填 | 验证规则 | 说明 |
|---------|--------|------|------|---------|------|
| repo_url 输入框 | `repo_url` | string | ✅ | URL格式 | 仓库地址 |
| commit_sha 输入框 | `commit_sha` | string | ✅ | 40位hex | Git提交哈希 |
| at_time 选择器 | `at_time` | string | ❌ | ISO-8601 | 固定时间戳，禁止"latest" |
| intent_id 输入框 | `intent_id` | string | ✅ | - | 意图标识 |
| requester_id 输入框 | `requester_id` | string | ✅ | - | 请求者标识 |
| context 编辑器 | `context` | object | ❌ | JSON | 上下文数据 |
| tier 选择器 | `tier` | string | ❌ | 枚举 | 会员等级，默认FREE |

**响应字段 → 前端展示**:

| 响应字段 | 前端展示位置 | 组件类型 |
|---------|-------------|---------|
| `run_id` | 执行结果卡片 | 文本+复制按钮 |
| `gate_decision` | 状态标签 | Badge (ALLOW=绿色/BLOCK=红色) |
| `release_allowed` | 开关状态 | Toggle/Icon |
| `evidence_ref` | 链接 | 可点击跳转到AuditPack |
| `data.execution_status` | 状态文本 | 文本 |
| `data.permit_id` | 许可证信息 | 文本+详情链接 |

**错误响应字段 → 前端展示**:

| 响应字段 | 前端展示位置 | 组件类型 |
|---------|-------------|---------|
| `error_code` | 错误标题 | 错误码标签 |
| `blocked_by` | 错误原因 | 文本说明 |
| `message` | 详细信息 | 错误消息框 |
| `forbidden_field_evidence` | 安全警告 | 警告面板 |

### 3.3 AuditPack 浏览器 (P1)

**功能描述**: 查询和浏览审计包历史

**请求参数** (`fetch_pack`):
```json
{
  "run_id": "string (optional)",
  "evidence_ref": "string (optional)",
  "at_time": "string (ISO-8601, optional)"
}
```

约束: `run_id` 与 `evidence_ref` 不能同时缺失，至少提供其一；否则返回 `N8N_MISSING_IDENTIFIER`。

**UI 组件**:
- [ ] 搜索表单
  - run_id 搜索输入
  - evidence_ref 搜索输入
  - 时间范围选择器
- [ ] AuditPack 列表视图
- [ ] AuditPack 详情页
  - 完整 JSON 展示
  - replay_pointer 信息
  - fetched_at 时间戳

### 3.4 RAG 查询界面 (P1)

**功能描述**: 知识库检索查询

**请求参数** (`query_rag`):
```json
{
  "query": "string (required)",
  "at_time": "string (ISO-8601, required)",
  "repo_url": "string (optional)",
  "commit_sha": "string (optional)",
  "top_k": "integer (default: 5, range: 1-100)"
}
```

**UI 组件**:
- [ ] RAG 搜索表单
  - 查询输入框
  - at_time 时间选择器（必须固定时间，禁止 "latest"）
  - repo_url / commit_sha 可选输入
  - top_k 滑块/输入
- [ ] 搜索结果列表
  - 相关度排序
  - 片段高亮
- [ ] replay_pointer 展示

### 3.5 外部技能导入向导 (P0)

**功能描述**: 6步治理流水线可视化

**请求参数** (`import_external_skill`):
```json
{
  "repo_url": "string (required)",
  "commit_sha": "string (required)",
  "external_skill_ref": "string (required)",
  "requester_id": "string (required)",
  "skill_name": "string (optional)",
  "skill_version": "string (optional)",
  "source_repository": "string (optional)",
  "context": "object (optional)",
  "tier": "string (default: FREE)"
}
```

**6步流水线状态**:
| 步骤 | 状态名 | 功能描述 |
|------|--------|---------|
| S1 | `S1_QUARANTINE` | 导入到隔离区 |
| S2 | `S2_CONSTITUTION_GATE` | 宪章门控检查（边界/权限/禁止能力） |
| S3 | `S3_SYSTEM_AUDIT` | L1-L5 系统审计 |
| S4 | `S4_DECISION` | 决策（需要 PASS@L3+） |
| S5 | `S5_PERMIT_ISSUANCE` | 许可证签发 |
| S6 | `S6_REGISTRY_ADMISSION` | 注册表接纳 |

**UI 组件**:
- [ ] 步骤进度条 (S1 → S6)
- [ ] 每步状态展示: PENDING / IN_PROGRESS / PASS / FAIL
- [ ] L1-L5 审计分数雷达图/条形图
  - L1: contract_audit
  - L2: control_audit
  - L3: security_audit
  - L4: evidence_audit
  - L5: reproducibility_audit
- [ ] 导入结果展示
  - quarantine_id
  - permit_id
  - registry_entry_id
  - skill_revision
- [ ] 失败时展示 required_changes 列表

### 3.6 NEW-GM 意图迁移：五段式编排 + 三张卡片

本小节基于 `D:\NEW-GM` 源实现提炼“意图层”，并在当前 SkillForge 前端落地为兼容投影。

来源（NEW-GM）:
- `D:\NEW-GM\src\services\orchestration\five_stage_plan.py`
- `D:\NEW-GM\src\services\orchestration\three_cards_builder.py`
- `D:\NEW-GM\ui\app\src\types\workflow.ts`
- `D:\NEW-GM\docs\五段式工作流可视化 UI 设计规范 v0.1.md`

#### 五段式编排（n8n 可视化口径）

采用 NEW-GM 的五段式 UI 语义：

1. `trigger`
2. `collect`
3. `process`
4. `deliver`
5. `report`

#### 三张卡片（产品展示口径）

采用 NEW-GM 类型语义：

1. `understanding`
2. `plan`
3. `execution_contract`

#### 当前后端兼容映射（先渲染，后直连）

| 迁移对象 | 当前 SkillForge 数据来源 | 前端渲染策略 |
|---|---|---|
| `trigger` | `POST /api/v1/n8n/run_intent` 请求+回执 | 请求成功即点亮 trigger |
| `collect` | `POST /api/v1/n8n/fetch_pack` | 拿到 pack/replay_pointer 即完成 |
| `process` | `POST /api/v1/n8n/query_rag` | 有结果或结构化错误即完成 |
| `deliver` | `gate_decision` + `release_allowed` | `ALLOW` 绿，其它红/橙 |
| `report` | `run_id` + `evidence_ref` + 汇总信息 | 形成可追溯报告卡 |
| `understanding` | run_intent 输入摘要 | 展示 repo/commit/at_time/intent/requester |
| `plan` | pack + rag + 决策摘要 | 展示回放指针、关键结果、风险提示 |
| `execution_contract` | permit/error 字段 | 展示 permit_id/validation/error_code/blocked_by/next_action |

#### 约束

1. n8n 仅编排，不可注入 `gate_decision/release_allowed/permit_token/run_id/evidence_ref`。  
2. 三卡属于前端展示层，不改变后端裁决逻辑。  
3. 后续若后端输出标准 `five_stage_plan/three_cards`，前端切换为直读模式。  

---

## 4. Gate 系统功能

### 4.1 Gate 列表

后端实现了完整的 Gate 流水线，需要前端可视化：

| Gate | 文件 | 功能描述 | 优先级 |
|------|------|---------|--------|
| `gate_intake` | `skills/gates/gate_intake.py` | 仓库/技能接入 | P1 |
| `gate_scan` | `skills/gates/gate_scan.py` | 代码扫描 | P1 |
| `gate_risk` | `skills/gates/gate_risk.py` | 风险评估 | P1 |
| `gate_sandbox` | `skills/gates/gate_sandbox.py` | 沙箱测试 | P1 |
| `gate_permit` | `skills/gates/gate_permit.py` | 许可证验证 | **P0** |
| `gate_draft_spec` | `skills/gates/gate_draft_spec.py` | 规格草稿 | P2 |
| `gate_publish` | `skills/gates/gate_publish.py` | 发布门控 | P2 |
| `gate_scaffold` | `skills/gates/gate_scaffold.py` | 脚手架生成 | P2 |

### 4.2 Gate 仪表盘 (P1)

**UI 组件**:
- [ ] Gate 流水线可视化
  - 水平/垂直流程图
  - 每个 Gate 状态: PENDING / RUNNING / PASSED / FAILED / SKIPPED
- [ ] Gate 详情展开面板
  - 输入参数
  - 输出结果
  - 耗时统计
  - 错误信息（如有）
- [ ] Gate 统计图表
  - 通过率趋势
  - 平均耗时
  - 失败原因分布

### 4.3 Permit 许可证管理 (P0)

**UI 组件**:
- [ ] 许可证状态展示
  - 当前后端稳定可用字段: `permit_id`, `validation_timestamp`
  - `GRANTED / PENDING / REVOKED / EXPIRED` 属于扩展状态，需要后端新增 `permit_status` 后再启用
  - permit_id 显示
  - 签发时间 / 过期时间
- [ ] 许可证验证表单
  - permit_token 输入
  - 验证结果展示
- [ ] 许可证详情
  - allowed_actions
  - scope
  - subject
  - 签名验证状态

---

## 5. 边界安全功能

### 5.1 N8N 边界适配器

后端实现了严格的边界安全验证，前端应展示相关状态：

**白名单字段**:
```
repo_url, commit_sha, at_time, requester_id, intent_id, n8n_execution_id
```

**禁止字段** (n8n 不能设置):
```
gate_decision, release_allowed, permit_token, evidence_ref, permit_id, run_id
```

**at_time 验证规则**:
- 必须是固定 ISO-8601 时间戳
- 禁止值: `latest`, `now`, `current`, `today`

### 5.2 边界安全 UI (P2)

**UI 组件**:
- [ ] 输入验证状态指示器
- [ ] 禁止字段警告提示
- [ ] at_time 格式验证反馈
- [ ] 安全审计日志展示

---

## 6. 错误码参考

### 6.1 N8N 错误码

| 错误码 | 描述 | 前端处理建议 |
|--------|------|-------------|
| `N8N_FORBIDDEN_FIELD_INJECTION` | n8n 尝试注入禁止字段 | 显示安全警告，提示联系管理员 |
| `N8N_PERMIT_ISSUE_FAILED` | SkillForge 内部签发 permit 失败 | 提示检查服务配置（如 `PERMIT_HS256_KEY`） |
| `N8N_MEMBERSHIP_DENIED` | 会员权限不足 | 引导升级会员等级 |
| `N8N_MISSING_IDENTIFIER` | fetch_pack 缺少 `run_id/evidence_ref` | 提示用户至少填写一个查询标识 |
| `N8N_INTERNAL_ERROR` | 内部错误 | 显示通用错误，建议重试 |
| `RAG-AT-TIME-MISSING` | at_time 参数缺失 | 提示填写 at_time |
| `RAG-AT-TIME-DRIFT-FORBIDDEN` | at_time 使用了漂移值 | 提示使用固定时间戳 |
| `RAG-VALIDATION-ERROR` | RAG 查询参数校验失败 | 提示检查 query/at_time/top_k 等输入 |
| `RAG-INTERNAL-ERROR` | RAG 内部错误 | 显示通用错误并建议重试 |
| `CONSTITUTION_GATE_FAILED` | 外部技能导入宪章门失败 | 显示 required_changes 并阻断导入 |
| `SYSTEM_AUDIT_FAILED` | 外部技能系统审计未达标 | 展示审计分层结果与整改项 |
| `IMPORT_INTERNAL_ERROR` | 外部技能导入内部错误 | 显示通用错误并保留 evidence_ref |

### 6.2 Permit 错误码

| 错误码 | 描述 | 前端处理建议 |
|--------|------|-------------|
| `E001` | 无许可证 | 引导获取许可证 |
| `E002` | 许可证无效 | 重新签发许可证 |
| `E003` | 签名错误 | 安全警告 |
| `E004` | 许可证过期 | 续期许可证 |
| `E005` | 作用域不匹配 | 检查请求范围 |
| `E006` | 主体不匹配 | 检查身份验证 |
| `E007` | 许可证已撤销 | 联系管理员 |

---

## 7. UI 设计规范

### 7.1 视觉风格（Style）

| 方案 | 描述 | 推荐度 |
|------|------|--------|
| **方案A：工业控制台** | 浅灰底 + 蓝绿主色，专业稳重 | ⭐⭐⭐ 推荐 |
| 方案B：审计中台 | 白底高对比，证据导向 | ⭐⭐ 备选 |
| 方案C：科技仪表盘 | 深浅分层，状态突出 | ⭐⭐ 备选 |

**选定方案：A - 工业控制台**
- 背景色：`#F5F7FA`（浅灰）
- 主色调：`#1890FF`（蓝） / `#13C2C2`（青绿）
- 文字色：`#1F2937`（主文本） / `#6B7280`（次文本）

### 7.2 产品格调（Tone）

| 格调原则 | 具体要求 |
|---------|---------|
| **严谨可审计** | 少情绪文案，多证据字段；每条记录可追溯 |
| **操作透明** | 每一步都给 `run_id` / `evidence_ref`，支持复制和跳转 |
| **Fail-Closed 友好** | 报错明确"为什么被拦截"、"怎么修"，不模糊带过 |

### 7.3 UI 设计规则（Design Rules）

#### 信息层级
```
┌─────────────────────────────────────────┐
│ 1. 结论层：ALLOW/BLOCK 状态（最醒目）      │
├─────────────────────────────────────────┤
│ 2. 标识层：run_id, evidence_ref（可复制）│
├─────────────────────────────────────────┤
│ 3. 细节层：输入参数、执行时间、耗时       │
├─────────────────────────────────────────┤
│ 4. 证据层：完整 JSON / replay_pointer    │
└─────────────────────────────────────────┘
```

#### 状态色统一

| 状态 | 颜色 | Hex | 使用场景 |
|------|------|-----|---------|
| **ALLOW** | 绿 | `#10B981` | gate_decision=ALLOW, release_allowed=true |
| **BLOCK** | 红 | `#EF4444` | gate_decision=BLOCK, 执行失败 |
| **PENDING** | 灰 | `#9CA3AF` | 等待中、未开始 |
| **WARN** | 橙 | `#F59E0B` | 警告、需注意 |
| **RUNNING** | 蓝 | `#3B82F6` | 执行中、进行中 |

#### 卡片结构统一

```
┌────────────────────────────────────────┐
│ 📋 标题区                              │
│   - 卡片标题（加粗）                    │
│   - 状态 Badge（右上角）                │
├────────────────────────────────────────┤
│ 📥 输入区                              │
│   - 表单字段（左标签右输入）            │
│   - 必填标记                            │
├────────────────────────────────────────┤
│ 📤 结果区                              │
│   - 执行结果                            │
│   - run_id / evidence_ref              │
├────────────────────────────────────────┤
│ 🔍 证据区                              │
│   - 展开查看详情                        │
│   - JSON 查看器 / replay_pointer        │
└────────────────────────────────────────┘
```

#### 表单统一规则

| 规则 | 说明 |
|------|------|
| 布局 | 左标签右输入，标签宽度统一 120px |
| 错误提示 | 贴字段显示，不弹全局模糊报错 |
| 必填标记 | 红色 `*` 在标签后 |
| 校验时机 | 失焦校验 + 提交前全量校验 |
| 禁用状态 | 灰色背景 + 禁止光标 |

### 7.4 展示方式（Presentation）

#### Run Intent 页面
```
┌────────────────────────────────────────┐
│ 📝 执行意图                            │
├────────────────────────────────────────┤
│ [表单区 - 上]                          │
│ repo_url: [________________]           │
│ commit_sha: [________________]         │
│ at_time: [____] 📅 intent_id: [____]   │
│ requester_id: [____] tier: [FREE ▼]    │
│                    [执行] [重置]        │
├────────────────────────────────────────┤
│ 📊 执行结果时间线 - 下                  │
│ ├─ 10:00:01 提交请求                   │
│ ├─ 10:00:02 GatePermit 验证通过        │
│ ├─ 10:00:03 执行完成                   │
│ └─ ✅ ALLOW  run_id: RUN-N8N-xxx       │
└────────────────────────────────────────┘
```

#### Import Skill 页面
```
┌────────────────────────────────────────┐
│ 📦 外部技能导入                         │
├────────────────────────────────────────┤
│ 6步流水线（横向进度条）                 │
│ [S1●]──[S2●]──[S3●]──[S4○]──[S5○]──[S6○]│
│  隔离   宪章   审计   决策   许可   注册  │
├────────────────────────────────────────┤
│ 当前步骤详情（抽屉/展开面板）           │
│ ┌──────────────────────────────────┐   │
│ │ S3: 系统审计                     │   │
│ │ L1 contract_audit:  PASS (95)    │   │
│ │ L2 control_audit:    PASS (90)   │   │
│ │ L3 security_audit:   PASS (88)   │   │
│ │ L4 evidence_audit:   PASS (92)   │   │
│ │ L5 reproducibility:  PASS (85)   │   │
│ └──────────────────────────────────┘   │
├────────────────────────────────────────┤
│ 导入结果                                │
│ quarantine_id: Q-XXX                   │
│ permit_id: PERMIT-EXT-XXX              │
│ registry_entry_id: REG-XXX             │
└────────────────────────────────────────┘
```

#### Gate Dashboard 页面
```
┌────────────────────────────────────────┐
│ 🚧 Gate 仪表盘                          │
├────────────────────────────────────────┤
│ 流程图（水平）                          │
│ [intake]→[scan]→[risk]→[sandbox]→[permit]│
│    ✅      ✅      ✅       ⏳       ⏸️  │
├────────────────────────────────────────┤
│ Gate 明细表                             │
│ ┌─────────────────────────────────────┐│
│ │ Gate    │ 状态  │ 耗时  │ 错误码   ││
│ │ intake  │ PASS  │ 120ms │ -        ││
│ │ scan    │ PASS  │ 350ms │ -        ││
│ │ risk    │ PASS  │ 200ms │ -        ││
│ │ sandbox │ RUN   │ 1.2s  │ -        ││
│ │ permit  │ PEND  │ -     │ -        ││
│ └─────────────────────────────────────┘│
└────────────────────────────────────────┘
```

#### AuditPack 页面
```
┌──────────────┬─────────────────────────┐
│ 📋 列表      │ 📄 详情                  │
├──────────────┼─────────────────────────┤
│ RUN-N8N-001  │ run_id: RUN-N8N-001     │
│ 2026-02-20   │ evidence_ref: EV-XXX    │
│ ALLOW        │ gate_decision: ALLOW    │
│              │ release_allowed: true   │
├──────────────┤ ┌─────────────────────┐ │
│ RUN-N8N-002  │ │ JSON 查看器         │ │
│ 2026-02-19   │ │ {                   │ │
│ BLOCK        │ │   "data": {...},    │ │
│              │ │   "replay_pointer": │ │
│              │ │     {...}           │ │
├──────────────┤ │ }                   │ │
│ RUN-N8N-003  │ └─────────────────────┘ │
│ ...          │                         │
└──────────────┴─────────────────────────┘
```

#### RAG 查询页面
```
┌────────────────────────────────────────┐
│ 🔍 RAG 知识库查询                       │
├────────────────────────────────────────┤
│ [查询区]                                │
│ query: [________________________]      │
│ at_time: [____] 📅 top_k: [5] ────     │
│ repo_url: [________] (可选)            │
│                    [搜索] [重置]        │
├────────────────────────────────────────┤
│ [命中片段]                              │
│ ┌──────────────────────────────────┐   │
│ │ 1. 相关度: 0.95                  │   │
│ │    "...高亮的<span>匹配</span>内容..."│  │
│ │    📍 docs/example.md:42         │   │
│ ├──────────────────────────────────┤   │
│ │ 2. 相关度: 0.87                  │   │
│ │    "...另一段匹配内容..."         │   │
│ └──────────────────────────────────┘   │
├────────────────────────────────────────┤
│ 📍 replay_pointer                      │
│ snapshot_ref: snap-xxx                 │
│ at_time: 2026-02-20T10:00:00Z          │
└────────────────────────────────────────┘
```

### 7.5 字体与间距

| 属性 | 值 | 说明 |
|------|-----|------|
| 主字体 | `Noto Sans SC` | 中文优先 |
| 等宽字体 | `JetBrains Mono` | 仅用于 run_id / evidence_ref / 错误码 / JSON 片段 |
| 基础间距 | `4px` | scale: 4/8/12/16/24/32/48 |
| 圆角分级 | `10px / 6px / 4px` | 卡片模态 10；输入/中按钮 6；Tag/Badge 4 |
| 阴影 | `0 2px 8px rgba(0,0,0,0.08)` | 卡片阴影 |

---

## 8. 前端页面规划

### 8.1 页面结构（综合冻结）

**v1.0（先交付，5页）**
```
/
├── /execute                     # 执行中心
│   ├── /run-intent              # 执行意图
│   └── /import-skill            # 外部技能导入
├── /audit                       # 审计与查询
│   ├── /packs                   # AuditPack 浏览
│   └── /rag-query               # RAG 查询
└── /system                      # 系统运维
    └── /health                  # 健康监控
```

**v1.1（治理增强）**
- 新增 `/governance/release`（三 Tab：Gate / Permit / Work-items）

页面数量：
- v1.0: 5 页
- v1.1: 6 页

### 8.2 开发阶段规划

**Phase 1 - MVP (P0)**
- [ ] N8N Run Intent 表单 + 结果展示
- [ ] 外部技能导入向导（6步流水线）
- [ ] Permit 状态展示
- [ ] 基础错误处理

**Phase 2 - 核心功能 (P1)**
- [ ] AuditPack 浏览器
- [ ] RAG 查询界面
- [ ] Gate 仪表盘
- [ ] 工作项 CRUD

**Phase 3 - 增强功能 (P2)**
- [ ] 认知历史记录
- [ ] 边界安全 UI
- [ ] 高级统计图表
- [ ] 批量操作

---

## 10. 基线方案评审（综合版冻结）

### 10.1 评审结论（综合）

- 结论：`部分同意（综合采纳）`
- 冻结策略：
  - v1.0 采用方案2：先做 5 页，严格对齐已实现后端能力
  - v1.1 吸收方案1：补齐治理深度（`/governance/release`）

### 10.2 必改项（v1.0）

1. v1.0 不单独上线 permits/work-items 页面，避免超出现有后端能力。  
2. `/system/health` 降级为系统监控模块（可独立页或顶栏抽屉，默认 30s 轮询）。  
3. `/execute/run-intent` 必须“先结论后细节”，首屏展示 `gate_decision + release_allowed`。  
4. `/audit/rag-query` 强制展示 `evidence_ref` 并支持复制。  
5. 顶栏新增 run_id 全局检索，打通 Intent / Audit / RAG 跳转。  

### 10.3 风格与格调冻结规则（综合）

1. 主视觉采用“审计中台（白底高对比，证据导向）”。  
2. 保留工业控制台的状态语义与流程可视化表达。  
3. 证据区使用浅蓝灰底 + 左侧蓝色标线。  
2. `PENDING` 状态增加轻呼吸动画（2s）。  
3. `JetBrains Mono` 仅用于机器字段，不用于普通文案。  
4. 圆角分级固定：10/6/4px。  
5. 间距分级固定：4/8/12/16/24/32/48。  

### 10.4 信息架构风险与缓解（综合）

1. 避免以 `n8n` 命名一级导航，统一按用户任务分组。  
2. `work-items/permits` 在 v1.0 收敛，v1.1 以 release 页 Tab 回归。  
3. 所有 `run_id/evidence_ref` 必须可点击跳转审计详情。  

### 10.5 评分（综合）

| 维度 | 分数 |
|------|------|
| 可用性 | 85 |
| 可实施性 | 80 |
| 一致性 | 90 |
| 可扩展性 | 84 |

### 10.6 冻结摘要（综合）

v1.0 先交付 5 页并严格对齐后端已实现能力，采用审计中台风格，执行“先结论后细节、证据可交互、Fail-Closed 可解释”。v1.1 再补 `/governance/release`（Gate/Permit/Work-items 三 Tab）增强治理深度。通过 run_id/evidence_ref 打通执行、审计、检索闭环。

---

## 11. API 集成参考

### 8.1 基础 URL

```
Development: http://localhost:8000/api/v1
Production: <TBD-by-ops>
```

注: `Production` 地址当前为占位，需由运维/网关发布后回填。

### 8.2 通用请求头

```typescript
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${token}`,
  'X-Request-ID': generateRequestId(),
};
```

注: `Authorization` 头为预留写法，实际鉴权方式（是否 Bearer/JWT/API Key）待网关策略冻结后确认。

### 8.3 响应信封格式

**成功响应**:
```typescript
interface SuccessEnvelope<T> {
  ok: true;
  data: T;
  gate_decision: 'ALLOW' | 'BLOCK';
  release_allowed: boolean;
  evidence_ref: string;
  run_id: string;
}
```

**错误响应**:
```typescript
interface ErrorEnvelope {
  ok: false;
  error_code: string;
  blocked_by: string;
  message: string;
  evidence_ref?: string;
  run_id: string;
  forbidden_field_evidence?: object;
  required_changes?: string[];
}
```

---

## 9. 参考文档

- [L4.5 启动清单 v2](./L4.5%20启动清单%20v2（2026-02-20）.md)
- [N8N 边界合约](./L45_N8N_BOUNDARY_CONTRACT_v1.md)
- [外部技能治理合约](../2026-02-19/contracts/external_skill_governance_contract_v1.yaml)
- [API 端点定义](../../skillforge/src/contracts/api/l4_endpoints.yaml)

---

## 变更历史

| 版本 | 日期 | 变更描述 |
|------|------|---------|
| v1.0 | 2026-02-20 | 初始版本，整理后端功能与前端需求 |
| v1.1 | 2026-02-20 | 审计修订：修正禁止字段、错误码、fetch_pack 参数约束、Permit 状态口径、引用路径 |
| v1.2 | 2026-02-20 | 口径修订：补充后端状态列、拆分已实现/规划统计、标记生产地址与鉴权为占位 |
| v1.3 | 2026-02-20 | 新增 UI 设计规范（视觉风格/产品格调/设计规则/展示方式）和基线方案评审模板 |
| v1.4 | 2026-02-20 | 从 NEW-GM 迁移五段式编排与三张卡片意图，新增当前后端兼容映射 |
| v1.5 | 2026-02-20 | 采纳方案1评审：冻结为 7 页 4 组架构，固化必改项/风格规则/IA 风险与评分 |
| v1.6 | 2026-02-20 | 版本号更新（按最新评审轮次继续收敛） |
| v1.7 | 2026-02-20 | 综合方案冻结：v1.0 采用方案2（5页对齐后端），v1.1 吸收方案1（release 治理增强） |
