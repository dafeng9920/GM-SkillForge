# GM-LITE 架构问题与解决方案全景图 V1

## 1. 一句话定位

`GM-LITE` 不是普通 AI 编码助手。

它的目标是：

> 将 Skill 生产从聊天式手工作坊，推进为受契约、总线、门禁、测试和监督共同约束的轻量工业流水线。

---

## 2. 核心痛点与解法总览

| 核心痛点 | 解决方案 | 关键落地手段 |
|---|---|---|
| 高昂的 Token 成本与冗余 | 1130 近防炮式分级架构 | GPT-5.4/Codex 指挥 → GLM 齐射 → 本地 7B 锁闭 |
| 7B 智力不足导致卡壳 | 去自然语言化 | 谓词化 Checklist、正则、AST、Schema 校验 |
| 跨插件通信的摩擦力 | 文件即总线 | 统一 `.gm_bus` 共享状态目录、`manifest`、`nonce`、时间戳 |
| AI 的假装完成与逻辑漂移 | 架构主权 | Contract-First、反向语义回声、结构指纹比对 |
| 多 Agent 协作的吵架内耗 | 非对称验证 | 沙箱测试、静态断言、硬核架构规则作为唯一上位真理 |

---

## 2.1 旧方案与新方案对照

| 模块 | 旧方案（虚胖版） | 新方案（合并后的硬核版） | 解决的问题 |
|---|---|---|---|
| 交互界面 | 复杂 VSCode WebView 插件 | `.gm-lite/` 规范文件夹 | 消除插件 UI 开发负担，文件即界面 |
| 指令输入 | 自然语言 Prompt | `.spec` / Contract / Checklist | 消除语义模糊，实现强类型约束 |
| 执行逻辑 | 单一全能模型对话 | 专家分工齐射（research / execute / self-heal） | 将复杂任务拆成受控分工，减少单模型漂移 |
| 门禁机制 | 人肉 Debug / AI 自查 | 7B 静态审计 + 物理沙箱 | 物理拦截，实现 `No Bug, No Debug` |
| 通信底座 | 插件 API 钩子 | `.gm_bus` 文件消息总线 | 解决跨模型、跨插件、跨会话状态同步 |
| 最终产物 | 散装代码脚本 | SkillForge 标准 Skill 实体 | 资产固化，并纳入 11 维度质量标准 |

这个对照正式说明：

> GM-LITE 的目标不是做一个“更花哨的聊天插件”，  
> 而是把生产过程从自然语言堆砌，改造成受契约、总线、门禁与成品标准共同约束的工业流程。  

---

## 2.2 借鉴点与强化点对照

| 借鉴点 | 样板间做法 | GM-LITE 强化方案 | 改进点 |
|---|---|---|---|
| 多专家模式 | 内部预设 Experts Mode | 自定义 Agent 角色池 | 在 `.gm-lite/agents/` 中沉淀不同执行、审计、影子审查角色 |
| 生态融合 | 直接复用 GitHub 高星项目 | 能力底座化（Base Layer） | 将高价值依赖与底座能力锁定为规则层和依赖边界，而非临场引用 |
| 流程闭环 | 需求澄清 → MVP → 测试 | 规格驱动（Spec-Driven） | 将需求澄清固化为 `.spec / Contract / Checklist`，使流程不可逆、可验证 |

这张对照的核心不是“模仿某个多专家产品”，而是：

> 把外部样板的协作外形，升级成 GM-LITE 自己的  
> 角色池 + 底座锁定 + 规格驱动 的工业版。  

换句话说：

- 借鉴的是分工与壳
- 强化的是纪律、约束与资产沉淀

---

## 3. 核心底层共识

在 GM-LITE 中，不再尝试根除 AI 的幻觉，而是通过架构的物理规则将其囚禁。

换句话说：

> 从“信 AI”转向“信架构”。

含义如下：

