# GM LITE Manual Transfer Elimination Minimal Implementation v1 Boundary Rules

## 核心边界
- 只做最小自动流转实现
- 不偷跑完整 workflow engine
- 不破坏主控 + 三权分立骨架

## 权威路径
- 权威项目树：
  - `D:\gm-lite`
- 镜像文档树：
  - `D:\GM-SkillForge\gm-lite`

## 允许项
- 最小 send action
- 最小 receive action
- 最小 writeback 读取与状态推进
- 插件壳内最小 bridge hook 接通

## 禁止项
- 不绕过 execution / review / compliance 分层
- 不破坏 manifest / blueprint / writeback 证据链
- 不改 `.gm_bus` 核心 contract
- 不一口气做复杂多通道自动化

## 成功判断
- 是否真实减少了一段手动转递
- 是否没有以牺牲边界和审计为代价
