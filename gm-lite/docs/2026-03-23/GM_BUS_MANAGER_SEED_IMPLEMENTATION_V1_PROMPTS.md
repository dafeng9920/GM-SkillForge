# GM BusManager Seed Implementation v1 Prompts

## 分派顺序
- 第一波并行：`BM1 + BM2`
- 第二波串行：`BM3`，依赖 `BM1 / BM2`
- 第三波串行：`BM4`，依赖 `BM3`

## 权威路径纪律
- `D:\gm-lite` = 权威项目树
- `D:\GM-SkillForge\gm-lite` = 主控文档镜像树
- 所有 verification / `.gm_bus` / sample payload / 实现文件，默认写入 `D:\gm-lite`

## 主控官提示
- 最小事实源
- 原子化写回
- 不跨库搜索
- 所有实现仅围绕 `BusManager` seed，不碰 watcher / auto-send / direct-connect
