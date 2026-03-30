# GM LITE Dispatch Assist Minimal Implementation v1 Boundary Rules

## 1. 唯一边界

`dispatch assist` 在本轮只负责：

- 计算 `next_hop`
- 识别 `missing_pieces`
- 生成 `backfill_prompt`
- 生成 `dispatch_packet`

它不负责：

- 真正把消息送进其他插件
- 自动接单确认
- timeout / retry
- 运行时调度

## 2. 唯一事实源

- `BusManager`
- `.gm_bus`
- 权威 verification 路径：`D:\gm-lite`

## 3. assist 输出纪律

assist 输出必须尽量结构化：

- `next_hop_decision`
- `missing_piece_list`
- `backfill_instruction`
- `dispatch_packet`

禁止输出：

- 大段复述任务卡
- 重新解释全模块战略
- 与当前任务无关的长篇分析

## 4. 不得越权

- 不得直接写 execution/review/compliance 结论
- 不得直接修改三件套
- 不得直接宣告 `GATE_READY`，除非依据完整状态
- 不得越过 tri-split 流转顺序

## 5. 权威路径纪律

- `D:\gm-lite` = 权威项目树
- `D:\GM-SkillForge\gm-lite` = 主控文档镜像树

凡 verification / `.gm_bus` / sample payload / assist runtime artifacts：

- 一律以 `D:\gm-lite` 为准

## 6. 本轮成功标准

只有在以下条件同时满足时，本轮 minimal implementation 才算成立：

- next hop assist 可用
- missing piece / backfill assist 可用
- dispatch packet build assist 可用
- 与 `BusManager` 有最小对接
- 无越界进入 auto-send / runtime / direct-connect
