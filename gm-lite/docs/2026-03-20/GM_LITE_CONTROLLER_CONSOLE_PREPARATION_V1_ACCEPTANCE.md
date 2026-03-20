# GM LITE Controller Console Preparation v1 Acceptance

## 通过标准
1. controller console 职责边界清晰
2. controller console 不负责项清晰
3. 与 `.gm_bus`、verification、task board 承接关系清晰
4. 主控官最小视图定义清晰
5. 主控官最小动作定义清晰
6. 未进入 UI / watcher / adapter / runtime
7. 四个子任务三件套齐全

## 退回标准
1. 控制台被定义成权威状态源
2. 控制台被定义成自动执行层
3. 混入 UI / watcher / adapter / runtime
4. 视图与动作边界冲突明显
5. 回收件不完整

## 局部修正后再审
- 术语不统一
- 视图命名问题
- 小范围边界表达不清
