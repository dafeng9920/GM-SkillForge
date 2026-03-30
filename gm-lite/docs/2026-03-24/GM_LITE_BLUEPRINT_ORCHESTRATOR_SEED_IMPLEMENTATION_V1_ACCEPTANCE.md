# GM LITE Blueprint Orchestrator Seed Implementation v1 Acceptance

## 通过标准

### A. 物理路径
- 可扫描 `.gm_bus/inbox`
- 可在 `.gm_bus/active/<intent_trace_id>` 初始化任务目录
- 可生成初始样板文件

### B. 打勾协议
- `BaseGate` 存在统一 checkpoint 更新能力
- `manifest.json` 可实时写入 gate 状态
- `blueprint.md` 可同步反映打勾进度
- 脚本重启后可基于 manifest 续传

### C. M6 最小门禁
- 至少可完成一轮 noun anchors 锁定
- 控制台可输出最小 gate 进度图
- 至少出现一条类似 `[✅] Gate M6: Noun Anchors Locked.` 的样板结果

### D. MirrorSealer
- 当 gate 状态满足条件时可生成最小 `.frozen_seal`
- 具备镜像规则说明与最小样板

## 不通过条件
- active 目录无法初始化
- 打勾只停留在口头，不落 manifest / blueprint
- 无法断点续传
- M6 无法给出最小样板结果
- 越界到完整 runtime / full mirror sync / direct-connect
