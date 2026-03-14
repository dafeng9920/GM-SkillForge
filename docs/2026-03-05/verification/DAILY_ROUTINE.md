# Fixed-Caliber 每日执行参考

## 目录结构说明

```
docs/
├── 2026-03-04/verification/
│   └── Fixed-Caliber_Exit_Criteria_Checklist_2026-03-04.md  # 主门槛检查表 (持续维护)
│
├── 2026-03-05/verification/
│   ├── PROGRESS_REPORT_2026-03-05.md                          # 当日进度报告
│   └── DAILY_ROUTINE.md                                       # 本文件
│
├── 2026-03-06/verification/
│   └── (当日进度记录)
│
└── ...
```

**规则**:
- 主检查表固定在 `2026-03-04/` 目录
- 每日进度记录写入对应日期目录
- Nightly recheck 结果写入 `2026-03-04/verification/` (保持集中)

## 环境设置

```bash
# 进入项目目录
cd d:/GM-SkillForge

# 设置日期 (Windows PowerShell)
$today = Get-Date -Format "yyyy-MM-dd"
```

## 每日任务

### 1. Nightly Recheck (必须)

```powershell
# PowerShell 设置日期
$today = Get-Date -Format "yyyy-MM-dd"

# 运行 nightly recheck
python scripts/antigravity_nightly_recheck.py --date $today

# 如果检测到 drift，使用 --update-permit 更新
python scripts/antigravity_nightly_recheck.py --date $today --update-permit
```

### 2. 检查结果

```powershell
# 查看报告
Get-Content "docs\2026-03-04\verification\ANTIGRAVITY-1-NIGHTLY-RECHECK-$today.json"
```

### 3. 更新检查表

编辑主检查表：
```
docs/2026-03-04/verification/Fixed-Caliber_Exit_Criteria_Checklist_2026-03-04.md
```
更新 G1 进度（累计天数）。

### 4. 创建当日进度记录（可选）

在对应日期目录创建每日进度记录：
```
docs/2026-03-05/verification/
docs/2026-03-06/verification/
...
```

## 进度跟踪

| 日期 | 状态 | 备注 |
|------|------|------|
| 2026-03-05 | ✅ PASS | 第1天，0 drift |
| 2026-03-06 | ⏳ 待执行 | |
| 2026-03-07 | ⏳ 待执行 | |
| 2026-03-08 | ⏳ 待执行 | |
| 2026-03-09 | ⏳ 待执行 | |
| 2026-03-10 | ⏳ 待执行 | |
| 2026-03-11 | ⏳ 待执行 | |
| 2026-03-12 | ⏳ 待执行 | |
| 2026-03-13 | ⏳ 待执行 | |
| 2026-03-14 | ⏳ 待执行 | |
| 2026-03-15 | ⏳ 待执行 | |
| 2026-03-16 | ⏳ 待执行 | |
| 2026-03-17 | ⏳ 待执行 | |
| 2026-03-18 | ⏳ 待执行 | |

## 完成条件

- ✅ 连续 14 天 nightly recheck 全部 PASS
- ✅ 0 drift (无哈希漂移)

## 完成后操作

当 G1 达成后：

1. 生成 Final Closure Report
2. 签发 CLOSE 决策
3. 转入维护模式 (每周巡检)

---

*创建时间: 2026-03-05*
*执行环境: LOCAL-ANTIGRAVITY*
