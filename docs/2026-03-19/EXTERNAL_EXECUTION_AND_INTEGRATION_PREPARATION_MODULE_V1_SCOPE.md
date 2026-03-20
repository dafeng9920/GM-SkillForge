# 外部执行与集成准备模块 v1 范围文档

## 当前模块
- `外部执行与集成准备模块 v1`

## 当前唯一目标
- 为外部执行与集成层建立“可承接已冻结主线、可连接现实世界、可被审查与验收、不可倒灌裁决层”的最小准备骨架与治理规则。

## 六个子面
1. connector contract
2. integration gateway
3. secrets / credentials boundary
4. external action policy
5. retry / compensation boundary
6. publish / notify / sync boundary

## 允许进入的范围
- 六个子面的最小目录骨架
- 六个子面的最小职责边界
- 与 frozen 主线的承接关系说明
- 与 `system_execution` 的接口关系说明
- permit / evidence / audit pack / decision 的使用规则说明
- “外部执行层只能持 permit 行动，不能自行裁决”的规则
- “Evidence/AuditPack 由内核生成且不可改写”的规则
- 后续 runtime 的排除边界

## 禁止进入的范围
- Gate / Review / Release / Audit 对象返修
- `system_execution` 返修
- runtime 执行层
- 真实外部系统接入
- 真实 webhook / queue / registry / db / slack / email / repo 联调
- 真实业务执行逻辑
- 自动重试补偿实现
- 真实发布执行
- 任何会倒灌 frozen 主线边界的改动
- 任何让编排/集成层替代 Governor 裁决的设计
