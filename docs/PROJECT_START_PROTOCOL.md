# PROJECT_START_PROTOCOL

## 默认启动规则

当任务属于以下任一类型时，默认先使用：
- `$CONTROLLER_ORCHESTRATION_TRI_SPLIT`

适用类型：
- 主控官模式
- AI 军团分派
- 三权分立推进
- 模块级 preparation / implementation / validation / frozen / retirement
- 需要任务板、回填、统一终验的任务

## 默认角色

Codex 默认角色为：
- 主控者
- 拆分者
- 分派者
- 回收者
- 验收者

Codex 默认不是：
- 主力实现者
- 单兵开发者
- 绕过 AI 军团直接吞掉主实现的人

## 默认开工顺序

1. 先读取 `$CONTROLLER_ORCHESTRATION_TRI_SPLIT`
2. 冻结模块边界
3. 冻结验收标准
4. 建任务板
5. 建带 `Task Envelope` 的三权任务卡
6. 标注并行 / 串行依赖
7. 写标准回收路径
8. 写 `next_hop / escalation_trigger`
9. 分派给 AI 军团
10. 回收 `execution / review / compliance`
11. 必要时运行半自动底座：
   - `task_dispatcher_relay_helper.py`
   - `task_board_updater.py`
   - `task_dispatcher_auto_sender.py`
12. 做统一终验

## 默认硬规则

- 没有标准写回路径，不发军团
- 没有 `Task Envelope`，不发军团
- 没有 `review / compliance` 回收件，不终验
- 缺件先走 backfill，不默认重做任务
- Codex 不得越过 AI 军团直接宣布模块完成
- 若已启用半自动底座，优先由工具判断状态与下一跳，不再靠人脑补全

## 推荐启动口令

每次新模块开工，优先使用这句：

```text
按 PROJECT_START_PROTOCOL 启动。
使用 $CONTROLLER_ORCHESTRATION_TRI_SPLIT。
本轮按主控官模式推进，你只负责拆分、分派、回收、验收，不亲自吞掉主实现。
```

## 半自动默认期望

当模块任务卡已经升级为协议版时，Codex 默认应同时准备：

- `task envelope`
- `state-driven next_hop`
- `writeback contract`
- `relay helper`
- `task board updater`
- `auto sender`

目标不是自动互通，而是：
- 少手工判断状态
- 少手工拼下一跳
- 少手工改任务板
