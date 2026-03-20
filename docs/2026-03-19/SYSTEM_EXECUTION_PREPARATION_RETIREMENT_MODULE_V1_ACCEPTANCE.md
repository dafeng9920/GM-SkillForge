# 系统执行层 preparation 历史资产退役验收标准 v1

## 通过标准
- 已生成完整旧路径引用盘点。
- 所有活动文档/脚本引用已切换到 `system_execution/`。
- `system_execution_preparation/` 已明确标记为历史资产或已删除。
- 导入链与模块报告未再依赖旧路径。
- Review 无阻断性问题。
- Compliance 结论为 `PASS`。

## 退回标准
- 仍有活跃引用指向旧目录。
- 清理过程中改动了 frozen 主线。
- 清理过程中引入 runtime / external integration。
- 借清理改写了 `system_execution/` 职责边界。

## 局部修正后再审
- 少量文档仍残留旧路径
- 自检脚本中的帮助文本未更新
- 退役说明缺失
