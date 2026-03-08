# T39 系统运维与错误拦截验收报告

> 文档版本: v1.0
> 任务ID: T39
> 执行者: Kior-A
> 日期: 2026-02-21
> 状态: COMPLETED

---

## 1. 任务概述

### 1.1 任务描述
实现系统运维页面的 Health 模块与全局统一错误拦截组件 BlockReasonCard。

### 1.2 输入规格
- **Job ID**: L45-FE-V10-20260220-007
- **页面路由**: `/system/health`
- **依赖文档**: `docs/2026-02-20/FRONTEND_REQUIREMENTS_v1.md`

### 1.3 交付物

| 文件路径 | 类型 | 状态 |
|---------|------|------|
| `ui/app/src/pages/system/HealthPage.tsx` | 新建 | ✅ 完成 |
| `ui/app/src/components/governance/BlockReasonCard.tsx` | 新建 | ✅ 完成 |
| `docs/2026-02-20/L45_FE_T39_HEALTH_BLOCKCARD_REPORT_v1.md` | 新建 | ✅ 当前文档 |

---

## 2. HealthPage.tsx 实现详情

### 2.1 功能规格

| 功能项 | 规格 | 实现状态 |
|--------|------|---------|
| 默认轮询间隔 | 30s (可配置) | ✅ |
| 轮询范围 | 5s - 300s | ✅ |
| 阈值规则 | 红/橙/绿三色 | ✅ |
| 最近检查历史 | 最多 20 条 | ✅ |
| 手动刷新 | 支持 | ✅ |
| 暂停/恢复轮询 | 支持 | ✅ |

### 2.2 阈值常量（文档+代码）

```typescript
// ui/app/src/pages/system/HealthPage.tsx

/** Default polling interval in milliseconds */
export const DEFAULT_POLL_INTERVAL_MS = 30000; // 30s

/** Minimum polling interval to prevent API abuse */
export const MIN_POLL_INTERVAL_MS = 5000; // 5s

/** Maximum polling interval */
export const MAX_POLL_INTERVAL_MS = 300000; // 5min

export const HEALTH_THRESHOLDS = {
  /** Response time < 500ms is considered healthy (GREEN) */
  GREEN_THRESHOLD_MS: 500,
  /** Response time >= 1000ms is considered degraded (ORANGE) */
  ORANGE_THRESHOLD_MS: 1000,
  /** Any error or response time >= 2000ms is unhealthy (RED) */
  RED_THRESHOLD_MS: 2000,
} as const;
```

### 2.3 导出接口

```typescript
// Types
export type HealthLevel = 'GREEN' | 'ORANGE' | 'RED';
export interface HealthResponse { ... }
export interface HealthCheckEntry { ... }
export interface RouteHealth { ... }

// Helper Functions
export function calculateHealthLevel(responseTimeMs: number, hasError: boolean): HealthLevel;
export function getHealthColor(level: HealthLevel): string;

// Component
export function HealthPage(props: HealthPageProps): React.ReactElement;
```

### 2.4 组件结构

```
HealthPage
├── Header (标题 + 控制按钮)
│   ├── 轮询间隔选择器
│   ├── 暂停/恢复按钮
│   └── 手动刷新按钮
├── Main Content Grid
│   ├── Left Column
│   │   ├── Current Status Card
│   │   │   ├── Response Time
│   │   │   ├── Version
│   │   │   ├── Uptime
│   │   │   └── Error Alert
│   │   └── Route Health Card (routes列表)
│   └── Right Column
│       ├── Threshold Rules (阈值规则展示)
│       └── Recent Checks (历史记录)
```

---

## 3. BlockReasonCard.tsx 实现详情

### 3.1 功能规格

| 功能项 | 规格 | 实现状态 |
|--------|------|---------|
| 拦截结论展示 | gate_decision / blocked_by | ✅ |
| 触发规则展示 | error_code / required_changes | ✅ |
| 证据引用 | evidence_ref / run_id | ✅ |
| 建议修复 | required_changes / suggestedAction | ✅ |
| 紧凑模式 | compact 属性 | ✅ |
| 复制功能 | run_id / evidence_ref | ✅ |

### 3.2 支持的错误码（完整）

#### Permit 错误码 (E001-E007)

| 错误码 | 描述 | 严重性 | 类别 |
|--------|------|--------|------|
| E001 | 无许可证 | critical | governance |
| E002 | 许可证无效 | critical | governance |
| E003 | 签名错误 | critical | security |
| E004 | 许可证过期 | warning | governance |
| E005 | 作用域不匹配 | error | governance |
| E006 | 主体不匹配 | error | governance |
| E007 | 许可证已撤销 | critical | governance |

#### N8N 错误码

| 错误码 | 描述 | 严重性 | 类别 |
|--------|------|--------|------|
| N8N_FORBIDDEN_FIELD_INJECTION | 禁止字段注入 | critical | security |
| N8N_PERMIT_ISSUE_FAILED | 许可证签发失败 | error | system |
| N8N_MEMBERSHIP_DENIED | 会员权限不足 | warning | governance |
| N8N_MISSING_IDENTIFIER | 缺少标识符 | error | validation |
| N8N_INTERNAL_ERROR | 内部错误 | error | system |

#### RAG 错误码

