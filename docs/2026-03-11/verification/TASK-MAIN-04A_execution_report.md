# TASK-MAIN-04A 执行报告

## 基本信息

- **任务ID**: TASK-MAIN-04A
- **任务名称**: 前端主链步骤展示
- **执行时间**: 2026-03-11
- **状态**: 已完成

## 交付内容

### 1. 新建文件

| 文件路径 | 描述 | 行数 |
|---------|------|------|
| [ui/app/src/components/governance/MainChainStepPanel.tsx](../../../ui/app/src/components/governance/MainChainStepPanel.tsx) | 主链步骤展示组件 | ~470行 |
| [docs/2026-03-11/verification/TASK-MAIN-04A_compliance_attestation.json](TASK-MAIN-04A_compliance_attestation.json) | 合规证明 | JSON |

### 2. 修改文件

| 文件路径 | 修改内容 |
|---------|---------|
| [ui/app/src/components/governance/index.ts](../../../ui/app/src/components/governance/index.ts) | 导出新组件和类型 |
| [ui/app/src/pages/execute/RunIntentPage.tsx](../../../ui/app/src/pages/execute/RunIntentPage.tsx) | 集成主链步骤面板 |

## 功能概述

### MainChainStepPanel 组件

展示主链的5个核心步骤：

1. **Permit** - 执行许可检查
2. **Pre-Absorb** - 吸收前置检查
3. **Absorb** - 吸收
4. **Local Accept** - 本地验收
5. **Final Accept** - 最终验收

### 状态类型

每个步骤支持以下状态：

- `pending` - 等待中 (灰色圆圈)
- `running` - 执行中 (蓝色播放图标，带脉冲动画)
- `pass` - 通过 (绿色勾)
- `fail` - 失败 (红色叉)
- `deny` - 拒绝 (黄色禁止标志)

### UI 特性

- 可展开查看详情（evidence_ref、错误信息）
- 点击复制证据引用
- 显示步骤执行时间戳
- 步骤间连接线颜色随状态变化
- 响应式布局
- 状态图例说明

## 数据映射位

组件预留了真实后端数据映射接口：

```typescript
export interface MainChainStep {
  id: MainChainStepId;
  name: string;
  shortLabel: string;
  description: string;
  status: MainChainStepStatus;
  evidenceRef?: string;
  error?: string;
  gateDecision?: 'ALLOW' | 'REQUIRES_CHANGES' | 'DENY';
  startedAt?: string;
  completedAt?: string;
}
```

## 模拟数据

提供 `generateMockMainChainSteps()` 函数生成5种状态的模拟数据：

- `idle` - 全部待执行
- `running` - 部分通过，正在执行
- `pass` - 全部通过
- `fail` - 执行失败
- `deny` - 被拒绝

## 约束符合性

✅ 不做整站重构 - 只新增组件
✅ 不改后端协议 - 使用 props 接收数据
✅ 不扩到 SEO/量化支线 - 仅主链步骤
✅ 不做假展示 - 预留真实数据映射位

## 风险

| 级别 | 描述 | 缓解措施 |
|-----|------|---------|
| 低 | 当前使用模拟数据 | 数据结构稳定，替换无需改动组件 |
| 低 | 样式注入可能冲突 | 使用唯一 styleId 隔离 |
| 中 | 步骤顺序固定 | TypeScript 字面量类型，扩展有提示 |

## 证据引用

- [MainChainStepPanel.tsx](../../../ui/app/src/components/governance/MainChainStepPanel.tsx) - 组件实现
- [RunIntentPage.tsx](../../../ui/app/src/pages/execute/RunIntentPage.tsx) - 集成位置
- [TASK-MAIN-04A_compliance_attestation.json](TASK-MAIN-04A_compliance_attestation.json) - 合规证明
