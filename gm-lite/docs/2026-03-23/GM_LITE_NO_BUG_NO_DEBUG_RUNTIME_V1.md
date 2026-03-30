# GM-LITE No Bug, No Debug Runtime V1

## 1. 核心口号的工程化含义

`No Bug, No Debug` 在 GM-LITE 中不是宣传口号，而是一个运行时目标：

> 尽量把错误拦截在“逻辑态”和“沙箱态”，  
> 不让未过门禁的候选代码进入正式视图与正式项目目录。

更直白地说：

| 传统开发 | GM-LITE / 1130 近防炮流程 |
|---|---|
| Debug 是为了修复错误 | 拦截是为了拒绝错误 |
| 代码写好了，发现有 Bug，人去修 | 代码生成了，不符合 Contract / Spec / Gate，系统直接物理销毁 |
| 开发者在屎山里挣扎 | 开发者只看到通过“近防炮”拦截后的纯净代码 |

这不等于承诺“世界上绝对没有 Bug”，而是明确以下原则：

- 未通过架构门禁的代码，不配出现在 IDE 主视图里
- Debug 不应主要发生在人工阅读阶段
- Debug 应被前移到：
  - Contract 检查
  - 结构影子审计
  - 静态扫描
  - 沙箱冒烟测试

---

## 2. 从“插件”降维到“过滤器”

GM-LITE Light 的第一落地重点，不应是复杂 UI，而应是：

> 一个监听 `.gm_bus`、触发门禁、筛掉坏产物、只放行合格产物的自动过滤器。

也就是说，Light 版的灵魂不是“界面像不像插件”，而是：

- 会监听
- 会校验
- 会熔断
- 会固化

---

## 3. 断头台式运行时的四步闭环

### Step 1. Spec / Contract 进入总线

指挥层产出：

- `.spec`
- `Contract.json`
- `Checklist.json`

并将其放入：

- `.gm_bus`

这一步不是让执行层“理解大局”，而是先冻结法律。

### Step 2. 执行层在沙箱中齐射

执行层在受控环境中产出候选代码。

要求：

- 只能在 Contract 边界内自愈
- 不能跳过 Checklist
- 不能用解释掩盖非法副作用

### Step 3. 运行时过滤器执行门禁

过滤器必须依次触发：

1. `spec legality check`
2. `contract check`
3. `AST / Schema / Type gate`
4. `structural shadowing`
5. `smoke test / hard test`

任一失败：

- 候选产物直接熔断
- 不进入正式目录
- 不进入主视图

### Step 4. 只有合格产物才被固化

只有全部通过的产物，才允许：

- 被移动到正式技能目录
- 被插件主视图读取
- 被用户看到为“可交付产物”

---

## 4. 三个核心动作

### 4.1 SpecKit / Contract 强约束

运行时首先相信的是 Contract，而不是执行层口头完成。

如果代码出现：

- 非法 `os` 调用
- 未允许副作用
- 缺失必需异常处理
- 类型或 Schema 越界

则运行时直接打回，不听解释。

### 4.2 逻辑指纹对比

运行时要把：

- 指挥层的 `PseudocodeFlow / LogicTree`
- 执行层代码的 AST / 结构指纹

做关键结构比对。

重点不在“全文同构”，而在：

- 关键分支
- 状态变更顺序
- 副作用位置
- 禁止结构是否出现

结构不对，直接拒收。

### 4.3 沙箱冒烟测试

代码生成后，必须在受控环境里跑最小物理反馈。

若：

- `Exit Code != 0`
- 测试失败
- 覆盖率异常低
- 非法系统调用出现

则候选产物仍视为假输出。

---

## 5. Watchman 只是原型，不是全部系统

使用 `watchdog` / 监听脚本作为 Light 版第一步是合理的。

但必须明确：

> `Watchman.py` 是 GM-LITE runtime kernel prototype，  
> 不是完整 GM-LITE。

它解决的是：

- 监听 `.gm_bus`
- 触发门禁链
- 只让通过者进入正式目录

它暂时不解决：

- 完整插件 UI
- 完整跨插件适配器
- 云端长时运行
- 完整自动重试 / 超时恢复

---

## 6. 统一命名：不再使用 `.forge_sync`

本文件中的运行时监听目录，统一使用：

- `.gm_bus`

不再新建：

- `.forge_sync`

原因：

- `.gm_bus` 已是共享任务现实层的权威命名
- 若再引入 `.forge_sync`，会造成：
  - 总线语义分裂
  - 状态源冲突
  - 适配器目标不唯一

因此：

> Light 版的 Watchman / 过滤器，监听目标必须是 `.gm_bus`。

---

## 7. 对用户体验的真实改变

当这套运行时成立后，用户的工作方式会变化为：

- Codex 负责写 Spec / Contract
- 执行军团在沙箱里带约束齐射
- 过滤器在后台做断头台式筛选
- 用户只在 IDE 里看到已经通过门禁的产物

也就是说：

> 把痛苦留给 AI 和运行时，  
> 把确定性留给用户。  

---

## 8. 与现有制度件的关系

本文件直接继承并具体化以下制度件：

- [GM_LITE_TRUST_ARCHITECTURE_NOT_AI_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-23/GM_LITE_TRUST_ARCHITECTURE_NOT_AI_V1.md)
- [GM_LITE_ARCHITECTURE_PANORAMA_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-23/GM_LITE_ARCHITECTURE_PANORAMA_V1.md)
- [GM_LITE_SPECKIT_FIT_ASSESSMENT_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-23/GM_LITE_SPECKIT_FIT_ASSESSMENT_V1.md)
- [GM_LITE_ANTI_DRIFT_SUPERVISION_MODEL_V1.md](/d:/GM-SkillForge/gm-lite/docs/2026-03-23/GM_LITE_ANTI_DRIFT_SUPERVISION_MODEL_V1.md)

---

## 9. 当前结论

本文件正式冻结以下判断：

1. `No Bug, No Debug` 的工程含义是“错误前移拦截”，不是空喊零缺陷
2. GM-LITE Light 应优先实现“断头台式过滤器”，而不是重 UI
3. 运行时监听与门禁触发应统一围绕 `.gm_bus`
4. Watchman / watchdog 路线可作为 Light 版 runtime 原型
5. 只有通过联合门禁的产物，才允许进入正式目录和正式视图
