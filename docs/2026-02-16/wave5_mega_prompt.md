# Wave 5 Mega Prompt — 编排引擎实现填充
# 目标：填充 engine.py / node_runner.py / gate_engine.py 的核心实现逻辑
# 用法：整段复制到 Claude 4.6

---

## 提示词正文（复制以下全部内容）

```text
你是 GM OS SkillForge 的实现工程师。你需要为 3 个已有骨架文件填充实现逻辑。
不要创建新文件，只输出这 3 个文件的完整替换内容。

## 硬约束

1. 不改变任何 class 签名、方法签名、属性名
2. 不添加新的外部依赖（只用 Python 标准库 + 已有 import）
3. 所有 helper 方法（_resolve_path, _build_output, _make_trace_event, _build_decision）已实现，不要修改它们
4. trace_event 的 event_type 必须是 trace_event.schema.json 中定义的枚举值：start, tool_call, llm_call, error, complete, checkpoint
5. gate_decision 的 decision 必须是：ALLOW, DENY, REQUIRES_CHANGES
6. 错误码只能使用 error_codes.yml 中定义的（前缀：GATE_, AUDIT_, REG_, EXEC_, SCHEMA_, SYS_）
7. 所有方法必须保留完整的 docstring
8. 保留已有的 from __future__ import annotations
9. 同时输出每个文件对应的 Skill Spec 更新（如果实现细节与 Spec 有偏差）

## 文件 1：engine.py

路径：skillforge/src/orchestration/engine.py

### 已实现的部分（不要修改）
- PATH_A, PATH_B, PATH_AB 列表
- GATE_NODES 集合
- PipelineEngine 的 register_node() 方法
- _resolve_path() 方法
- _build_output() 方法

### 需要填充：PipelineEngine.run() 方法

行为要求：
1. 生成 job_id = str(uuid.uuid4())
2. 记录 start_time
3. 验证 input_data：
   - mode 必须是 "nl" / "github" / "auto"
   - mode="nl" 时 natural_language 不能为空
   - mode="github" 时 repo_url 不能为空
   - mode="auto" 时 natural_language 不能为空
   - 验证失败返回 status="failed" + error
4. 调用 _resolve_path(mode) 获取 path_label 和 node_ids
5. 初始化 artifacts: dict[str, Any] = {"input": input_data}
6. 遍历 node_ids：
   a. 检查 node_id 是否在 node_registry 中，不在则 error
   b. 如果 node_id 在 GATE_NODES 中且有 gate_evaluator：
      - 调用 gate_evaluator.evaluate(node_id, artifacts)
      - 将 gate_decision 加入 gate_decisions 列表
      - 如果 decision == "DENY"：终止，返回 status="gate_denied"
      - 如果 decision == "REQUIRES_CHANGES"：终止，返回 status="failed" + error
   c. 否则（普通节点）：
      - 调用 handler.validate_input(input_data_for_node)（input_data_for_node 是 artifacts 的当前快照）
      - 如果验证失败：返回 status="failed"
      - 调用 handler.execute(artifacts)
      - 调用 handler.validate_output(result)
      - 将 result 存入 artifacts[node_id]
   d. stages_completed += 1
   e. 产出 trace_event (type="complete" for each stage)
7. 如果是最后一个节点 (pack_audit_and_publish)，从 artifacts 中取出 audit_pack_path 和 publish_result
8. 计算 duration_ms = int((time.time() - start_time) * 1000)
9. 用 _build_output() 组装返回值
10. 整个 run() 包在 try/except 中捕获异常，返回 status="failed"

### 额外要求
- run() 的异常处理中，用 _make_trace_event 可以不有（engine 自己不产 trace），但要把各 node 产出的 trace 收集起来放到 output.trace_events 中
- 实际上 engine 委托给 NodeRunner 更好，但这里简化为直接调用 handler

## 文件 2：node_runner.py

路径：skillforge/src/orchestration/node_runner.py

### 已实现的部分（不要修改）
- NodeRunner 的属性定义（default_timeout_seconds, max_retries, retry_delay_seconds）
- _make_trace_event() 方法

### 需要填充：NodeRunner.run() 方法

行为要求：
1. 解析 timeout 和 max_retries（传入值优先，否则用默认值）
2. 产出一个 trace_event: event_type="start"
3. 调用 handler.validate_input(input_data)
   - 如果有错误：raise ValueError 并产出 event_type="error" trace
4. 重试循环（最多 max_retries 次）：
   a. 记录开始时间
   b. 用 threading 或 signal 做超时控制（简化版：不用真的做 signal，用时间检测即可）
   c. 调用 handler.execute(input_data)
   d. 成功则 break
   e. 捕获异常，retries_used += 1
   f. 如果还有重试次数：time.sleep(retry_delay_seconds * 2^retries_used)
   g. 如果重试耗尽：raise RuntimeError
5. 调用 handler.validate_output(output)
   - 如果有错误：raise RuntimeError 并产出 event_type="error" trace
6. 产出 event_type="complete" trace，包含 duration_ms
7. 返回 {"node_id": ..., "output": ..., "trace_events": [...], "duration_ms": ..., "retries_used": ...}

## 文件 3：gate_engine.py

路径：skillforge/src/orchestration/gate_engine.py

### 已实现的部分（不要修改）
- GateEngine 的 schema_version 属性
- _build_decision() 方法

### 需要填充：GateEngine.evaluate() 方法

行为要求：
1. 生成 gate_id = f"gate-{uuid.uuid4()}"
2. 根据 node_id 分发到不同的评估逻辑：
   - "license_gate"：
     a. 检查 artifacts 中是否有 "provenance" 或 "build_record"
     b. 检查 license 是否在白名单中：["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "0BSD", "Unlicense"]
     c. 如果 license 未知或不在白名单：DENY + 原因
     d. 否则 ALLOW
   - "constitution_risk_gate"：
     a. 检查 artifacts 中是否有 skill_spec 或 draft_spec
     b. 检查 capabilities：
        - 如果 network=true 且 sandbox_mode="strict"：DENY
        - 如果 subprocess=true 且 risk_tier > L1：REQUIRES_CHANGES
     c. 检查 risk_tier 是否合理（L0-L3）
     d. 如果有 capabilities 声明且不超限：ALLOW
   - 其他 node_id：默认 ALLOW（带 warning 说明这个 gate 没有专用评估逻辑）
3. 用 _build_decision() 组装返回值
4. 整个方法包在 try/except 中，异常时返回 DENY + 异常信息

## 输出格式

请按以下格式输出每个文件：

### 文件: [相对路径]

```python
[完整文件内容，包括所有 import、class 定义、已有方法和新填充方法]
```

### Skill Spec 更新: [相对路径]（仅在有变化时输出）

```yaml
[只输出需要变更的字段，不需要输出完整 Spec]
```

一共 3 个代码文件 + 可能的 Spec 更新。请完整输出。
```

