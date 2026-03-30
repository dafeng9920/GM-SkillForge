# GM LITE Shell Seed Implementation v1 Acceptance

## 通过标准

### A. 统一入口
- 存在单一 shell 入口
- 可从入口看到 bus / blueprint / dispatch 的最小总览

### B. 最小操作面
- 至少存在一组最小动作：
  - `ingest`
  - `inspect`
  - `dispatch`
  - `suspend`
  - `resume`
- 动作可映射到已有 runtime / assist / blueprint 能力

### C. 状态可见性
- 可看到当前任务/蓝图状态
- 可看到 gate / redline / recovery 的最小状态
- 可看到需要人工转递的明确位置

### D. 使用说明
- 已提供 README / usage / example
- 无重型 UI / auto-send / direct-connect 越界

## 不通过条件
- 仍然只能靠翻散文档定位入口
- 没有最小动作面
- 看不到当前状态、卡点、下一步
- 越界到重插件或自动发单
