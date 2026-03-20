# 系统执行层 preparation 历史资产退役边界规则 v1

## 允许处理的对象
- `skillforge/src/system_execution_preparation/`
- `docs/2026-03-19/verification/system_execution_minimal_landing/` 下直接引用旧路径的材料
- `docs/2026-03-19/` 下系统执行层模块文档中与旧路径直接相关的内容

## 禁止处理的对象
- `contracts/` 下所有 frozen 对象
- `gate / review / release / audit` frozen 文档正文
- `skillforge/src/system_execution/` 五子面职责语义
- runtime / external integration 相关实现

## 退役规则
- 先盘点，再修正文档/脚本引用，再确认导入链，再退役旧目录。
- 未通过合规确认前，不删除旧目录。
- 删除旧目录必须有：
  - 引用清零证据
  - Review 通过
  - Compliance PASS

## 禁止混入的语义类型
- 新功能扩展
- 新模块职责变更
- runtime 行为实现
- 外部集成接入
