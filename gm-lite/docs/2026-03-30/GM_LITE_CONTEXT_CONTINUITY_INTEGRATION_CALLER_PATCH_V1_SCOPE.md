# GM_LITE_CONTEXT_CONTINUITY_INTEGRATION_CALLER_PATCH_V1_SCOPE

## task_line_id
- `gm_lite_context_continuity_integration_caller_patch_v1`

## trigger
- `CI3` 执行与审查确认：
  - 协议层完整
  - 运行时层完整
  - 集成层断开
  - 回写后仍需手工重建核心上下文

## problem_statement
- `CC3` 已提供上下文恢复与受控状态转换能力。
- 当前缺的不是协议对象或运行时方法，而是：
  - VS Code 扩展主链没有稳定调用这些能力
  - writeback / followback / console 返回链没有自动吃到恢复结果
  - 连续协作链因此在“回写后继续对话”处断开

## objective
- 为 `CI3` 补一条独立的集成调用修复线：
  - 让上下文恢复真正服务于连续协作链
  - 让回写后不再需要手工重建核心上下文
  - 让 `CI3` 后续重入时评估的是“是否打通调用链”，而不是再次发现“无人负责集成层”

## in_scope
- Console / Workbench 对上下文恢复能力的调用接线
- writeback / followback / active task 返回链的上下文绑定
- 受控状态转换在扩展主链中的触发点补齐
- 面向 `CI3` / `OR1` 的最小可验证连续性证据

## out_of_scope
- 新协议对象设计
- 新 runtime 方法设计
- 重调度中心 / 重 watcher / heavy scheduler
- AI legion 能力模型扩张

## success_condition
- `CI3` 后续重入时不再因“集成层断开”失败
- writeback 后能自动恢复核心上下文，而不是要求人工重新建立
- 连续协作链在“回写 -> 继续对话/继续工作面”处有明确证据
