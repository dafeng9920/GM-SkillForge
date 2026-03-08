# SkillForge + OpenClaw Integration Task List

## Phase 1: Research & Environment Setup
- [x] Analyze SkillForge Registry architecture
- [x] Analyze SkillForge Governance Gates (Sandbox/Permit)
- [ ] Install OpenClaw in WSL2/Docker environment
- [ ] Configure Feishu Open Platform (App, Permissions, Bot)
- [ ] Verify OpenClaw + Feishu "Long Connection" (WebSocket)
- [ ] Verify OpenClaw basic functionality


## Phase 2: Integration Strategy Design
- [ ] Define the "Contract" between SkillForge and OpenClaw
- [/] Draft Implementation Plan for chosen integration path
- [ ] Review plan with Commander (User)

## Phase 3: Implementation
- [ ] Implement OpenClaw Adapter in SkillForge
- [ ] Implement Governance Hook in OpenClaw
- [ ] Connect OpenClaw Trace events to SkillForge G6 (Sandbox)
- [ ] Implement Permit-based execution for OpenClaw via SkillForge G9

## Phase 4: Verification
- [ ] Run E2E test: Trigger OpenClaw action -> Intercept by SkillForge -> Audit -> Approve/Reject
- [ ] Generate AuditPack for OpenClaw execution
