# p1-closing-freeze-skill

> 版本: v0.1.0  
> 适用阶段: P1 收口冻结 / L4 基础能力收口

---

## 触发词

- `P1 冻结校验`
- `closing freeze 验收`
- `closing_pack_index 检查`
- `P1 freeze gate`

---

## 输入

```yaml
input:
  date: string                         # 默认 2026-02-22
  verify_dir: string                   # 默认 docs/2026-02-22/verification
  require_allow: bool                  # 默认 true，要求 final_gate_decision_p1=ALLOW
  require_hash_filled: bool            # 默认 true，要求 closing_pack_index sha256 全部已填
  output_mode: string                  # text | json，默认 text
```

---

## 步骤

1. 检查以下关键文件存在性：
   - `P1_CLOSING_FREEZE.md`
   - `closing_pack_index.json`
   - `final_gate_decision_p1.json`
2. 读取 `closing_pack_index.json`：
   - 校验 `approval` 字段完整（reviewer/compliance_officer/approved_at/note）。
   - 校验 `integrity_checks` 为 `true`（若启用）。
   - 校验 `artifacts[*].sha256` 非 `[TO_FILL]`（若启用）。
3. 读取 `final_gate_decision_p1.json`：
   - 若 `require_allow=true`，要求 `decision=ALLOW`。
4. 生成结论：
   - `ALLOW`：全部检查通过
   - `REQUIRES_CHANGES`：存在缺失项或不一致
5. 输出证据：
   - 缺失字段列表
   - 关键文件定位
   - 建议修复动作

---

## DoD

- 冻结包关键文件存在且可解析。  
- `closing_pack_index.json` 中审批信息完整。  
- `artifacts` 哈希无占位符。  
- `final_gate_decision_p1.json` 满足决策要求。  
- 输出明确 `ALLOW/REQUIRES_CHANGES` 和 `required_changes`。  

---

## 执行命令

```powershell
python skills/p1-closing-freeze-skill/scripts/p1_closing_freeze_check.py --verify-dir docs/2026-02-22/verification --require-allow
```

---

## 失败处理

| 场景 | 处理 |
|---|---|
| 审批字段缺失 | 标记 `REQUIRES_CHANGES`，补齐 approval 字段 |
| sha256 仍为占位符 | 标记 `REQUIRES_CHANGES`，重新计算并写回 |
| 最终决策非 ALLOW | 标记 `REQUIRES_CHANGES`，先完成上游回执修复 |
| 文件缺失/解析失败 | 标记 `REQUIRES_CHANGES`，列出缺失路径与修复建议 |

