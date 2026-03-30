# GM LITE Plugin Shell Seed Implementation v1 Boundary Rules

## 核心边界
- 只做最小插件壳 seed
- 不偷跑完整产品化
- 不偷跑完整自动桥接

## 宿主
- 默认宿主：
  - `VS Code Extension`

## 允许项
- 插件入口文件
- 最小命令注册
- 最小状态面板或视图容器
- 读取 `GM-LITE` 状态模型
- 动作入口占位
- bridge hook 占位

## 禁止项
- 不改 `.gm_bus` contract
- 不改 `BusManager` 核心逻辑
- 不改 `BlueprintOrchestrator` 主流程
- 不直接接真实外部 AI 通道
- 不做完整 auto-send / auto-receive

## 成败判断
- 是否让插件壳真实出现
- 是否让系统开始有产品承载体
- 是否逼近“手动转递消失”的第一刀
