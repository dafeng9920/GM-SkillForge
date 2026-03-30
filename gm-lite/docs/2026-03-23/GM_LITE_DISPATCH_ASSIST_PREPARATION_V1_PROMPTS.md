# GM LITE Dispatch Assist Preparation v1 Prompts

## 分派顺序
- 第一波并行：`DA1 + DA2`
- 第二波串行：`DA3`，依赖 `DA1 / DA2`
- 第三波串行：`DA4`，依赖 `DA3`

## 主控官提示
- 子任务默认启用最小事实源
- 报告必须原子化写回
- 默认不跨库搜索
- 若出现自动发送 / direct-connect / runtime 扩张，必须升级主控官
