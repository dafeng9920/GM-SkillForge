# GM LITE Dispatch Assist Preparation v1 Boundary Rules

## 1. 唯一边界

`dispatch assist` 在 `GM-LITE Light` 中只负责：

- 帮主控官减少手工派发
- 帮主控官识别缺件
- 帮主控官生成 next hop / dispatch packet / backfill prompt

它不负责：

- 自动把消息送进其他插件输入框
- 自动接单确认
- 自动重试
- 自动超时恢复

## 2. 唯一事实源

- `.gm_bus`：共享任务现实层
- verification 标准写回路径：回收件事实源
- controller console read model：主控视图投影层

## 3. assist 只做的三件事

1. `next_hop_assist`
2. `missing_piece_backfill_assist`
3. `dispatch_packet_build_assist`

## 4. 不得越权

- 不得直接改写 verification 事实文件
- 不得替执行 / 审查 / 合规角色做结论
- 不得越过 tri-split 流转顺序
- 不得直接宣告 `GATE_READY`，除非三件套与状态条件齐备

## 5. 输出纪律

assist 输出必须结构化且最小化：

- 只输出主控官下一步真正需要的对象
- 不复述整份任务卡
- 不吞入无关全局文档
- 必须遵守 token/context guardrails

## 6. 权威路径纪律

当前 `GM-LITE` 的权威项目树以：

- `D:\\gm-lite`

为准。

若镜像树与权威树冲突：

- 一律以 `D:\\gm-lite` 下标准路径是否真实存在为准

## 7. 本轮成功标准

只有在以下条件同时满足时，本轮 preparation 才算成立：

- dispatch assist 职责边界冻结
- assist 输入输出冻结
- assist 动作清单冻结
- exclusions / change control 冻结
