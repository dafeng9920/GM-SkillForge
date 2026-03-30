# GM LITE Plugin Shell Preparation v1 Boundary Rules

## 核心边界
- 只做 `插件外壳准备`
- 不偷跑完整插件实现
- 不偷跑完整桥接实现

## 权威路径
- 权威项目树：
  - `D:\gm-lite`
- 镜像文档树：
  - `D:\GM-SkillForge\gm-lite`

## 允许项
- 宿主锁定
- 最低能力清单
- 插件入口/面板/动作面草图级定义
- `manual transfer elimination` 第一刀路径定义
- change control / exclusions 定义

## 禁止项
- 不写重型 UI 代码
- 不改现有 `.gm_bus` contract
- 不改现有 `BusManager` 核心逻辑
- 不改现有 `BlueprintOrchestrator` 逻辑
- 不硬接真实外部插件通道
- 不做完整 release packaging

## 主线判断标准
- 是否逼近：
  - 插件外壳成立
  - 手动转递开始消失
- 若不能逼近这两条，则后置
