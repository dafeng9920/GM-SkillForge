# GM LITE Real Test Harness Preparation v1 Boundary Rules

## 核心边界
- 只做真实测试体系的准备定义
- 不偷跑完整测试实现
- 不用这轮去补业务逻辑

## 权威路径
- 权威项目树：
  - `D:\gm-lite`
- 镜像文档树：
  - `D:\GM-SkillForge\gm-lite`

## 允许项
- 测试对象范围定义
- 测试命令入口定义
- 测试文件目录结构定义
- `.md + .json` 测试报告口径定义
- exclusions / 风险 / change control 定义

## 禁止项
- 不偷跑完整 pytest/测试框架实现
- 不修改 `.gm_bus` contract
- 不修改插件壳主逻辑
- 不借机做新功能开发

## 当前判断标准
- 是否明确了可跑、可测、可证明的测试脉络
- 是否为后续 minimal implementation 提供了稳定边界
