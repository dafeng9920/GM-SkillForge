# GM Shared Task Bus Minimal Validation v1 Boundary Rules

## 模块边界
- 本模块只做验证，不做新实现主导
- 本模块只判断当前最小实现是否满足进入 frozen judgment 的条件
- 本模块不扩展产品范围

## 验证边界
- 结构验证：目录与文件骨架
- 协议验证：最小对象字段与命名
- 视图验证：manifest / task_board / projector / validator 关系
- 边界验证：runtime、SQLite、adapter、插件直连仍未混入

## 权威状态边界
- `manifest` 可作为当前最小实现的权威骨架候选
- `task_board` 仍是投影视图
- 若发现两者混淆，直接列为阻断问题

## change control
- 允许：问题清单、缺口说明、非阻断性建议
- 受控：最小命名修正建议、字段补充建议
- 禁止：借验证轮直接做新实现
