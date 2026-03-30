# GM LITE Shell Seed Implementation v1 Prompts

## 放行顺序
- 第一波并行：`SH1 + SH2`
- 第二波串行：`SH3`
- 第三波串行：`SH4`

## 权威路径提醒
- 权威项目树以 `D:\gm-lite` 为准
- 标准 verification 路径以 `D:\gm-lite\docs\2026-03-24\verification\gm_lite_shell_seed_implementation\` 为准

## 当前模块固定禁止项
- 不实现重型 UI
- 不实现 auto-send
- 不实现 receipt / ack runtime
- 不实现 timeout / retry runtime
- 不实现跨插件 direct-connect

## 当前模块默认目标
- 先做外壳
- 先做入口
- 先做最小操作面
- 先把手动转递收缩成一个清晰动作，而不是散落在文档之间