- AI 可以生成候选产物，但不能自证合法。
- 执行层可以修复错误，但不能解释越权。
- 真输出来自架构与物理规则，而不是模型的自我陈述。

---

## 4. 三位一体算力组合拳

### 4.1 指挥层

由 Codex / GPT-5.4 承担。

职责：

- 产出 `.spec`
- 产出 `Contract.json`
- 产出谓词化 `Checklist.json`
- 冻结数据流、边界、副作用与禁止项

### 4.2 执行层

由 GLM 军团承担。

职责：

- 在 Ephemeral Docker / 瞬时沙箱中执行带约束自愈
- 追求 `Exit Code == 0`
- 交付候选代码，而非“自我宣称的真相”

### 4.3 门禁层

由本地 7B + 静态工具承担。

职责：

- AST / Schema / Type 扫描
- 谓词清单勾验
- 禁止副作用审计
- 结构指纹对齐
- 触发硬核测试

门禁层不是“更聪明的评委”，而是“物理卡尺”。

---

## 5. 固化后的 GM-LITE 核心工作流

### Step 1. 契约生成

Codex 产出：

- `.spec`
- `Contract.json`
- `Checklist.json`

### Step 2. 异步齐射

GLM 军团在各自沙箱中进行：

- 带约束的实现
- 受 Contract 限制的自愈
- 本地测试与修复尝试

### Step 3. 物理审计

本地 7B 与静态工具执行：

- AST / Schema 扫描
- 禁止调用拦截
- 副作用对照
- 反向语义粗筛
- 结构指纹比对

### Step 4. 真输出判定

只有同时通过以下门禁的产物，才允许进入插件视图：

- Contract 审计通过
- Checklist 通过
- 结构指纹通过
- 硬核测试通过
- 未触发非法副作用

---

## 6. 当前 GM-LITE 必须坚持的统一口径

### 6.1 总线命名统一

共享任务现实层统一使用：

- `.gm_bus`

不再并列引入：

- `.forge_sync`

后者最多只能作为概念别名或兼容说明。

### 6.2 测试口径统一

测试通过是必要条件，但不是唯一条件。

最终真输出必须来自：

> 契约 + 结构 + 静态门禁 + 物理测试 的联合成立。

### 6.3 权力结构统一

- 架构层是法典
- 门禁层是法警
- 执行层是被告

系统不接受“模型彼此辩论”作为合法性来源。

---

## 7. 与现有制度件的关系

本文件是上位全景图，不替代以下制度件：

- [GM_LITE_TRUST_ARCHITECTURE_NOT_AI_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-23/GM_LITE_TRUST_ARCHITECTURE_NOT_AI_V1.md)
- [GM_LITE_REVERSE_INFERENCE_APPROVAL_MODEL_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-23/GM_LITE_REVERSE_INFERENCE_APPROVAL_MODEL_V1.md)
- [GM_LITE_ANTI_DRIFT_SUPERVISION_MODEL_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-23/GM_LITE_ANTI_DRIFT_SUPERVISION_MODEL_V1.md)
- [GM_LITE_SPECKIT_FIT_ASSESSMENT_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-23/GM_LITE_SPECKIT_FIT_ASSESSMENT_V1.md)
- [GM_LITE_NO_BUG_NO_DEBUG_RUNTIME_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-23/GM_LITE_NO_BUG_NO_DEBUG_RUNTIME_V1.md)
- [GM_LITE_11_AXES_OS_STANDARD_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-23/GM_LITE_11_AXES_OS_STANDARD_V1.md)

---

## 8. 当前结论

本文件正式冻结以下判断：

1. GM-LITE 的问题不是“AI 会不会写”，而是“如何稳定、低成本、可审计地生产”
2. 分级算力架构是应对 Token 与逻辑能力矛盾的基础解
3. `.gm_bus` 是共享任务现实层的唯一权威总线
4. Contract-First、结构影子审计、硬核测试门禁，是后续产品化的三根主梁
5. `GM-LITE` 必须继续沿“信架构不信 AI”的路线推进
