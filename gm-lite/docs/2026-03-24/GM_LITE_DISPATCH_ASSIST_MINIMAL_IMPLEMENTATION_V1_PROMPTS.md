# GM LITE Dispatch Assist Minimal Implementation v1 Prompts

## 分派顺序
- 第一波并行：`DI1 + DI2`
- 第二波串行：`DI3`，依赖 `DI1 / DI2`
- 第三波串行：`DI4`，依赖 `DI3`

## 权威路径纪律
- `D:\gm-lite` = 权威项目树
- `D:\GM-SkillForge\gm-lite` = 主控文档镜像树
- verification / `.gm_bus` / sample payload / assist runtime artifacts 默认写入 `D:\gm-lite`

## 主控官提示
- 最小事实源
- 原子化写回
- 不跨库搜索
- 所有实现仅围绕 dispatch assist minimal implementation，不碰 auto-send / watcher / direct-connect
