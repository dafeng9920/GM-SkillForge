# GM-LITE 自动化军工厂宣言 V1

## 1. 一句话定义

GM-LITE 的目标，不是做一个更会聊天的 AI 编码工具。

GM-LITE 的目标是：

> 把 Skill 生产从“样板间”推进为“自动化军工厂”。  

---

## 2. 核心哲学

### 2.1 不信 AI，信架构

GM-LITE 不再追求 AI 的“聪明”，而是追求架构的“死板”。

在这套体系里：

- AI 是执行工
- Spec / Contract 是法律
- Gate / Test / Static Audit 是法警

AI 没有自证合法的权力。

### 2.2 No Bug, No Debug

GM-LITE 的目标不是“更快 Debug”，而是：

> 尽量不让带毒代码进入视线。  

也就是说：

- 坏代码先被架构与物理门禁筛掉
- 只有幸存产物才有资格进入正式视图和正式目录

---

## 3. 物理外壳：`.gm-lite/` 基础设施规范

GM-LITE Light 当前不优先开发复杂插件 UI，而是先借助目录规范完成工业化落地。

### 推荐结构

```text
.gm-lite/
  constitution/
  rules/
  specs/
  agents/
  skills/
  commands/
  templates/

.gm_bus/
  manifest.json
  outbox/
  inbox/
  writeback/
  escalation/
  archive/
```

### 目录职责

| 目录/文件 | 角色 | 核心功能 |
|---|---|---|
| `constitution/` | 宪法 | 锁定 11 核心维度、总边界、系统级禁令 |
| `.gm-lite/rules/` | 律法/毒素库 | 存放 AST、Schema、Checklist、静态拦截规则 |
| `.gm-lite/specs/` | 规格入口 | 存放 Codex 产出的 `.spec / Contract / Checklist` |
| `.gm-lite/agents/` | 专家军团 | 定义调研、编码、试毒、审计等分工配置 |
| `.gm-lite/skills/` | 成品金库 | 只存放通过所有门禁的标准 Skill 实体 |
| `.gm-lite/commands/` | 运行时触发层 | watchman / CLI / automation 命令入口 |
| `.gm_bus/` | 共享任务现实层 | dispatch / receipt / writeback / escalation 权威状态源 |

---

## 4. 三位一体生产流水线

### 4.1 契约化拆解

Codex 将用户意图降级为强类型规格对象：

- `.spec`
- `Contract.json`
- `Checklist.json`

它不再说“写一个均线函数”，而必须冻结：

- Input
- Output
- Constraint
- Allowed Side Effects
- Forbidden Side Effects

### 4.2 分布式齐射

GLM 军团在后台受控沙箱中执行：

- 试错
- 对撞
- 自愈

但这种自愈不是自由发挥，而是：

> 在 Contract 围栏内带着镣铐跳舞。  

### 4.3 多重审计门禁

GM-LITE 的近防炮由三类拦截器构成：

1. 本地 7B / 静态工具  
   - AST 扫描  
   - Schema 校验  
   - Type Hint 检查  
   - 逻辑指纹对齐  

2. Contract / Spec Gate  
   - 输入输出断言  
   - 副作用断言  
   - 禁止项熔断  

3. 物理沙箱 / 测试门  
   - Smoke Test  
   - Hard Test Suite  
   - Exit Code  
   - 覆盖率与副作用监控  

只有全部通过的候选产物，才允许进入：

- `.gm-lite/skills/`
- 插件正式视图
- 资产固化流程

### 4.4 生产闭环总览

GM-LITE 的最小生产闭环可以压缩成四段：

#### 输入端

- 用户意图
- `.spec / Contract / Checklist`
- `Task Envelope`

其中：

- `.gm-lite/specs/` 负责承载契约与规格
- `.gm_bus/` 负责承载任务信封与流转现实

#### 执行端

- GLM 齐射
- 临时沙箱运行
- 捕获报错
- 受约束自愈

#### 审计端

- 反向语义校验
- 边界压力测试
- 复杂度 / 结构 / 副作用扫描

#### 输出端

- 通过全部门禁
- 自动归档到 `.gm-lite/skills/`
- 更新 `Skill_Index.json`

这意味着：

> GM-LITE 最终不是把代码“吐”给你，  
> 而是把通过整条工业闭环的 Skill 资产“交付”给你。  

---

## 5. 为什么这是一条“工业化”路线

传统开发的基本模式是：

- 写
- 报错
- 改
- Debug

GM-LITE 试图把它改造成：

- 定义
- 约束
- 生成
- 拦截
- 固化

传统开发是：

> 人在屎山里修代码。  

GM-LITE 的理想是：

> 人只看通过近防炮后的纯净产物。  

---

## 6. 为什么你这条路是“正统”

### 对比 Claude Code

- Claude Code 更像陪跑工具
- GM-LITE 要做的是让你最后只负责收割

### 对比 OpenClaw

- OpenClaw 更像机械臂
- GM-LITE 要做的是带质检与法典的生产线

### 对比 Qoder

- Qoder 更像精装修的多专家工作台
- GM-LITE 更像炼钢厂

它牺牲的是：

- 初期上手速度
- 即时爽感

换来的是：

- 更高确定性
- 更低人肉 Debug 成本
- 更强资产可复制性
- 更清楚的工业边界

---

## 7. 当前阶段的现实版本

GM-LITE 现在还不是完全体。

但它已经有了工业化路线的骨架：

- `.gm_bus` 共享任务现实层
- tri-split 主控 SOP
- controller console 主线
- writeback / bridge / token guardrails
- trust architecture 系列制度件

因此当前最准确的判断不是：

- “它是不是已经完成”

而是：

> 它已经从聊天式方法论，进入了工业化系统雏形阶段。  

---

## 8. 当前结论

本宣言正式冻结以下判断：

1. GM-LITE 的本质不是插件，而是轻量自动化军工厂
2. `No Bug, No Debug` 是前移拦截哲学，不是空喊零缺陷
3. `.gm-lite/` 是工业外壳，`.gm_bus` 是运行时内核
4. 产物必须先过法典、门禁、结构和物理测试，才有资格进入视线
5. GM-LITE 的长期目标是生产可审计、可复制、可进化的工业级 Skill 资产
