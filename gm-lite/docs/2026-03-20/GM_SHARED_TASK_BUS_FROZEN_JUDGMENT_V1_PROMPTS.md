# GM Shared Task Bus Frozen Judgment v1 Prompts

## 主控官速览

### 第一波并行
- F1 structure frozen check
- F2 protocol frozen check
- F3 boundary frozen check

### 第二波串行
- F4 frozen rules draft
- 依赖：F1 / F2 / F3

### 统一回收路径
- `gm-lite/docs/2026-03-20/verification/gm_shared_task_bus_frozen_judgment/`

### 主控官一句话判断标准
- 四个子任务都具备 `execution / review / compliance` 后，才允许终验

## 本轮统一优化规则
- 最小事实源投影
- 原子化写回
- 搜索范围节流
- 主控官回收最小化
- 回填优先，不重跑优先
