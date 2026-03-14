# T-ASM Review + Compliance 分发单

- 日期：`2026-03-10`
- 阶段：`Review + Compliance`
- 任务范围：
  - `T-ASM-01`
  - `T-ASM-02`
  - `T-ASM-03`

## 一、当前状态

三项任务均已提交 Execution 结果：

- `T-ASM-01`：统一后半段入口
- `T-ASM-02`：最小运行接口
- `T-ASM-03`：最小统一验证入口

当前缺失：

- 独立 `Review`
- 独立 `Compliance`

因此本轮目标不是继续执行，  
而是完成三权分立中的后两权裁决。

## 二、给 Review Agent 的指令

```text
你是本轮 T-ASM 任务的 Review Agent。

任务范围：
- T-ASM-01
- T-ASM-02
- T-ASM-03

你只做审查，不做执行，不做放行。

审查输入：
- T-ASM-01 Execution Report
- T-ASM-02 Execution Report
- T-ASM-03 Execution Report
- multi-ai-collaboration.md
- docs/2026-03-10/本地主线盘点_缺口_优先级_2026-03-10.md

审查重点：
1. 是否越权改动
2. 是否把“主线组装”扩成“大重构”
3. 是否破坏现有 Permit / pre_absorb_check / absorb
4. 是否缺少关键证据
5. 是否与当前主链目标脱节
6. T-ASM-01 / 02 / 03 三者之间是否存在接口冲突或定义不一致

你必须对每个任务分别输出：
- task_id
- decision: ALLOW / REQUIRES_CHANGES / DENY
- reasons
- evidence_refs
- required_changes

不要补代码，不要代替执行者修复。
```

## 三、给 Compliance Agent 的指令

```text
你是本轮 T-ASM 任务的 Compliance Agent。

任务范围：
- T-ASM-01
- T-ASM-02
- T-ASM-03

你按 fail-closed 做硬校验。

审查输入：
- T-ASM-01 Execution Report
- T-ASM-02 Execution Report
- T-ASM-03 Execution Report
- multi-ai-collaboration.md
- docs/2026-03-10/本地主线盘点_缺口_优先级_2026-03-10.md

硬规则：
1. 不得绕过三权分立
2. 不得削弱 Permit / EvidenceRef / Compliance 口径
3. 不得把文档口径冒充真实执行能力
4. 不得越权改动
5. 不得把局部统一冒充“系统最终完成”
6. 不得因统一入口而降低 fail-closed

你必须对每个任务分别输出：
- task_id
- decision: PASS / FAIL
- violations
- evidence_refs
- required_changes

一票否决条件：
- 绕开 Permit
- 弱化门禁
- 无证据宣称完成
- 越权改动
```

## 四、给总装汇总者的指令

```text
你现在是任务总装汇报者，请只汇总以下内容，不新增设计：
- T-ASM-01 Review 结论
- T-ASM-01 Compliance 结论
- T-ASM-02 Review 结论
- T-ASM-02 Compliance 结论
- T-ASM-03 Review 结论
- T-ASM-03 Compliance 结论

输出格式：
1. 哪些任务通过 Review
2. 哪些任务通过 Compliance
3. 哪些任务可进入总装
4. 哪些任务必须返工
5. 当前主链是否已经具备：
   - 统一后半段入口
   - 最小运行接口
   - 最小统一验证入口
6. Final Gate 建议：
   - ALLOW / REQUIRES_CHANGES / DENY
```

## 五、一句话

这一步不再新增执行任务，  
只做 `Review + Compliance`，把三项执行结果推进到可总装或可返工的正式裁决状态。
