# GM Shared Task Bus Minimal Implementation v1 Acceptance

## 通过标准
1. `.gm_bus/` 最小目录骨架已落位
2. `manifest / outbox / inbox / writeback / escalation / archive` 均有最小实现载体
3. 六个协议对象至少具备最小 schema 或 example
4. `manifest` 与 `task_board` 权威/投影边界未混淆
5. 存在最小 `validator / projector` 雏形
6. 无 runtime 越界
7. 无插件直连、无网络总线、无 SQLite 提前实现
8. 四个子任务三件套齐全

## 退回标准
1. 把 `task_board` 写成权威状态源
2. 提前实现自动互通 runtime
3. 提前实现 SQLite / timeout / retry
4. 提前实现插件 UI
5. 交付物与边界口径不一致
6. 回收件不完整

## 局部修正后再审
- 命名问题
- schema/example 小缺口
- README 缺小节
- 写回件路径错误
