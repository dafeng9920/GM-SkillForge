# P1 演示链路闭环指南

> **目标**: 5分钟内复现完整审计流程：命令执行 -> 产物生成 -> 前端查看
> **Job ID**: L4-P1-FOUNDATION-20260222-002
> **Scope**: P1-3
> **Created**: 2026-02-22

---

## 1. 前置依赖

| 依赖项 | 状态 | 说明 |
|--------|------|------|
| T60 | ✅ 完成 | 前端审计页面 MVP (SkillAuditPage.tsx) |
| T61 | ✅ 完成 | 契约校验与前端校验提示 |
| Python 3.9+ | 必需 | 运行审计脚本 |
| Node.js 18+ | 必需 | 运行前端开发服务器 |
| Git 仓库 | 必需 | `git-Claude仓库/knowledge-work-plugins` 技能源数据 |

### 环境检查
```bash
# 检查 Python
python --version  # 预期: Python 3.9.x 或更高

# 检查 Node.js
node --version    # 预期: v18.x 或更高
```

---

## 2. 步骤 1：运行审计命令 (约 30 秒)

```bash
# 从项目根目录执行
python scripts/skillforge_audit.py audit run \
  --profile l5-static \
  --domains finance,legal \
  --top-n 3
```

### 预期输出
```
[audit] run_id=L5S-20260222065429Z-XXXXXXXX
[audit] evidence_ref=EV-L5S-L5S-20260222065429Z-XXXXXXXX
[audit] profile=l5-static
[audit] policy_version=v1.0.0-20260222
[audit] input_hash=xxxxxxxxxxxx...
[audit] result_hash=xxxxxxxxxxxx...
[audit] report_json=.../reports/skill-audit/finance_legal_top3_l5-static_2026-02-22.json
[audit] report_md=.../reports/skill-audit/finance_legal_top3_l5-static_2026-02-22.md
[audit] run_dir=.../reports/skill-audit/runs/L5S-20260222065429Z-XXXXXXXX
[audit] gate_counts: PASS=3 WARN=0 FAIL=0
```

### 退出码
- `0`: 成功
- `1`: 失败（见排错提示）

---

## 3. 步骤 2：验证产物 (约 30 秒)

### 产物列表
| 产物 | 路径 | 说明 |
|------|------|------|
| JSON 报告 | `reports/skill-audit/finance_legal_top3_l5-static_2026-02-22.json` | 完整审计结果 |
| Markdown 报告 | `reports/skill-audit/finance_legal_top3_l5-static_2026-02-22.md` | 可读格式报告 |
| Run 元数据 | `reports/skill-audit/runs/<run_id>/run_meta.json` | 运行元信息 |
| Run JSON | `reports/skill-audit/runs/<run_id>/report.json` | 运行副本 |
| Run MD | `reports/skill-audit/runs/<run_id>/report.md` | 运行副本 |

### 验证命令
```bash
# 检查 JSON 报告
cat reports/skill-audit/finance_legal_top3_l5-static_2026-02-22.json | python -m json.tool | head -30

# 检查 Markdown 报告
head -50 reports/skill-audit/finance_legal_top3_l5-static_2026-02-22.md
```

### 预期 JSON 结构
```json
{
  "summary": {
    "run_date": "2026-02-22",
    "run_id": "L5S-...",
    "sample_size": 3,
    "gate_counts": { "PASS": 3, "WARN": 0, "FAIL": 0 },
    "avg_overall_score": 75.3,
    ...
  },
  "results": [
    {
      "domain": "finance",
      "skill": "audit-support",
      "overall_score": 74.0,
      "gate": "PASS",
      "layer_scores": { "L1_cost": 40, "L2_redundancy": 100, ... },
      ...
    },
    ...
  ]
}
```

---

## 4. 步骤 3：启动前端查看 (约 2 分钟)

### 启动开发服务器
```bash
# 进入前端目录
cd ui/app

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

### 预期输出
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

### 访问审计页面
1. 打开浏览器，访问: `http://localhost:5173/`
2. 导航至: `/audit/skill-audit`
3. 或直接访问: `http://localhost:5173/audit/skill-audit`

