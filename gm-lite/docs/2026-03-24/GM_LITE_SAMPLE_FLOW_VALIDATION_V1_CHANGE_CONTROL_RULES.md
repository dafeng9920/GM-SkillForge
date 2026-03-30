# GM LITE Sample Flow Validation v1 Change Control Rules

## Frozen 输入
- `GM_LITE_DISPATCH_ASSIST_MINIMAL_IMPLEMENTATION_V1_REPORT.md`
- `GM_BUS_MANAGER_SEED_IMPLEMENTATION_V1_REPORT.md`
- 既有 `.gm_bus` contract 与 frozen judgment 文档

## 允许变更
- 补充样板输入输出
- 补充 replay 说明
- 补充 validation notes
- 修正样板路径与 evidence 引用

## 禁止变更
- 不重写总线 contract
- 不扩展 runtime 设计
- 不改写 controller console 范围
- 不把样板验证升级成 release judgment

## 主控规则
- 出现 authority path 冲突，立即暂停
- 出现 scope expansion，立即暂停
- 出现 frozen contract 被改写，立即暂停
