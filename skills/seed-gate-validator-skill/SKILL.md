# seed-gate-validator-skill

> 版本: v0.1.0  
> 适用阶段: L4.5 / SEEDS P0-P2

---

## 触发词

- `跑 gate 校验`
- `strict 验证`
- `SEEDS 校验`
- `validate_seeds_p0_p1`
- `验收前复核`

---

## 输入

```yaml
input:
  strict: bool                    # 默认 true
  base_path: string               # 默认仓库根目录
  pytest_basetemp: string         # 建议 D:\GM-SkillForge\.tmp\pytest
  output_mode: string             # text | json
  report_path: string             # 可选，落盘报告路径
```

---

## 步骤

1. 检查 `scripts/validate_seeds_p0_p1.py`、P0/P1 seed 文件是否存在。  
2. 注入 `PYTEST_ADDOPTS=--basetemp <pytest_basetemp>`，规避 Windows temp 权限漂移。  
3. 执行 `python scripts/validate_seeds_p0_p1.py --strict`。  
4. 解析输出中的 `Total/Passed/Failed/Overall` 与各 suite 结果。  
5. 生成结论：`ALLOW` 或 `BLOCK`，并输出证据命令与关键信息。  

---

## DoD

- `--strict` 返回码为 `0`。  
- 所有 suite 为 `passed`，无 `error`。  
- 输出中明确记录了 `PYTEST_ADDOPTS` 生效值。  
- 产出可复制的审计摘要（命令、时间、结果、结论）。  

---

## 失败处理

| 场景 | 处理 |
|---|---|
| pytest temp 权限错误 | 强制设置 `PYTEST_ADDOPTS=--basetemp ...` 后重跑 |
| 单测失败 | 标记 `BLOCK`，附失败 suite 与日志摘要 |
| seed 文件缺失 | 标记 `BLOCK`，列缺失路径与修复建议 |
| 脚本超时 | 标记 `BLOCK`，建议拆分 suite 定位 |

