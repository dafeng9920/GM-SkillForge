---
name: wave-recheck-generator-skill
description: 自动生成 Wave 重校对结果（JSON+MD），用于 API 故障后衔接恢复与放行判断。
---

# wave-recheck-generator-skill

## 触发条件

- 出现 API428/同步异常
- 任务状态与落盘记录不一致
- 需要快速重建可转发校对结论

## 输入

```yaml
input:
  job_id: "P0-L6-AUTH-YYYYMMDD-XXX"
  verification_dir: "docs/{date}/p0-governed-execution/verification"
  wave: "Wave2|Wave3|Wave4"
  prerequisites:
    - "previous_wave_all_allow"
```

## 输出

```yaml
output:
  recheck_json: "verification/Wave{N}_recheck_after_api428.json"
  recheck_md: "verification/Wave{N}_recheck_after_api428.md"
  decision: "ALLOW | REQUIRES_CHANGES | DENY"
```

## DoD

- [ ] JSON 与 MD 同步输出
- [ ] 阻断原因可定位到任务号
- [ ] 含可执行的纠偏动作列表

