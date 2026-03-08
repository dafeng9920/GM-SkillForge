# Profiles

## dispatch

用途：输出当前可启动任务与可转发提示词。

输入：
- date
- dispatch path
- prompts path

输出：
- next task
- owner
- dependency check
- forward prompt section

## validate

用途：校验调度包结构与注册映射。

检查：
- 任务实名绑定
- 任务与提示词一一对应
- final gate 输出路径存在
- dispatch registry 完整（含 governance-orchestrator-skill）

## reconcile

用途：当 `T98/T99`、`review/compliance` 发生冲突时，生成最小返工链。

输出：
- blocking evidence
- minimum rework list
- rerun sequence

## final_gate

用途：对批次进行最终裁决。

规则：
1. 缺三权证据 => DENY
2. 任一 compliance 非 PASS => REQUIRES_CHANGES
3. 依赖链不闭合 => REQUIRES_CHANGES
4. 全部满足 => ALLOW

