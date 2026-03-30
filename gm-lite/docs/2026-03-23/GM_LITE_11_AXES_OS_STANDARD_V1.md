# GM LITE 11 Axes OS Standard v1

## 一句话定义

这 11 个维度是 `GM-LITE` 的 OS 级质量标准。

它们不是理念装饰，而是：

- 判断一个 Skill / 模块 / 协议是否达标的硬尺
- 后续自动化脚本、validator、gate、report 的上位依据

---

## 11 个维度

### 1. 语义解析 `Semantic Parsing`
- 衡量对象：意图识别、任务拆解、协议转译的精准度
- 目标：输入意图不漂移，任务定义不走形

### 2. 上下文管理 `Context Management`
- 衡量对象：上下文装载、清洗、压缩、回填策略
- 目标：减少无效背景吞入，避免 token 膨胀与截断

### 3. 可靠性 `Reliability`
- 衡量对象：异常处理、缺件识别、回填追认、稳定流转
- 目标：流程不因小缺口失控，问题可定位、可补回

### 4. 性能 `Performance`
- 衡量对象：响应时延、token 消耗、搜索半径、回收成本
- 目标：系统可持续运行，不被上下文和扫描成本拖死

### 5. 安全性 `Security`
- 衡量对象：路径权限、受信任写回、注入与越权防护
- 目标：系统知道谁能写什么，哪些路径是白名单写回区

### 6. 合规性 `Compliance`
- 衡量对象：业务规则、治理规则、B Guard、Fail-Closed
- 目标：不让执行流转突破治理底线

### 7. 可维护性 `Maintainability`
- 衡量对象：命名、模块边界、change control、文档一致性
- 目标：结构长期可演进，不靠临场记忆维持

### 8. 可测试性 `Testability`
- 衡量对象：样板链路、验证回合、边界用例、回放验证
- 目标：不是“看起来能跑”，而是“可验证地能跑”

### 9. 互操作性 `Interoperability`
- 衡量对象：跨插件、跨 agent、跨会话共享任务现实
- 目标：不同插件围绕同一个任务现实工作

### 10. 确定性 `Certainty`
- 衡量对象：同一输入下的稳定输出、协议一致性、固定写回
- 目标：系统不靠运气，不靠口头状态

### 11. 自我进化 `Self-evolution`
- 衡量对象：基于错误日志、缺件、阻断点进行自愈与优化
- 目标：每次踩坑都沉淀成系统能力，而不是只靠记忆

---

## 当前已落地映射

### 已经开始落地的维度

#### 上下文管理
- [GM_LITE_TOKEN_CONTEXT_GUARDRAILS_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-20/GM_LITE_TOKEN_CONTEXT_GUARDRAILS_V1.md)

#### 互操作性
- [GM_LITE_CHAT_OUTPUT_TO_BUS_BRIDGE_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-20/GM_LITE_CHAT_OUTPUT_TO_BUS_BRIDGE_V1.md)

#### 安全性
- [GM_LITE_WRITEBACK_PERMISSION_MODEL_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-20/GM_LITE_WRITEBACK_PERMISSION_MODEL_V1.md)

#### 可靠性 / 合规性 / 确定性
- tri-split SOP
- `.gm_bus` shared task bus
- standard writeback
- frozen judgment

#### 语义解析 / 确定性 / 自我进化
- [GM_LITE_REVERSE_INFERENCE_APPROVAL_MODEL_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-23/GM_LITE_REVERSE_INFERENCE_APPROVAL_MODEL_V1.md)

#### 可靠性 / 安全性 / 可测试性
- [GM_LITE_ANTI_DRIFT_SUPERVISION_MODEL_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-23/GM_LITE_ANTI_DRIFT_SUPERVISION_MODEL_V1.md)

#### 语义解析 / 互操作性 / 确定性
- [GM_LITE_SPECKIT_FIT_ASSESSMENT_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-23/GM_LITE_SPECKIT_FIT_ASSESSMENT_V1.md)

#### 可靠性 / 性能 / 可测试性
- [GM_LITE_NO_BUG_NO_DEBUG_RUNTIME_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-23/GM_LITE_NO_BUG_NO_DEBUG_RUNTIME_V1.md)

---

## 落地原则

这 11 个维度的落地方式不是：

- 人工 checklist

而应该是：

- 协议对象
- 系统文档
- 自动 validator
- gate 规则
- report 模板
- 样板验证链

---

## 使用方式

后续每个 `GM-LITE` 模块都应该回答：

1. 本模块主要增强哪几个维度？
2. 本模块是否损伤其他维度？
3. 本模块的维度增强是：
   - 理念层
   - 协议层
   - 实现层
   - 自动化层

---

## 当前结论

从现在开始：

> 11 个维度不再只是设计哲学，
> 而是 `GM-LITE` 的 OS 级质量标准。

后续所有主线：

- shared task bus
- controller console
- dispatch assist
- chat-output bridge
- writeback permission

都应以本标准作为上位衡量尺。
