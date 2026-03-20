# GM Shared Task Bus Preparation v1 Prompts

## 主控官速览

### 第一波并行
- B1 `.gm_bus` directory structure
- B2 protocol object boundaries

### 第二波串行
- B3 manifest / projection boundary
- B4 runtime exclusions / change control
- 依赖：B1 / B2

### 统一回收路径
- `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_preparation/`

### 主控官一句话判断标准
- 四个子任务都具备 `execution / review / compliance` 后，才允许终验

## 本轮统一优化规则

### 最小事实源投影
- 若全局 `scope / boundary_rules` 对单子任务过大，主控官应优先提供任务级最小上下文投影
- 不要求执行体为单任务吞入全部全局背景

### 原子化写回
- `execution / review / compliance` 写回件只写增量改动、核心结论、必要 EvidenceRef
- 不重复抄写任务卡原文

### 搜索范围节流
- 默认只允许在 `gm-lite/` 当前模块相关目录内搜索
- 未经主控放行，不跨 `D:/NEW-GM` 或其他大仓库扫描
