# GM LITE Sample Flow Validation v1 Boundary Rules

## 权威路径
- 权威项目树：`D:\gm-lite`
- 镜像 / 主控文档树：`D:\GM-SkillForge\gm-lite`
- 权威 verification 路径以 `D:\gm-lite\docs\2026-03-24\verification\gm_lite_sample_flow_validation\` 为准

## 允许验证对象
- `.gm_bus` 下任务包样板
- `BusManager` 最小读写结果
- dispatch assist 输出
- verification 三件套
- `validation_status`
- `lifecycle_status`
- `gate_levels`

## 禁止越界
- 不发真实外部请求
- 不接真实插件 API
- 不做自动发送
- 不做 receipt / ack runtime
- 不做 timeout / retry
- 不改写已 frozen 的 bus contract

## 样板验证原则
- 优先验证闭环，不追求大而全
- 优先验证权威路径产物，不以对话完成代替落盘
- 优先验证状态链与证据链，不以口头说明代替样板输出

## 写回纪律
- execution / review / compliance 三件套必须齐
- 如有附加样板文件，必须可从权威路径直接扫描
- FAIL 不得自行结案，必须升级主控官
