# GM-LITE SpecKit 适配评估 V1

## 1. 结论先行

SpecKit 对 GM-LITE 来说不是可有可无的点子，而是一个高度对口的候选层：

> SpecKit 最适合作为 GM-LITE 的 Contract / IR / 契约编译层。

但它不替代 `.gm_bus`。

---

## 2. GM-LITE 中的分层定位

### 2.1 `.gm_bus` 的职责

`.gm_bus` 负责：

- 共享任务现实
- dispatch / receipt / writeback / escalation
- manifest / 状态流转 / 权威路径

### 2.2 SpecKit 的职责

SpecKit 负责：

- Contract 定义
- 强类型边界
- 输入输出规格
- 生成契约测试桩
- 作为跨插件的中间表示（IR）

因此两者关系应为：

> `.gm_bus` = 流转与状态层  
> `SpecKit` = 契约与 IR 编译层

---

## 3. 为什么 SpecKit 对口

### 3.1 终结语义模糊

SpecKit 天然偏向：

- Spec-Driven
- 强类型
- 边界先行

这与 GM-LITE 的：

- Contract-First
- 不信 AI，信架构

完全同向。

### 3.2 自动化非对称校验

SpecKit 若能自动生成：

- Test Stubs
- Mock Data
- Contract Tests

则执行层不必再与审查模型辩论，而是直接过硬规则。

### 3.3 作为跨插件共同语言

当 Codex、Claude、GLM、7B 处在不同容器 / 插件 / 会话里时，SpecKit 可以承担：

- 共同 Contract
- 共同 IR
- 共同输入输出边界

这正好对冲跨插件语义损耗。

---

## 4. 需要防的坑

### 4.1 Spec 本身也会出错

如果上游模型写出了自相矛盾的 Spec：

- 类型永远无法满足
- 数据流节点互相冲突
- 副作用规则互斥

则 SpecKit 会让系统直接停机。

这不是坏事，但意味着：

> 在执行层拿到 Spec 之前，必须先做 Spec 合法性预审。

### 4.2 不要全盘替换

当前 GM-LITE 还不适合立刻把所有协议文档全面改造成 SpecKit。

更稳的方式是：

- 先作为试点层引入
- 选一个样板链跑通
- 再逐步向主线扩展

---

## 5. 推荐的引入方式

### 5.1 第一阶段：候选层试点

先在一个局部链路中试点：

- `chat-output-to-bus bridge`
- `dispatch assist`
- `sample flow validation`

### 5.2 第二阶段：Spec Preflight

在 Orchestrator / Controller 层加一层：

- `spec preflight`
- `spec legality check`

目标：

- 先验证法典本身没 bug
- 再把 Spec 交给执行层

### 5.3 第三阶段：工具链映射

逐步明确：

- 哪些 `.spec` 可以由 SpecKit 表达
- 哪些 Contract 字段能直接转成 SpecKit Definition
- 哪些 gate 能由 SpecKit 自动生成测试桩承担

---

## 6. 对 GM-LITE 的现实意义

如果引入成功，SpecKit 会成为：

- Codex 写法律的语言
- 执行层的围栏
- 跨插件共同 IR
- 非对称验证的自动规则来源

最准确的描述是：

> SpecKit 不是 GM-LITE 的总线。  
> SpecKit 是 GM-LITE 的契约编译层候选方案。  

---

## 7. 当前结论

本文件正式冻结以下判断：

1. SpecKit 与 GM-LITE 的 `Contract-First` 路线高度兼容
2. SpecKit 不替代 `.gm_bus`
3. SpecKit 最适合作为 Contract / IR / 契约编译层候选方案
4. 引入前必须先做 `spec legality check`
5. 推荐从局部样板链试点，而非立即全盘替换
