# Cloud Minimal Joint Test Report

- Date: `2026-03-08`
- Test ID: `SMOKE-GATE-001`
- Scope: `verify_governance_env.sh + pre_absorb_check.sh`
- Verdict: `PASS`

## 1. verify_governance_env.sh 结果

- APP_ROOT: `/root/openclaw-box/skillforge`
- DROPZONE_ROOT: `/root/openclaw-box/dropzone`
- DOCS_ROOT: `/root/openclaw-box/docs`
- 首次结果: `FAIL`
- 失败原因: `APP_ROOT 不存在`
- 修复动作: 创建 `/root/openclaw-box/skillforge`
- 重跑结果: `PASS`

## 2. 测试任务包实际路径

- `/root/openclaw-box/dropzone/SMOKE-GATE-001`

## 3. manifest.json 内容摘要

- task_id: `SMOKE-GATE-001`
- artifacts:
  - `blueprint.md`
  - `risk_statement.md`
  - `changes.diff`
  - `test_report.md`
  - `completion_record.md`
  - `manifest.json`
- evidence:
  - `logs/execution.log`
  - `evidence/checkpoint.txt`
- env:
  - `APP_ROOT=/root/openclaw-box/skillforge`
  - `DROPZONE_ROOT=/root/openclaw-box/dropzone`
  - `DOCS_ROOT=/root/openclaw-box/docs`

## 4. pre_absorb_check.sh 结果

- Command: `bash /root/openclaw-box/scripts/pre_absorb_check.sh SMOKE-GATE-001`
- Result: `PASS`
- 检查覆盖:
  - 环境变量校验
  - 路径安全
  - manifest 白名单路径存在性
  - 关键件完整性

## 5. 结论

- 本次仅做最小联调验证
- 未执行真实业务 absorb
- 未修改真实业务代码
- 当前可定性为：`治理底盘已安装并通过最小联调`

## 6. 后续动作

1. 修正脚本默认 `APP_ROOT` 为云端真实工作根
2. 冻结 `SMOKE-GATE-001` 结果，作为后续云端业务执行底盘验证依据
3. 转入首个真实受控业务任务