| 错误码 | 描述 | 严重性 | 类别 |
|--------|------|--------|------|
| RAG-AT-TIME-MISSING | at_time 缺失 | error | validation |
| RAG-AT-TIME-DRIFT-FORBIDDEN | at_time 漂移禁止 | error | validation |
| RAG-VALIDATION-ERROR | RAG 验证错误 | error | validation |
| RAG-INTERNAL-ERROR | RAG 内部错误 | error | system |

#### 导入错误码

| 错误码 | 描述 | 严重性 | 类别 |
|--------|------|--------|------|
| CONSTITUTION_GATE_FAILED | 宪章门失败 | error | governance |
| SYSTEM_AUDIT_FAILED | 系统审计失败 | error | governance |
| IMPORT_INTERNAL_ERROR | 导入内部错误 | error | system |

### 3.3 导出接口

```typescript
// Types
export type GateDecision = 'ALLOW' | 'BLOCK' | 'DENY' | 'REQUIRES_CHANGES';
export type PermitErrorCode = 'E001' | 'E002' | 'E003' | 'E004' | 'E005' | 'E006' | 'E007';
export type N8nErrorCode = 'N8N_FORBIDDEN_FIELD_INJECTION' | ...;
export type BlockErrorCode = PermitErrorCode | N8nErrorCode | string;

export interface N8nErrorEnvelope {
  ok: false;
  error_code: string;
  blocked_by: string;
  message: string;
  evidence_ref?: string;
  run_id: string;
  forbidden_field_evidence?: Record<string, unknown> | null;
  required_changes?: string[];
}

export interface BlockReasonCardProps { ... }

// Constants
export const ERROR_CODE_REGISTRY: Record<string, {...}>;

// Components
export function BlockReasonCard(props: BlockReasonCardProps): React.ReactElement;
export function BlockReasonCardFromError(error: N8nErrorEnvelope, options?): React.ReactElement;
```

### 3.4 组件结构

```
BlockReasonCard
├── Header
│   ├── Category Icon
│   ├── Title
│   └── Error Code Badge
├── Body
│   ├── Blocked By (拦截结论)
│   ├── Detailed Message (详细信息)
│   ├── Security Warning (可选)
│   ├── Required Changes (触发规则)
│   ├── Suggested Fix (建议修复)
│   ├── Evidence Trail (证据引用)
│   │   ├── run_id + Copy Button
│   │   └── evidence_ref + Copy Button
│   └── Additional Context (可展开)
```

---

## 4. 约束符合性

| 约束 | 描述 | 状态 |
|------|------|------|
| health 默认 30s 轮询且可配置 | `DEFAULT_POLL_INTERVAL_MS = 30000` | ✅ |
| 红橙绿阈值规则在文档与代码常量 | `HEALTH_THRESHOLDS` 常量 | ✅ |
| BLOCK 场景统一走 BlockReasonCard | 组件设计覆盖所有 BLOCK 场景 | ✅ |
| 不得在各页面散落自定义错误样式 | 使用统一 `l4-card`, `l4-alert` 样式 | ✅ |

---

## 5. 构建验证

### 5.1 TypeScript 编译

HealthPage.tsx 和 BlockReasonCard.tsx 的 TypeScript 编译 **无错误**。

注：项目中存在预先存在的错误（`react-router-dom` 缺失等），这些不是由本次任务引入的。

### 5.2 相关文件

| 文件 | 行数 | 说明 |
|------|------|------|
| HealthPage.tsx | ~450 | 系统健康监控页面 |
| BlockReasonCard.tsx | ~430 | 全局错误拦截组件 |

---

## 6. 使用示例

### 6.1 HealthPage 使用

```tsx
import { HealthPage } from './pages/system/HealthPage';

function App() {
  return (
    <HealthPage
      apiBaseUrl="/api/v1"
      pollIntervalMs={30000}
      maxHistorySize={20}
      onHealthLevelChange={(level) => {
        console.log('Health level changed:', level);
      }}
    />
  );
}
```

### 6.2 BlockReasonCard 使用

```tsx
import { BlockReasonCard, BlockReasonCardFromError } from './components/governance/BlockReasonCard';

// 方式1: 直接使用 props
<BlockReasonCard
  errorCode="E003"
  blockedBy="Signature Verification Failed"
  message="Permit signature verification failed."
  runId="RUN-N8N-001"
  evidenceRef="EV-001"
  suggestedAction="Contact system administrator."
/>

// 方式2: 从 N8nErrorEnvelope 创建
const error: N8nErrorEnvelope = {
  ok: false,
  error_code: 'N8N_FORBIDDEN_FIELD_INJECTION',
  blocked_by: 'Security Gate',
  message: 'Attempted to inject forbidden field.',
  run_id: 'RUN-N8N-002',
  evidence_ref: 'EV-002',
};
{BlockReasonCardFromError(error)}
```

---

## 7. 后续建议

1. **集成路由**: 将 HealthPage 添加到路由配置 `/system/health`
2. **全局错误处理**: 在应用顶层添加错误边界，统一使用 BlockReasonCard
3. **API Mock**: 为开发环境添加 health API mock 数据
4. **测试用例**: 添加单元测试和集成测试

---

## 变更历史

| 版本 | 日期 | 变更描述 |
|------|------|---------|
| v1.0 | 2026-02-21 | 初始版本，完成 HealthPage 和 BlockReasonCard 实现 |
