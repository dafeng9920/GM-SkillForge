# GM LITE Manual Transfer Elimination Preparation v1 Scope

## 模块目标
- 正式定义 `GM-LITE` 打掉手动转递的第一阶段
- 冻结“最后一米人肉搬运”该从哪里切断
- 为后续 bridge / send / receive / writeback 自动流转做前置准备

## 当前定位
- 这不是完整自动化实现
- 这是手动转递消失主线的 preparation
- 它直接服务于：
  - `作战运行级 1`

## 本轮必须回答
1. 手动转递当前真实发生在哪几处
2. 第一刀先砍哪一处最值钱
3. 插件壳里哪些位置作为 send / receive / writeback 挂点
4. 哪些边界现在绝不能越

## 完成定义
- 已明确第一刀切点
- 已明确插件侧 send/receive hook 位置
- 已明确 writeback 回流最小链路
- 已明确 exclusions / 风险 / change control
