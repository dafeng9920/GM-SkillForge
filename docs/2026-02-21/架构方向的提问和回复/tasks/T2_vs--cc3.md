```yaml
# 元信息
task_id: "T2"
executor: "vs--cc3"
wave: "Wave 1"
depends_on: []
estimated_minutes: 60

# 输入合同 (Input Contract)
input:
  description: "M1 Permit 签名强制闭环：替换 mock 放行，实现 HS256 强验证和 Fail-Closed 兜底"
  context_files:
    - path: "skillforge/src/skills/gates/gate_permit.py"
      purpose: "修改 _stub_signature_verifier 为严格逻辑"
    - path: "skillforge/tests/test_gate_permit.py"
      purpose: "更新测试以支持带密钥的真实 HMAC 计算，剔除旧 fixture 放行"
  constants:
    env_keys: ["PERMIT_HS256_KEY"]

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "skillforge/src/skills/gates/gate_permit.py"
      type: "修改"
    - path: "skillforge/tests/test_gate_permit.py"
      type: "修改"
  constraints:
    - "gate_permit 遇到非 HS256 或无 Key 必须返回 False（进而输出 E003 BLOCK），不得抛 500 异常"
    - "测试代码必须包含针对：无Key、错误Key（坏签名）、未知算法 的三个阻塞测试用例"
    - "【零例外治理】: 默认拒绝。任何不确定、缺配置、验签失败，一律 BLOCK，绝对不接受'临时放行'。"
    - "【零例外治理】: 变更必可回滚。测试未全绿、无回滚兜底不允许通过。"

# 红线 (Deny List)
deny:
  - "不得引入如 PyJWT 等新依赖，直接用 hmac 库实现即可"
  - "禁止在测试中把全局环境变量写死，应该用 mock 或依赖注入（比如传 _signature_verifier）"
  - "禁止隐性后门：发现 fallback、兼容性放行、为了跑通老测试而特判放行的逻辑，将直接打回重做。"

# 质量门禁 (Gate Check)
gate:
  auto_checks:
    - command: "pytest skillforge/tests/test_gate_permit.py -v"
      expect: "passed"
    - command: "pytest -q"
      expect: "系统测试全绿"
```
