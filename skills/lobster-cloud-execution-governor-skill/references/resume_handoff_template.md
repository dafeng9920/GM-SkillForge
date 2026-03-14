# Resume Handoff Template

```yaml
task_id: "m2-feature-20260307-001"
generated_at: "2026-03-07T22:30:00Z"
executor: "cloud-lobster"
contract_ref: ".tmp/openclaw-dispatch/m2-feature-20260307-001/task_contract.json"
status: "READY_TO_RESUME"

objective: "按冻结合同完成编码开发与测试"
last_completed_step: "edited_service_and_added_partial_tests"

changed_files:
  - "skillforge/src/example_service.py"
  - "skillforge/tests/test_example_service.py"

executed_commands:
  - "pytest skillforge/tests/test_example_service.py -q"

command_results:
  - command: "pytest skillforge/tests/test_example_service.py -q"
    summary: "2 passed, 1 failed"

remaining_work:
  - "修复 test_example_service.py 中最后一个失败断言"
  - "重新跑 pytest"
  - "更新 execution_receipt.json"

blocked_by:
  - "token_budget_warning"

checkpoint_refs:
  - ".tmp/openclaw-dispatch/m2-feature-20260307-001/checkpoint/state.yaml"
  - ".tmp/openclaw-dispatch/m2-feature-20260307-001/execution_receipt.json"

resume_entrypoint: >
  先读取 task_contract.json、当前 handoff、execution_receipt.json，
  再打开 skillforge/tests/test_example_service.py 修复最后一个失败断言，
  然后运行 pytest skillforge/tests/test_example_service.py -q。

do_not_do:
  - "不得新增合同外文件"
  - "不得扩大任务范围"
  - "不得写 review/compliance 结论"
  - "不得签 permit 或 final gate"

review_boundary:
  reviewer_required: true
  compliance_required: true
  publish_decision_required: true

notes:
  - "本轮因 token 接近上限而暂停，不是任务完成。"
  - "续跑时只信落盘证据，不信聊天记忆。"
```
