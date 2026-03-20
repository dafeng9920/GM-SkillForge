# GM LITE Controller Console Minimal Implementation v1 Prompts

## 主控官速览

### 第一波并行
- CI1 console skeleton implementation
- CI2 read/view model implementation

### 第二波串行
- CI3 state/alert/gate-ready views
- CI4 control actions placeholders
- 依赖：CI1 / CI2

### 统一回收路径
- `gm-lite/docs/2026-03-20/verification/gm_lite_controller_console_minimal_implementation/`

### 主控官一句话判断标准
- 四个子任务都具备 `execution / review / compliance` 后，才允许终验

## 本轮统一优化规则
- 最小事实源投影
- 原子化写回
- 搜索范围节流
- 主控官回收最小化
- 回填优先，不重跑优先
