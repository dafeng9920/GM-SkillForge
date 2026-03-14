# n8n 缺失部分分析与五段式—三张卡片设计

**日期**: 2026-03-04
**来源**: NEW-GM 源码分析 + SkillForge 现状对比
**目的**: 明确 n8n 集成缺失部分，记录五段式编排与三张卡片的设计理念

---

## 一、n8n 缺失部分分析

### 1.1 当前状态

| 组件 | 状态 | 说明 |
|------|------|------|
| **n8n workflow 执行** | ✅ 已有 | L4 API: run_intent, fetch_pack, query_rag |
| **五段式数据映射** | ❌ 缺失 | n8n 结果 → 五段式结构 |
| **三张卡片生成** | ❌ 缺失 | 五段式 → 三张卡片转化 |
| **前端展示集成** | ⚠️ 部分完成 | 前端组件已实现，但数据源缺失 |

### 1.2 断点位置

```
┌─────────────────────────────────────────────────────────────┐
│                        当前断点                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   n8n workflow (复杂连线)                                    │
│      │                                                       │
│      ▼                                                       │
│   L4 API (run_intent, fetch_pack, query_rag)               │
│      │                                                       │
│      ▼                                                       │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━               │
│      │  ⚠️  断点：映射层缺失                                 │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━               │
│      │                                                       │
│      ▼                                                       │
│   五段式编排 ← 【缺失技能1】                                │
│      │                                                       │
│      ▼                                                       │
│   三张卡片   ← 【缺失技能2】                                │
│      │                                                       │
│      ▼                                                       │
│   前端 UI 渲染                                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 缺失技能清单

| 技能名称 | 功能 | 优先级 |
|---------|------|--------|
| `five-stage-orchestrator-skill` | L4 API → 五段式数据映射 | P1 |
| `three-cards-orchestrator-skill` | 五段式 → 三张卡片转化 | P1 |

---

## 二、五段式编排设计理念

### 2.1 核心概念

**五段式编排**是 n8n workflow 的结构化抽象，将复杂的执行流程分解为 5 个可理解的阶段。

### 2.2 五段式定义

| 阶段 | 英文 | 中文 | 说明 | n8n 对应 |
|------|------|------|------|----------|
| Stage 1 | `trigger` | 触发 | 任务启动的入口点 | Webhook, Schedule, Manual |
| Stage 2 | `collect` | 收集 | 数据采集与预处理 | HTTP Request, DB Query, Scraper |
| Stage 3 | `process` | 处理 | 核心业务逻辑执行 | LLM, Transform, Code |
| Stage 4 | `deliver` | 交付 | 结果输出与通知 | Email, Webhook, Feishu |
| Stage 5 | `report` | 报告 | 执行记录与反馈 | Metrics, Logs, Summary |

### 2.3 数据结构（参考 NEW-GM）

```python
@dataclass
class Stage:
    stage_id: PlanStage          # 阶段ID
    stage_name: str              # 阶段名称
    description: str             # 描述
    tasks: List[StageTask]       # 任务列表
    status: str                  # pending/in_progress/completed/skipped
    estimated_time: str          # 预估时间
    exit_criteria: List[str]     # 退出标准

@dataclass
class FiveStagePlan:
    plan_id: str                 # 计划ID
    user_goal: str               # 用户目标
    domain: str                  # 领域 (writing/etl/ops/unknown)
    stages: List[Stage]          # 五个阶段
    metadata: Dict               # 元数据
```

### 2.4 与 SkillForge 的映射关系

| 五段式阶段 | SkillForge API 端点 | 数据来源 |
|-----------|-------------------|----------|
| `trigger` | `POST /api/v1/n8n/run_intent` | 请求 + 回执 |
| `collect` | `POST /api/v1/n8n/fetch_pack` | pack/replay_pointer |
| `process` | `POST /api/v1/n8n/query_rag` | RAG 结果 |
| `deliver` | `gate_decision` | ALLOW/BLOCK/DENY |
| `report` | `run_id` + `evidence_ref` | 可追溯报告 |

---

## 三、三张卡片设计理念

### 3.1 核心价值

**"把地狱连线压扁成三张卡片"**

n8n workflow 可能有几十个节点、上百条连线，用户无法快速理解：
- 执行了什么？
- 结果是什么？
- 下一步要做什么？

三张卡片是**概括层**，将复杂信息转化为三张可读卡片。

### 3.2 三张卡片定义

| 卡片 | 英文 | 中文 | 内容 |
|------|------|------|------|
| Card 1 | `understanding` | 理解卡 | 展示：我理解了什么？已确认哪些字段？ |
| Card 2 | `plan` | 方案卡 | 展示：推荐的执行方案（快/稳/强） |
| Card 3 | `execution_contract` | 执行合同卡 | 展示：还需确认什么？或准备就绪？ |

### 3.3 数据结构（参考 NEW-GM）

```python
@dataclass
class Card:
    card_type: str              # 'understanding' | 'plan' | 'execution_contract'
    title: str                  # 卡片标题
    content: Any                # 卡片内容
    actions: List[Dict]         # 可执行操作

