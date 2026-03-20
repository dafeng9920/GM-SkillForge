# GM LITE Writeback Permission Model v1

## 一句话定义

`GM-LITE` 若要从“协议化流转”走向“低摩擦落地”，必须建立：

> 标准写回权限模型

也就是：

- 哪些写回路径属于受信任写回区
- 哪些角色可以写哪些标准文件
- 哪些写回可以减少人工逐次确认
- 哪些写回仍必须保留人工确认

---

## 当前暴露的问题

当前 AI 军团已经知道：

- 写回路径
- 下一跳
- `execution / review / compliance` 的职责

但在真正落盘时，插件仍会弹出：

- “Do you want to create `*_compliance_attestation.md`?”

这说明现在系统只解决了：

- **写回协议**

但还没有解决：

- **写回权限**

---

## 为什么它是成立前提

如果没有写回权限模型：

1. 每次标准写回都要人工点确认
2. 多 Agent 流转会被高频确认弹窗打断
3. 系统无法形成稳定的低摩擦接力
4. 用户仍然是最后一道手工 I/O 总线

因此它不是优化项，而是：

> `GM-LITE` 成立的关键前置条件之一

---

## 最小目标

Light 版当前至少要做到：

1. 定义标准 writeback 白名单路径
2. 定义角色到路径的最小写权限映射
3. 区分：
   - 标准 verification 写回
   - 非标准任意编辑
4. 明确哪些动作可以进入“会话级受信任写回”

---

## 白名单写回区

当前建议首先白名单化的路径：

- `gm-lite/docs/**/verification/**/*.md`
- `.gm_bus/writeback/**`
- `.gm_bus/escalation/**`
- `.gm_bus/archive/**`

这些路径的特点：

- 是标准协议产物
- 文件名可预测
- 角色职责可映射
- 不属于任意业务源码编辑

---

## 角色写回映射

### Execution

默认只允许写：

- `*_execution_report.md`

### Review

默认只允许写：

- `*_review_report.md`

### Compliance

默认只允许写：

- `*_compliance_attestation.md`

### 主控官

默认允许写：

- task board
- module report
- change control
- final gate / frozen report

---

## Light 版推荐权限模型

### 模型 A：会话级白名单放行

用户在当前 session 对标准 writeback 白名单路径执行：

- `allow all edits during this session`

效果：

- 同类 verification 写回不再逐次确认

优点：

- 最易落地

缺点：

- 仍然依赖人工开启

### 模型 B：路径级受信任写回

插件识别：

- 当前动作属于标准 writeback
- 当前角色与文件路径匹配

则自动视为受信任写回，不弹逐次确认。

优点：

- 更接近真正低摩擦流转

缺点：

- 需要插件侧实现

---

## 当前 Light 版不做什么

当前不做：

- 细粒度 ACL 系统
- 多用户身份系统
- 永久权限托管
- 云端统一权限中心

这些属于后续 Core 版问题。

---

## 与其他前置问题的关系

该模型与以下问题并列，都是 `GM-LITE` 的关键前提：

- `chat-output-to-bus bridge`
- shared task bus
- controller console

关系是：

- shared task bus 负责承载任务现实
- chat-output-to-bus bridge 负责把输出送入总线
- writeback permission model 负责让标准写回真正顺畅落地

---

## 当前结论

从当前阶段开始：

> 标准写回已协议化，
> 但写回权限还未系统化。

因此：

- 该问题必须单独立案
- 后续 Light 版设计必须显式吸收
- 否则用户仍会被频繁人工确认打断
