---
name: google-workspace-skill
description: OpenClaw GuG (WorkspaceCLI) 办公底座。实现智能体与 Google 办公生态（Gmail, Drive, Sheets, Calendar）的高效交互。
---

# google-workspace-skill

## 触发条件

- 需要检索工作邮件或排期
- 需要将数据同步至 Google Sheets 进行图表化展示
- 需要管理云端文档、备份核心知识库

## 操作指令

- `mail_scan`: 扫描特定发件人或关键词的最新邮件。
- `sheet_update`: 动态更新表格数据（用于展示量化收益或任务进度）。
- `drive_backup`: 自动将本地 `archive/` 目录同步至云端安全目录。

## 特色功能 (GuG Logic)

- **Context Link**: 自动将当前任务与相关的 Calendar 事件链接。
- **Auto-Report**: 每日生成的 `daily_briefing` 会自动通过 Gmail 发送给 Commander 或同步至 Drive 归档。

## DoD

- [ ] OAuth2 认证链路已在本地系统跑通
- [ ] `workspace_cli.py` 辅助脚本可被智能体调用
- [ ] 具备文件/邮件级别的隐私过滤逻辑
