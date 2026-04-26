# GM_LITE_CONTEXT_CONTINUITY_INTEGRATION_CALLER_PATCH_V1_TASK_BOARD

## phase_order
- 第一波并行：`IC1 + IC2`
- 第二波串行：`IC3`
- 第三波串行：`IC4`
- 完成后：强制回到 `CI3` 重入

## tasks

### IC1
- file: `tasks/IC1_console_and_writeback_context_restore_call_path.md`
- review: `tasks/IC1_review.md`
- compliance: `tasks/IC1_compliance.md`
- focus:
  - Console / writeback 路径真正调用上下文恢复能力
  - latest writeback / latest active task 返回时自动带回核心上下文

### IC2
- file: `tasks/IC2_followback_active_surface_context_binding_patch.md`
- review: `tasks/IC2_review.md`
- compliance: `tasks/IC2_compliance.md`
- focus:
  - followback / active surface 绑定 intent trace / task context
  - 减少“看到了结果，但上下文没回到当前工作面”的断裂

### IC3
- file: `tasks/IC3_controlled_transition_trigger_in_extension_chain.md`
- review: `tasks/IC3_review.md`
- compliance: `tasks/IC3_compliance.md`
- focus:
  - 扩展主链中的受控状态转换触发点
  - 回写后的状态推进与恢复不能停留在方法存在层

### IC4
- file: `tasks/IC4_patch_summary_and_ci3_reentry_rule.md`
- review: `tasks/IC4_review.md`
- compliance: `tasks/IC4_compliance.md`
- focus:
  - 说明这次补的是“集成调用责任”
  - 锁定 `CI3` 重入必须检查的证据
