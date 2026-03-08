# 3-Day Compliance Review

建议至少每 3 天运行一次规范回溯审查（当前已接入 CI 每天自动执行一次）：

```powershell
python scripts/run_3day_compliance_review.py --run-tests
```

说明：
- 默认输出报告到 `docs/compliance_reviews/`
- 生成：
  - `review_YYYY-MM-DD.md`
  - `review_YYYY-MM-DD.json`
  - 每次运行归档：`runs/YYYY-MM-DD/HHMMSSZ/review.md|review.json`
- 若存在 `CRITICAL/HIGH` 失败项，脚本返回非零退出码（用于 CI/门禁）

可选参数：
- `--max-gap-days 3`：允许的最大审查间隔天数
- `--allow-fail`：仅用于本地观察，不建议用于 CI

建议制度：
- 审查窗口固定 30-45 分钟
- 失败项必须形成 RequiredChanges 并在下一窗口前闭环

CI 自动巡查：
- Workflow: `.github/workflows/compliance-daily.yml`
- 频率: 每天 `03:00 UTC`（也支持手动触发）
