# GM-LITE 权威路径规则 V1

## 1. 核心结论

当前 `GM-LITE` 的权威项目树为：

- `D:\gm-lite`

`D:\GM-SkillForge\gm-lite` 当前只作为：

- 主控文档镜像树
- 设计与制度件仓
- 任务卡生成仓

它不是 execution / review / compliance / `.gm_bus` / runtime artifacts 的权威落盘树。

---

## 2. 一刀切规则

凡涉及以下真实写回：

- execution report
- review report
- compliance attestation
- `.gm_bus` 记录
- sample payload
- runtime artifacts

一律优先写入：

- `D:\gm-lite\...`

若 `D:\GM-SkillForge\gm-lite` 与 `D:\gm-lite` 路径口径冲突：

- 一律以 `D:\gm-lite` 为准

---

## 3. 分工

### 权威树
- `D:\gm-lite`

### 镜像树
- `D:\GM-SkillForge\gm-lite`

镜像树只承载：

- scope
- boundary
- prompts
- tasks
- task board
- report
- manifesto / architecture / 制度件

---

## 4. 当前结论

从现在开始：

1. `D:\gm-lite` = 权威树
2. `D:\GM-SkillForge\gm-lite` = 镜像树
3. AI 军团不得再把两者混为同一写回目标

---

## 5. Runtime 路径守卫补充

- runtime / BusManager 优先使用绝对路径，不信相对路径
- 对关键路径建议做 `abspath / resolve` 绝对化处理
- 如 `D:\gm-lite` 根路径校验失败：
  - 直接 fail-closed 退出
  - 不允许带着错误路径继续推进后续步骤