@dataclass
class ThreeCards:
    card1_understanding: Card   # 理解卡
    card2_plan: Card            # 方案卡
    card3_execution_contract: Card  # 执行合同卡
    metadata: Dict              # 元数据
```

### 3.4 三张卡片详细内容

#### Card 1: 理解卡 (understanding)

```
标题: "我的理解"
内容:
  - domain: 任务领域
  - task_type: 任务类型
  - original_input: 用户原始输入
  - confirmed_fields: 已确认的字段列表
  - confirmed_values: 已确认的字段值
```

**作用**: 告诉用户"我听懂了"，建立信任。

---

#### Card 2: 方案卡 (plan)

```
标题: "推荐方案"
内容:
  - fast: 快速版（最快完成，适合简单任务）
  - steady: 稳健版（平衡质量与效率）
  - power: 强力版（最高质量，需要更多时间）
操作:
  - [快速] [稳健] [强力]
```

**作用**: 给用户选择权，控制质量/效率权衡。

---

#### Card 3: 执行合同卡 (execution_contract)

```
状态 A: "还需确认" (信息不全时)
  内容: 下一个问题文本
  操作: [选项1] [选项2] [...]

状态 B: "准备就绪" (信息齐全时)
  内容: "所有信息已收集完成"
  操作: [确认执行]
```

**作用**: 明确下一步动作，消除不确定性。

---

### 3.5 三张卡片在 SkillForge 中的映射

| 三张卡片 | SkillForge 数据来源 | 前端展示策略 |
|---------|---------------------|-------------|
| `understanding` | run_intent 输入摘要 | repo/commit/at_time/intent/requester |
| `plan` | pack + rag + 决策摘要 | 回放指针、关键结果、风险提示 |
| `execution_contract` | gate_decision + permit | permit_id/validation/error_code/blocked_by/next_action |

---

## 四、五段式 → 三张卡片的转化逻辑

### 4.1 转化原则

```
五段式 (执行细节)     三张卡片 (用户视角)
     │                        │
     ├─ trigger ──────────────┼─→ understanding (我理解了)
     ├─ collect ───────────────┤
     ├─ process ───────────────┼─→ plan (推荐方案)
     ├─ deliver ───────────────┤
     └─ report ────────────────┼─→ execution_contract (执行合同)
```

### 4.2 转化示例

**输入**: 五段式执行结果

```json
{
  "trigger": {"status": "completed", "user_intent": "生成SEO报告"},
  "collect": {"status": "completed", "data_sources": ["Google Analytics", "Search Console"]},
  "process": {"status": "completed", "llm_summary": "..."},
  "deliver": {"status": "completed", "output_format": "PDF"},
  "report": {"status": "completed", "metrics": {"time": "45s", "tokens": "1200"}}
}
```

**输出**: 三张卡片

```json
{
  "card1_understanding": {
    "title": "我的理解",
    "content": {
      "task": "生成 SEO 报告",
      "sources": ["Google Analytics", "Search Console"],
      "output": "PDF 格式"
    }
  },
  "card2_plan": {
    "title": "推荐方案",
    "content": {
      "fast": "快速生成（基础指标）",
      "steady": "完整报告（含分析）",
      "power": "深度报告（含建议）"
    }
  },
  "card3_execution_contract": {
    "title": "准备就绪",
    "content": "所有信息已确认，可立即执行",
    "actions": [{"label": "确认执行", "value": "confirm"}]
  }
}
```

---

## 五、需要创建的技能

### 5.1 five-stage-orchestrator-skill

**功能**: 将 n8n workflow 执行结果映射为五段式结构

**输入**:
```yaml
input:
  n8n_execution_result: "n8n workflow 执行结果"
  api_responses:
    run_intent: "run_intent 回执"
    fetch_pack: "pack 数据"
    query_rag: "RAG 查询结果"
