# GM Shared Task Bus Minimal Validation v1 Prompts

## 主控官速览

### 第一波并行
- V1 structure validation
- V2 protocol object validation

### 第二波串行
- V3 manifest / projection / validator validation
- V4 boundary & change-control validation
- 依赖：V1 / V2

### 统一回收路径
- `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_minimal_validation/`

### 主控官一句话判断标准
- 四个子任务都具备 `execution / review / compliance` 后，才允许终验

## 本轮统一优化规则

### 最小事实源投影
- 子任务默认只读取当前任务直接相关的最小事实源
- 不为单任务加载全部无关全局背景

### 原子化写回
- 写回只记录阻断问题、非阻断问题、核心结论、必要 EvidenceRef
- 不复述任务卡原文

### 搜索范围节流
- 默认只允许在 `gm-lite/` 当前模块相关目录内搜索
- 未经主控放行，不跨库扫描

### 主控官回收最小化
- 主控默认优先读 task board、report、verification 文件名清单
- 只有存在 `FAIL / REQUIRES_CHANGES / 路径冲突 / 权威状态不一致` 时才深读正文

### 回填优先
- 缺件优先做回填追认，不默认重跑整轮任务

### 单任务上下文预算
- 默认不超过：1 张任务卡 + 2 份边界文档 + 1 份局部 snapshot
