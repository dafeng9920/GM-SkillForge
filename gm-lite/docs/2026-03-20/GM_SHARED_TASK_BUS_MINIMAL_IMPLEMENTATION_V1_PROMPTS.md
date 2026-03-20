# GM Shared Task Bus Minimal Implementation v1 Prompts

## 主控官速览

### 第一波并行
- C1 `.gm_bus` skeleton implementation
- C2 protocol object seed implementation

### 第二波串行
- C3 manifest / projector / validator stub
- 依赖：C1 / C2

### 第三波串行
- C4 implementation guard / sample flow packaging
- 依赖：C3

### 统一回收路径
- `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_implementation/`

### 主控官一句话判断标准
- 四个子任务都具备 `execution / review / compliance` 后，才允许终验

## 本轮统一优化规则

### 最小事实源投影
- 子任务默认只读取当前任务直接相关的最小事实源
- 不为单任务加载全部无关全局背景

### 原子化写回
- 写回只记录增量改动、核心结论、必要 EvidenceRef
- 不复述任务卡原文

### 搜索范围节流
- 默认只允许在 `gm-lite/` 当前模块相关目录内搜索
- 未经主控放行，不跨库扫描