```

**输出**:
```yaml
output:
  five_stage_plan:
    trigger:
      status: "completed"
      summary: "..."
    collect:
      status: "completed"
      summary: "..."
    process:
      status: "completed"
      summary: "..."
    deliver:
      status: "pending"
      summary: "..."
    report:
      status: "pending"
      summary: "..."
```

---

### 5.2 three-cards-orchestrator-skill

**功能**: 将五段式数据转化为三张卡片

**输入**:
```yaml
input:
  five_stage_plan: "五段式数据"
  gate_decision: "门控决策"
  permit: "许可令牌"
```

**输出**:
```yaml
output:
  three_cards:
    card1_understanding:
      title: "我的理解"
      content: {...}
    card2_plan:
      title: "推荐方案"
      content: {...}
    card3_execution_contract:
      title: "准备就绪"
      content: {...}
```

---

## 六、设计原则总结

### 6.1 核心价值

| 层级 | 作用 | 受众 |
|------|------|------|
| **n8n workflow** | 执行细节 | 开发者 |
| **五段式编排** | 结构化抽象 | 技术用户 |
| **三张卡片** | 用户友好的概括 | 终端用户 |

### 6.2 设计约束

1. **Fail-Closed**: 转化失败时必须明确告知用户，而非隐藏错误
2. **可追溯**: 每张卡片必须能追溯到原始 n8n 执行记录
3. **可操作**: 三张卡片必须包含明确的下一步操作
4. **一致性**: 相同输入必须产生相同的卡片输出

### 6.3 实现优先级

| 优先级 | 任务 | 说明 |
|--------|------|------|
| P1 | 创建 five-stage-orchestrator-skill | 建立 n8n → 五段式映射 |
| P1 | 创建 three-cards-orchestrator-skill | 建立五段式 → 三卡片映射 |
| P2 | 前端集成 | 将三张卡片数据渲染到 UI |
| P3 | n8n workflow 优化 | 简化 n8n workflow 结构 |

---

## 七、完整 NL → SKILL → N8N 链路分析

### 7.1 填补缺失后的链路（仅输出端）

```
NL 输入
   ↓
【❌ 缺失：生成层 11 个技能】
   ↓
SKILL (Skill Spec)
   ↓
【❌ 缺失：Skill → n8n workflow 映射】
   ↓
n8n workflow 执行
   ↓
【✅ 已填补：five-stage + three-cards】
   ↓
