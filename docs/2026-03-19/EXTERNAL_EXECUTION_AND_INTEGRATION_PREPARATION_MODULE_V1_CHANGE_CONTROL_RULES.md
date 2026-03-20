# 外部执行与集成准备模块 v1 变更控制规则

## 允许变更
- 文档补强
- 命名修正
- 类型注解补强
- 非语义性目录/文件命名修正

## 受控变更
- permit 规则表述细化
- Evidence / AuditPack 引用规则细化
- 六子面接口关系补充
- 建议目录/文件骨架增补

## 禁止变更
- 回改 frozen 主线
- 回改 `system_execution`
- 进入 runtime
- 接入真实外部系统
- 实现真实 webhook / queue / db / registry / slack / email / repo 流程
- 实现真实业务执行逻辑
- 自动重试补偿实现
- 真实发布执行
- 让集成层替代 Governor 裁决
- 绕过 permit 规则
- 让 Evidence / AuditPack 可被改写
