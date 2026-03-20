# GM LITE Token Context Guardrails v1

## 一句话定义

`GM-LITE` 若要支撑多 Agent 持续推进，必须把：

- token 截断
- 上下文过载
- 跨库误扫
- 报告复述膨胀

作为系统级风险提前防住，而不是事后靠人工节流。

---

## 当前风险

随着 `GM-LITE` 模块增多，最容易出现的 token 泄洪点包括：

1. 子任务吞入过多全局文档
2. execution / review / compliance 相互复述
3. 主控官重复读取整套历史文件
4. Agent 自发全仓 / 跨库扫描
5. 已有结果不回填，反而整轮重跑

---

## Guardrail 1：最小事实源

每个子任务默认只允许读取：

- 当前任务卡
- 最多 1 到 2 份最相关边界文档
- 必要时的局部 `*_CONTEXT_SNAPSHOT.md`

禁止：

- 为了“保险”吞入整套模块文档
- execution / review / compliance 都各自重读全部背景

规则：

- 默认最小化输入
- 需要扩上下文时，由主控官显式放行

---

## Guardrail 2：原子化写回

所有标准写回件只允许写：

- 核心结论
- 增量改动
- 必要 EvidenceRef
- PASS / REQUIRES_CHANGES / FAIL

禁止：

- 复述任务卡全文
- 复述上一轮 report 大段内容
- 把任务书抄回 verification

规则：

- 写回短、准、可验
- verification 是结果件，不是第二份任务书

---

## Guardrail 3：搜索范围节流

默认只允许在当前项目、当前模块、当前任务相关目录内搜索。

禁止：

- 无理由跨 `D:/NEW-GM`
- 无理由跨 `GM-SkillForge`
- 无理由全盘递归扫描

规则：

- 跨模块 / 跨库搜索必须写明目的
- 主控官未放行，不扩大搜索半径

---

## Guardrail 4：主控官回收最小化

主控官回收时默认优先读取：

- task board
- report
- verification 文件名清单

只有以下情况才深入读报告正文：

- 存在 `FAIL`
- 存在 `REQUIRES_CHANGES`
- 存在路径冲突
- 存在权威状态不一致

规则：

- 不把主控回收做成全文复读
- 主控阅读应以证据定位为主，不以全文重吞为主

---

## Guardrail 5：回填优先，不重跑优先

如果任务实际已完成，但标准路径缺件：

- 优先做 `回填追认`
- 不默认重跑整轮任务

规则：

- 缺件先补落盘
- 非必要不重新喂入全部上下文

---

## Guardrail 6：单任务上下文预算

单任务默认不应依赖超过：

- 1 张任务卡
- 2 份边界文档
- 1 份局部 snapshot

若超出，必须由主控官说明：

- 为什么当前任务不能再被压缩

---

## 适用范围

本 guardrail 适用于：

- tri-split 任务卡
- preparation / implementation / validation / frozen judgment
- verification 回收
- backfill
- shared task bus
- controller console
- dispatch assist

---

## 当前结论

从 `GM-LITE` 当前阶段开始：

> token / context control 不是优化项，
> 而是系统级执行纪律。

后续所有模块默认继承本 guardrail。