五段式 → 三张卡片 → UI 展示
```

**结论**：填补缺失技能后，只能解决**输出展示**问题。

完整链路需要三个阶段全部实现。

---

### 7.2 完整链路的三个阶段

#### 阶段一：NL → SKILL（输入端）

需要 **11 个生成层技能**：

| 技能 | 功能 | 依赖 |
|------|------|------|
| `intent-parser-skill` | NL → DemandSpec 解析 | - |
| `source-strategy-skill` | 路径决策（NL/GitHub/Auto）| intent-parser |
| `github-discovery-skill` | GitHub 搜索匹配 | source-strategy |
| `skill-composer-skill` | 从零生成 Skill Spec | intent-parser |
| `constitution-risk-gate-skill` | 宪法风险裁决 | - |
| `draft-skill-spec-skill` | Contract → Skill Spec | constitution-gate |
| `scaffold-impl-skill` | 生成可运行骨架 | draft-spec |
| `sandbox-test-skill` | 沙箱测试 + trace | scaffold |
| `pack-publish-skill` | L3 AuditPack 组装 | sandbox-test |
| `license-gate-skill` | 依赖/模板许可检查 | github-discovery |
| `repo-scan-skill` | 仓库扫描适配度评分 | github-discovery |

**输入**：自然语言需求
**输出**：Skill Spec + 实现骨架

---

#### 阶段二：SKILL → N8N（执行端）

需要 **技能到工作流映射**：

| 技能 | 功能 | 依赖 |
|------|------|------|
| `skill-to-n8n-compiler-skill` | Skill Spec → n8n workflow JSON | skill-composer |
| `n8n-workflow-validator-skill` | 验证 workflow 有效性 | skill-to-n8n-compiler |
| `n8n-workflow-deployer-skill` | 部署 workflow 到 n8n 实例 | n8n-workflow-validator |

**输入**：Skill Spec
**输出**：可执行的 n8n workflow JSON

---

#### 阶段三：N8N → 展示（输出端）✅

| 技能 | 功能 | 状态 |
|------|------|------|
| `five-stage-orchestrator-skill` | n8n → 五段式 | 待创建 |
| `three-cards-orchestrator-skill` | 五段式 → 三张卡片 | 待创建 |

**输入**：n8n workflow 执行结果
**输出**：三张卡片（用户友好的概括）

---

### 7.3 分步实施建议

| 阶段 | 内容 | 价值 | 复杂度 |
|------|------|------|--------|
| **Phase 1** | 填补输出端（五段式+三卡片）| 用户能看到执行结果 | 🟢 低 |
| **Phase 2** | 实现输入端（NL → Skill）| 用户可以用 NL 创建技能 | 🔴 高 |
| **Phase 3** | 实现映射端（Skill → n8n）| 技能自动转换为工作流 | 🔴 高 |

**当前状态**：Phase 1 待完成
**完整愿景**：Phase 1 + Phase 2 + Phase 3

---

### 7.4 完整链路图

```
┌─────────────────────────────────────────────────────────────────┐
│                    完整 NL → SKILL → N8N 链路                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   用户输入 NL                                                     │
│      "帮我做一个定时抓取 Reddit 数据并发送邮件的工具"               │
│      ↓                                                           │
│   ┌───────────────────────────────────────────────────────┐     │
│   │  Phase 2: NL → SKILL (输入端) 【缺失】                  │     │
│   ├───────────────────────────────────────────────────────┤     │
│   │  intent-parser → source-strategy → skill-composer       │     │
│   │       ↓              ↓                ↓                  │     │
│   │  constitution-gate → draft-spec → scaffold-impl         │     │
│   │       ↓                                       ↓          │     │
│   │  sandbox-test → pack-publish                           │     │
│   └───────────────────────────────────────────────────────┘     │
│      ↓                                                           │
│   SKILL Spec + 实现骨架                                          │
│      ↓                                                           │
│   ┌───────────────────────────────────────────────────────┐     │
│   │  Phase 3: SKILL → N8N (映射端) 【缺失】                  │     │
│   ├───────────────────────────────────────────────────────┤     │
│   │  skill-to-n8n-compiler → n8n-workflow-validator        │     │
│   │       ↓                              ↓                  │     │
│   │  n8n-workflow-deployer                                  │     │
│   └───────────────────────────────────────────────────────┘     │
│      ↓                                                           │
│   n8n workflow JSON                                              │
│      ↓                                                           │
│   n8n 执行引擎                                                    │
│      ↓                                                           │
│   ┌───────────────────────────────────────────────────────┐     │
│   │  Phase 1: N8N → 展示 (输出端) 【待填补】                 │     │
│   ├───────────────────────────────────────────────────────┤     │
│   │  five-stage-orchestrator (n8n → 五段式)                │     │
│   │       ↓                                                  │     │
│   │  three-cards-orchestrator (五段式 → 三张卡片)           │     │
│   └───────────────────────────────────────────────────────┘     │
│      ↓                                                           │
│   三张卡片 UI 展示                                                 │
│      ↓                                                           │
│   用户看到："我理解了" + "推荐方案" + "执行合同"                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### 7.5 核心价值总结

| 完整链路 | 当前能力 | 完整后能力 |
|---------|---------|-----------|
| **NL → SKILL** | ❌ 手动编写 | ✅ NL 自动生成 |
| **SKILL → N8N** | ❌ 手动配置 | ✅ 自动转换部署 |
| **N8N → 展示** | ⚠️ 复杂连线 | ✅ 三张卡片概括 |

**填补输出端后的价值**：
- 用户能看到可读的执行结果
- 系统具备完整的输出概括能力
- 为完整链路奠定展示层基础

**完整链路的价值**：
- 用户可以用 NL 创建技能
- 系统自动生成、部署、执行工作流
- 端到端的 "AI 驱动的技能工厂"

---

## 八、附录

### 8.1 NEW-GM 源码参考

```
D:/NEW-GM/src/services/orchestration/five_stage_plan.py
D:/NEW-GM/src/services/orchestration/three_cards_builder.py
D:/NEW-GM/docs/五段式工作流可视化 UI 设计规范 v0.1.md
```

### 8.2 相关文档

```
docs/2026-02-20/FRONTEND_REQUIREMENTS_v1.md (Section 3.6)
docs/2026-02-26/l4-n8n-execution/
ui/app/src/types/orchestrationProjection.ts
ui/app/src/mappers/orchestrationProjectionMapper.ts
```

---

**文档结束**