### 前端页面功能检查
| 功能 | 检查方式 |
|------|----------|
| 总览卡 | 显示 run_date, sample_size, gate_counts |
| 明细表 | 显示 3 条审计结果 |
| 排序功能 | 点击列头 (Domain/Skill/Score/Gate/Tokens) |
| 详情面板 | 点击表格行，右侧显示详情 |
| 结论限制区 | 底部显示 policy_version, policy_path |

---

## 5. 步骤 4：契约校验测试 (约 1 分钟)

### 测试坏数据校验
```bash
# 备份原始 JSON
cp reports/skill-audit/finance_legal_top3_l5-static_2026-02-22.json \
   reports/skill-audit/finance_legal_top3_l5-static_2026-02-22.json.bak

# 构造坏数据：删除 summary 字段
cat reports/skill-audit/finance_legal_top3_l5-static_2026-02-22.json | \
  python -c "import sys,json; d=json.load(sys.stdin); del d['summary']; print(json.dumps(d))" \
  > /tmp/bad.json && mv /tmp/bad.json reports/skill-audit/finance_legal_top3_l5-static_2026-02-22.json
```

### 预期前端行为
刷新页面后，显示错误信息：
```
加载失败: 数据格式错误: summary - 缺少必需字段 summary
```

### 恢复正常数据
```bash
mv reports/skill-audit/finance_legal_top3_l5-static_2026-02-22.json.bak \
   reports/skill-audit/finance_legal_top3_l5-static_2026-02-22.json
```

---

## 6. 失败分支排错

### 问题 1: 审计命令失败
| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `No domains specified` | 未指定 --domains | 添加 `--domains finance,legal` |
| `No skills found` | 技能目录不存在或为空 | 检查 `git-Claude仓库/knowledge-work-plugins` 路径 |
| `policy file not found` | 策略文件缺失 | 检查 `configs/audit_policy_v1.json` |
| `ModuleNotFoundError` | Python 依赖缺失 | 运行 `pip install -r requirements.txt` |

### 问题 2: 前端无法加载报告
| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `加载失败: 无法加载审计报告` | JSON 文件不存在 | 先运行审计命令生成报告 |
| `数据格式错误: ...` | JSON 不符合 schema | 检查 JSON 完整性，恢复备份 |
| 页面空白 | 路由未配置 | 检查 `router.tsx` 中 `/audit/skill-audit` 路由 |

### 问题 3: 前端构建失败
| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `npm ERR!` | 依赖未安装 | 运行 `npm install` |
| `TypeScript error` | 类型定义缺失 | 检查 `@types/*` 依赖 |
| `Vite error` | 配置问题 | 检查 `vite.config.ts` |

### 调试命令
```bash
# 检查 audit 命令详细输出
python scripts/skillforge_audit.py audit run --profile l5-static --domains finance,legal --top-n 3 2>&1

# 检查前端构建
cd ui/app && npm run build 2>&1

# 检查 JSON 格式
python -m json.tool reports/skill-audit/finance_legal_top3_l5-static_2026-02-22.json
```

---

## 7. 完整复现时间估算

| 步骤 | 预估时间 |
|------|----------|
| 步骤 1: 运行审计命令 | ~30 秒 |
| 步骤 2: 验证产物 | ~30 秒 |
| 步骤 3: 启动前端 | ~2 分钟 |
| 步骤 4: 契约校验测试 | ~1 分钟 |
| **总计** | **~4 分钟** |

---

## 8. 关键文件清单

| 文件 | 用途 |
|------|------|
| `scripts/skillforge_audit.py` | 统一审计入口命令 |
| `configs/audit_policy_v1.json` | 审计策略配置 |
| `schemas/skill_audit_report.schema.json` | JSON Schema 契约定义 |
| `ui/app/src/pages/audit/SkillAuditPage.tsx` | 前端审计结果页 |
| `ui/app/src/app/router.tsx` | 路由配置 |

---

## 9. Evidence References

| ID | Kind | Locator |
|----|------|---------|
| EV-T62-GATE | LOG | Gate self-check passed |
| EV-T62-DEMO | FILE | docs/2026-02-22/DEMO_STEPS_P1.md |

---

*文档结束*
