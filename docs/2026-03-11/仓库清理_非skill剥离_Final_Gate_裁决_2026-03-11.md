# 仓库清理 + 非 skill 剥离 Final Gate 裁决

- 日期：2026-03-11
- Final Gate：Codex / 主控
- 范围：
  - `CLEANUP-EXEC-01`
  - `CLEANUP-EXEC-02`
  - `CLEANUP-EXEC-03`

## 一、裁决结论

- `CLEANUP-EXEC-01`：`ALLOW`
- `CLEANUP-EXEC-02`：`ALLOW`
- `CLEANUP-EXEC-03`：`ALLOW`
- 合并结论：`ALLOW`

## 二、本轮已正式成立

以下三项现已正式成立：

1. `.gitignore` 收口已完成  
2. 根目录散落文件第一次分类已完成  
3. 非 skill 主线业务边界冻结已完成  

## 三、主线口径封口

从本裁决起，`SkillForge` 主线只看 `skill` 本身及其直接支撑层，不再将以下业务混入主线完成度判断：

### 已冻结为非主线业务

- `SEO` 板块
  - `pseo/`
  - `export-seo/`
  - 根目录 `*-ai-seo-checker.html`
  - 相关 SEO 审计页面与产物

- `量化` 板块
  - `adapters/quant/`
  - `quant-system/`
  - `demo_trading_data/`
  - `trading_data/`
  - `check_akshare_funcs.py`
  - `check_institution.py`
  - 相关量化基础设施脚本

## 四、准确口径

本轮成立的是：

- `SEO` 与 `量化` 已完成 **边界剥离**
- 它们已从 `SkillForge` 主线判断中移出

本轮没有宣称的是：

- `SEO` 已物理迁出完成
- `量化` 已物理迁出完成
- 独立仓迁移已经执行完成

一句话：

- **逻辑上已剥离**
- **物理上未迁走**

## 五、主线保留范围

当前继续作为 `SkillForge` 主线范围的核心/辅助层：

- `skills/`
- `skillforge/`
- `core/`
- `schemas/`
- `contracts/`
- `orchestration/`
- `scripts/`
- `configs/`
- `permits/`
- `docs/`
- `workflows/`

## 六、后续动作

后续若继续处理 `SEO` 或 `量化`，一律按以下口径：

- 作为支线任务推进
- 不参与 `SkillForge` 主线封板判断
- 不得再混写为“主线完成度证据”

## 七、Final Gate 判断

- 当前判断：`ALLOW`

理由：

- `CLEANUP-EXEC-01 / 02 / 03` 已完成三权闭环
- P0 范围内的仓库清理与边界冻结已完成
- “主线只看 skill，SEO/量化为支线” 的系统职能边界已明确

一句话封口：

- `SkillForge` 主线就是 `skill` 本身；`SEO` 和 `量化` 自此只按支线任务管理，不再混入主线标的。
