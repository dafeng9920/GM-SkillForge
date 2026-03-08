# Phase 3.5 - Dual-Channel UX Redesign Taskpack

## 0. 决策结论

- 当前 Phase 3（全站样式铺开）暂缓。
- 先执行 Phase 3.5：双对话通道重构（先做单页 PoC，再全站推广）。
- PoC 页面固定为：`RunIntent`。

---

## 1. 目标（必须达成）

1. 建立“双通道工作台”：
   - 通道 A：认知/分析对话（Cognition）
   - 通道 B：执行/交付对话（Execution）
2. 保证治理信息始终前置：
   - `GateDecision`
   - `blocked_by`
   - `evidence_ref`
   - `required_changes`
3. 样式语言升级为“专业治理控制台”，不是普通表单页。

---

## 2. 范围（本阶段只做这些）

### In Scope
- `ui/app/src/pages/execute/RunIntentPage.tsx`
- `ui/app/src/components/governance/DecisionHeroCard.tsx`
- `ui/app/src/components/governance/BlockReasonCard.tsx`
- 新增双通道容器组件（如 `DualChannelWorkbench`）
- 必要样式（CSS Modules + tokens）

### Out of Scope
- 先不改 `AuditPacks`/`SystemHealth`/`ImportSkill` 的全量布局。
- 先不做大规模信息架构迁移。

---

## 3. 双通道信息架构（必须遵守）

## 顶部固定区（不可滚动）
- 左：`GateDecision` 主状态
- 中：`run_id` / `evidence_ref`（可点击 + 复制）
- 右：系统态（ALLOW/BLOCK/REQUIRES_CHANGES）

## 主体区（左右双栏）
- 左栏（A 通道）：认知对话流
  - 输入：分析意图
  - 输出：推理摘要、风险提示、建议动作
- 右栏（B 通道）：执行对话流
  - 输入：执行命令/执行参数
  - 输出：执行结果、阻断原因、required_changes

## 底部区（证据与审计）
- 抽屉式 Evidence 面板
- 每条关键事件可追溯到 `evidence_ref`

---

## 4. 交互规则（硬约束）

1. A/B 两通道消息互不覆盖，必须能独立滚动。
2. 执行失败时，B 通道自动插入 `BlockReasonCard`。
3. 任意 BLOCK 事件必须附 `required_changes`。
4. `run_id:evidence_ref` 组合键一键复制。
5. 移动端降级：双栏改为标签切换，但信息不可丢。

---

## 5. 视觉规则（你要的方向）

1. 主信息卡实色背景，高对比，避免“花哨盖过数据”。
2. Neon 只用于状态点（PASS/BLOCK），禁止大面积发光。
3. 玻璃态只允许次级容器（侧边栏/浮层），禁止主结论区使用。
4. 字体：`Outfit`（标题）+ `Inter`（正文）。
5. 动效仅 2-3 处关键交互；必须兼容 `prefers-reduced-motion`。

---

## 6. 技术约束

1. 禁止第三方 UI 依赖。
2. 禁止新增 inline style。
3. 样式必须落在 CSS Modules + `tokens.css`。
4. 必须保留键盘焦点可见（`:focus-visible`）。
5. 对比度满足 WCAG AA。

---

## 7. 交付物（PoC）

1. `ui/app/src/pages/execute/RunIntentPage.tsx`（双通道布局）
2. `ui/app/src/pages/execute/RunIntentPage.module.css`
3. `ui/app/src/components/governance/DualChannelWorkbench.tsx`（可新建）
4. `docs/2026-02-21/PHASE_3_5_ACCEPTANCE.md`（验收报告）
5. `docs/2026-02-21/PHASE_3_5_WALKTHROUGH.md`（前后对比截图 + 演示说明）

---

## 8. 验收门（Go/No-Go）

### 必过
- `npm run build` 通过
- 双通道可用（桌面双栏 + 移动标签切换）
- 四个治理字段始终可见（首屏）
- 无 inline style
- `prefers-reduced-motion` 生效

### 拒绝条件（NO-GO）
- 样式漂亮但治理信息后置
- 视觉特效覆盖核心数据可读性
- 仅改皮肤，未实现双通道
- 无证据文档（Walkthrough/Acceptance）

---

## 9. 给执行模型的指令头（可直接复制）

```text
你现在执行 Phase 3.5 Dual-Channel UX Redesign（仅 RunIntent PoC）。
必须先实现双通道信息架构，再做视觉。
禁止第三方依赖，禁止 inline style，必须保留治理字段前置。
若任何硬约束无法满足，输出 REQUIRED_CHANGES，不得伪装完成。
```