---

## 交付后验收标准

```bash
cd D:\GM-SkillForge\skillforge-spec-pack

# 1. 现有测试不退化
pytest -q                          # >= 39 passed

# 2. protocol 测试不退化
pytest skillforge/tests/test_protocols.py -v   # 116 passed

# 3. engine.run() 不再抛 NotImplementedError
python -c "
from skillforge.src.orchestration.engine import PipelineEngine
e = PipelineEngine()
result = e.run({'mode': 'github', 'repo_url': 'https://github.com/example/repo'})
print(f'status={result[\"status\"]}')
# 预期: status=failed (因为没注册 node)
"

# 4. node_runner.run() 不再抛 NotImplementedError
python -c "
from skillforge.src.orchestration.node_runner import NodeRunner
from skillforge.src.nodes.intake_repo import IntakeRepo
nr = NodeRunner()
try:
    nr.run(IntakeRepo(), {'repo_url': 'test'})
except NotImplementedError:
    print('FAIL: node handler still NotImplementedError (expected)')
except (ValueError, RuntimeError) as e:
    print(f'OK: {type(e).__name__}: {e}')
"

# 5. gate_engine.evaluate() 不再抛 NotImplementedError
python -c "
from skillforge.src.orchestration.gate_engine import GateEngine
ge = GateEngine()
result = ge.evaluate('license_gate', {'provenance': {'license': 'MIT'}})
print(f'decision={result[\"decision\"]}')
# 预期: decision=ALLOW
"

# 6. validate.py 不退化
python tools/validate.py --all
```
