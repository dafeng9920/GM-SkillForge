# SkillForge UI 状态机

> 版本: 0.1.0

## 概述

基于 error_code + next_action 渲染的 UI 状态机定义。

## 状态映射

### 按 Node ID + Error Code

| Node | Error Code | UI 状态 | 用户操作 |
|------|------------|---------|----------|
| intake_repo | SYS_DEPENDENCY_FAILURE | `error-retry` | 显示"重试访问"按钮 |
| intake_repo | SYS_INTERNAL | `error-system` | 显示"稍后重试"提示 |
| license_gate | AUDIT_LICENSE_UNKNOWN | `warning-license` | 显示"添加许可证"引导 |
| license_gate | AUDIT_PROVENANCE_INCOMPLETE | `error-provenance` | 显示"补充溯源"表单 |
| constitution_risk_gate | GATE_POLICY_DENY | `blocked-policy` | 显示拒绝原因和解锁路径 |
| constitution_risk_gate | GATE_REQUIRES_CHANGES | `warning-changes` | 显示 required_changes 列表 |
| sandbox_test_and_trace | EXEC_TIMEOUT | `error-timeout` | 显示"重试"或"增加超时"选项 |
| sandbox_test_and_trace | EXEC_TEST_INSUFFICIENT_RUNS | `warning-runs` | 显示当前运行次数和目标 |
| sandbox_test_and_trace | EXEC_METRICS_THRESHOLD_FAILED | `error-metrics` | 显示指标对比图表 |
| pack_audit_and_publish | REG_PUBLISH_VISIBILITY_DENIED | `blocked-visibility` | 显示"改为私有发布"选项 |

## 状态机图

```
                    ┌─────────────┐
                    │   IDLE      │
                    └──────┬──────┘
                           │ start
                           ▼
                    ┌─────────────┐
              ┌─────│  RUNNING    │─────┐
              │     └─────────────┘     │
              │            │            │
         node_error   node_success  system_error
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  RETRY   │ │ CONTINUE │ │  FAILED  │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │            │            │
             │            │            │
             └────────────┴────────────┘
                          │
                     pipeline_end
                          │
                          ▼
                   ┌─────────────┐
                   │  COMPLETED  │
                   └─────────────┘
```

## UI 组件映射

### error-retry
```tsx
<ErrorState
  icon="retry"
  title="访问失败"
  message={user_message_template}
  actions={[
    { id: "retry", label: "重试", primary: true },
    { id: "config", label: "检查配置" }
  ]}
/>
```

### warning-license
```tsx
<WarningState
  icon="license"
  title="许可证未知"
  message="未能识别许可证，将限制为私有使用"
  actions={[
    { id: "add_license", label: "添加许可证", primary: true },
    { id: "continue_private", label: "继续（私有）" }
  ]}
  hints={patch_hints}
/>
```

### blocked-policy
```tsx
<BlockedState
  icon="blocked"
  title="策略拒绝"
  message={gate_decision.reasons}
  requiredChanges={required_changes}
  unlockPath={patch_hints}
/>
```

## next_action_id 命名规范

格式: `<node>.<verb>.<object>`

示例:
- `intake_repo.retry.access` - 重试访问仓库
- `license_gate.add.license` - 添加许可证
- `sandbox.add.runs` - 增加测试运行次数
- `publish.change.visibility` - 修改发布可见性

## 错误码到 UI 的映射表

完整映射见 `orchestration/error_policy.yml`，前端通过以下方式获取：

```typescript
interface ErrorAction {
  error_code: string;
  user_message_template: string;
  next_action: {
    action_id: string;
    title: string;
    suggested_fixes: Array<{
      kind: string;
      description: string;
    }>;
  };
}

function getUIState(nodeId: string, errorCode: string): ErrorAction {
  // 从 error_policy.yml 加载
  return errorPolicy[nodeId].on_error.find(e => e.error_code === errorCode);
}
```

## 国际化支持

`user_message_template` 和 `title` 支持参数替换：

```
"测试运行次数不足: {current}/{minimum}"
```

前端负责注入实际值：
```typescript
message.replace('{current}', current).replace('{minimum}', minimum);
```
