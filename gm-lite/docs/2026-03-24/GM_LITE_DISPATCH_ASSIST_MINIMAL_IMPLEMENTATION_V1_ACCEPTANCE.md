# GM LITE Dispatch Assist Minimal Implementation v1 Acceptance

## 通过标准

### A. next hop
- 可以基于 bus state / verification state 计算 `next_hop`

### B. missing piece / backfill
- 可以识别缺件
- 可以生成标准路径回填提示

### C. dispatch packet
- 可以组装最小 dispatch packet
- 与 BusManager 记录格式兼容

### D. 样板与说明
- 已提供 sample input / output
- 已提供 README / usage
- 已冻结 exclusions / change control

## 不通过条件
- assist 输出仍然依赖手工拼装
- 无法识别标准缺件
- dispatch packet 不能稳定生成
- 越界到 auto-send / runtime / direct-connect
