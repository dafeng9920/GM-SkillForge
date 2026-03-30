# GM LITE Sample Flow Validation v1 Prompts

## 放行顺序
- 第一波并行：`SV1 + SV2`
- 第二波串行：`SV3`
- 第三波串行：`SV4`

## 权威路径提醒
- 权威项目树以 `D:\gm-lite` 为准
- 标准 verification 路径以 `D:\gm-lite\docs\2026-03-24\verification\gm_lite_sample_flow_validation\` 为准

## 当前模块固定禁止项
- 不实现 watcher
- 不实现 auto-send
- 不实现 receipt / ack runtime
- 不实现 timeout / retry runtime
- 不实现跨插件 direct-connect
