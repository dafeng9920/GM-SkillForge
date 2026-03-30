# GM LITE Real Test Harness Minimal Implementation v1 Boundary Rules

## 核心边界
- 只做测试体系最小实现
- 不借机开发业务功能
- 不偷跑重型测试平台

## 权威路径
- 权威项目树：
  - `D:\gm-lite`
- 镜像文档树：
  - `D:\GM-SkillForge\gm-lite`

## 允许项
- 最小测试命令
- 最小测试文件
- sample replay test
- operational validation test
- `json + md` 测试报告

## 禁止项
- 不改 `.gm_bus` contract
- 不改主控逻辑
- 不改插件壳主流程
- 不引入与当前主线无关的重型测试基础设施

## 成功判断
- 是否真的有“可跑测试命令”
- 是否真的有“测试文件和报告”
