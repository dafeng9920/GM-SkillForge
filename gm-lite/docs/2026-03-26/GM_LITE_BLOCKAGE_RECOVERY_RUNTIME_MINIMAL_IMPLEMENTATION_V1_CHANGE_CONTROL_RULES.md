# GM LITE Blockage Recovery Runtime Minimal Implementation v1 Change Control Rules

## 变更原则
- 本轮只补最小 runtime 闭环
- 所有新增恢复逻辑必须可审计、可回放、可写回
- 不得因为追求自动化而跳过人工裁决位

## 升级条件
- 若发现需要完整 auto-orchestrator 才能继续，必须升级主控官
- 若 tri-split 被自动流转合并或绕过，直接判为越界
- 若 blockage/recovery 需求扩展到多域复杂调度，另立后续模块
