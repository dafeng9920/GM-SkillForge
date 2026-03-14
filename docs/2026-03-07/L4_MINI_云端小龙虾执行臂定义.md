# L4-mini 云端小龙虾执行臂定义（2026-03-07）

## 目的

给 `L4-mini` 明确补上一条关键能力：

**让小龙虾在云端按照已冻结要求完成编码开发与执行任务，从而抓住一切可并行时间，加快交付。**

这份文档回答的是：

- 小龙虾在云端到底负责什么
- 不负责什么
- 需要回传什么
- 如何与本地治理内核配合
- 核心治理约束：[lobster-cloud-execution-governor-skill](file:///d:/GM-SkillForge/skills/lobster-cloud-execution-governor-skill/SKILL.md)

---

## 一、角色定义

### 定位

**小龙虾 = 云端执行开发臂**

小龙虾的价值，不是代替治理内核，而是：

- 在云端吃掉编码开发和受控执行的时间成本
- 按冻结合同完成任务
- 回传可审计产物

### 不是谁

小龙虾不是：

- 最终审查者
- 最终合规裁决者
- Permit 签发者
- final gate 决策者
- 可自行扩 scope 的自治代理

---

## 二、职责范围

### 可以做的事

1. **编码开发**
   - 修改代码
   - 创建/调整脚本
   - 补测试
   - 生成配置

2. **受控执行**
   - 运行指定命令
   - 执行 smoke/test/build
   - 拉取或整理指定产物

3. **交付产物**
   - execution report
   - stdout/stderr logs
   - changed files list
   - EvidenceRef
   - completion record

4. **边界内迭代**
   - 根据 required_changes 修修复项
   - 在合同/任务书允许范围内补缺

### 不可以做的事

1. 擅自改任务目标
2. 擅自增加新范围
3. 宣称“已通过 review/compliance/final gate”
4. 绕过 permit/gate
5. 自行决定发布
6. 覆盖或修改审查/合规结论

---

## 三、L4-mini 中的标准工作方式

### 标准链路

1. 用户需求进入
2. 本地内核形成/冻结合同
3. 小龙虾在云端执行开发任务
4. 小龙虾回传 execution artifacts
5. 本地 reviewer 审查
6. 本地 compliance 裁决
7. 本地 final gate 决定是否放行

### 核心原则

**云端负责执行，本地负责裁决。**

这是 `L4-mini` 不能松的边界。

---

## 四、最小必需回传物

小龙虾每次完成 shard，至少必须回传：

1. `execution_report`
2. `completion_record`
3. `modified_files`
4. `commands_run`
5. `test_or_smoke_results`
6. `stdout/stderr` 或等价日志定位
7. `EvidenceRef`
8. `remaining_risks`

若缺上述任一关键项，则：

**不得视为完成。**

---

## 五、与审计治理的关系

### 必须保留的治理链

即使小龙虾云端执行很快，也不能绕过：

- evidence chain
- review decision
- compliance attestation
- final gate
- permit binding

### 允许优化的部分

可以压缩的是：

- 执行时间
- 代码开发时间
- 并行跑任务的时间
- 构建和验证的等待时间

不能压缩掉的是：

- 裁决链
- 证据链
- fail-closed 规则

---

## 六、L4-mini 上线前对小龙虾执行臂的最低要求

### 必须达到

1. 能接收冻结后的任务书
2. 能在云端完成受控代码修改
3. 能稳定回传 execution artifacts
4. 不在回传中冒充 review/compliance
5. 能被本地治理内核继续接管收口

### 暂时不要求

1. 自治规划全部任务
2. 自治决定发布
3. 全场景通用执行
4. 无限扩展的多 agent 协作
5. 完全无人值守发布

---

## 七、当前最现实的落地目标

当前不要追求：

**“让小龙虾在云端什么都做完。”**

而要追求：

**“让小龙虾在云端，按冻结要求，高吞吐地完成编码开发与受控执行；让本地治理内核继续掌握裁决权。”**

这才是 `L4-mini` 阶段最有价值、最能加速上线的用法。

---

## 八、一句话结论

**小龙虾云端执行臂是 `L4-mini` 的关键加速器，但必须始终是执行臂，而不是裁决臂。**

只有这样，系统才能同时做到：

- 抓住时间
- 加快开发
- 不丢治理
- 能上线后继续迭代
