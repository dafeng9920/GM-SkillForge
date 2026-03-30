# GM LITE Sample Flow Validation v1 Acceptance

## 通过标准

### A. happy path
- 至少一条最小 happy path 样板链可回放
- `RAW -> ENRICHED -> FROZEN` 状态成立
- `next_hop` 可稳定给出

### B. missing piece / backfill
- 至少一条缺件样板链可识别缺件
- 可生成 backfill assist
- 可恢复到 `GATE_READY`

### C. dispatch / bus / verification
- dispatch packet 与 bus state 可对齐
- verification 三件套可稳定回收
- `lifecycle_status / gate_levels / validation_status` 可被样板证明

### D. 说明与回放
- 已提供样板说明
- 已提供最小 replay / validation notes
- 无 watcher / auto-send / direct-connect 越界

## 不通过条件
- 样板链只能口头说明，无法落盘回放
- 缺件识别或 backfill 无法成立
- 状态链无法闭环
- 越界到 runtime / watcher / direct-connect
