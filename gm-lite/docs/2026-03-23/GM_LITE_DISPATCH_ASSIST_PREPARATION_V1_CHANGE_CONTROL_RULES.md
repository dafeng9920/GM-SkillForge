# GM LITE Dispatch Assist Preparation v1 Change Control Rules

## 允许变更
- 可以细化职责边界
- 可以细化 assist 输入输出字段
- 可以细化 next hop / backfill / dispatch packet 的准备定义
- 可以补充最小样板路径口径

## 禁止变更
- 不得引入自动发送
- 不得引入跨插件 direct-connect
- 不得引入 timeout / retry / receipt runtime
- 不得把 controller console 职责并入 dispatch assist
- 不得改写 `.gm_bus` frozen 主线

## 升级条件
- 出现职责重叠
- 出现路径权威冲突
- 出现自动发送诉求
- 出现 direct-connect 诉求
- 出现试图把 preparation 直接拉成 implementation 的行为
