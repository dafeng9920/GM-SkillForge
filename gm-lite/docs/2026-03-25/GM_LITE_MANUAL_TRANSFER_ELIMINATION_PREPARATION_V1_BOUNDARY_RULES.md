# GM LITE Manual Transfer Elimination Preparation v1 Boundary Rules

## 核心边界
- 只做手动转递消失的准备定义
- 不偷跑完整 bridge implementation
- 不偷跑完整 auto-dispatch

## 权威路径
- 权威项目树：
  - `D:\gm-lite`
- 镜像文档树：
  - `D:\GM-SkillForge\gm-lite`

## 允许项
- 手动转递链路拆解
- 第一刀切点冻结
- send hook / receive hook / writeback hook 位置定义
- 插件壳与 `.gm_bus` 的最小对接边界定义

## 禁止项
- 不直接实现外部插件通道接管
- 不绕过三权分立
- 不绕过 `manifest / blueprint / writeback` 证据链
- 不改 `.gm_bus` 既有 contract

## 判断标准
- 是否真实逼近“手动转递开始消失”
- 是否不以牺牲证据链和边界为代价
