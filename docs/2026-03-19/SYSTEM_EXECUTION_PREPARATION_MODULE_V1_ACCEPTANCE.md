# 系统执行层准备模块验收标准 v1

## 通过标准
- 五子面都有最小职责定义。
- 五子面都有明确的不负责项。
- 五子面之间关系清晰，无明显重叠或断裂。
- 与 frozen 主线承接关系清晰且只读。
- 未回改任何 frozen 对象边界。
- 未混入 `runtime / external integration`。
- 未让 `workflow / orchestrator` 成为裁决者。
- 未让 `service / handler / api` 成为真实业务执行层。
- 已完成固定文档 1-6。
- skeleton 与文档口径一致。
- 无阻断性问题。

## 退回标准
- 任一子面进入 runtime。
- 任一子面进入外部执行或集成。
- 任一子面要求改写 frozen 主线。
- 任一子面承载真实业务逻辑。
- `workflow / orchestrator` 被写成治理或执行裁决层。
- `service / handler / api` 被写成真实执行层。
- 文档与 skeleton 不一致。
- Review 或 Compliance 给出未解决的阻断性问题。

## 局部修正后再审
- 命名可再收紧。
- 注释不足。
- 文档缺少非关键小节。
- skeleton 占位文件说明可再清晰。

## 本轮验收结论记录口径
- `ALLOW`：全部通过标准成立。
- `REQUIRES_CHANGES`：仅存在非阻断性问题。
- `DENY`：触发任一退回标准。
