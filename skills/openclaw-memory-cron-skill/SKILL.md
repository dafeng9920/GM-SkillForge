---
name: openclaw-memory-cron-skill
description: OpenClaw 记忆库定时自动化清理技能。解决由于历史会话堆积导致的 Token 溢出故障，支持备份自动轮转。
---

# openclaw-memory-cron-skill

## 适用场景
- 需要无人值守自动维护 OpenClaw 会话记忆空间。
- 确保存储空间不被无限增长的 SQLite 和 JSONL 文件打爆。
- 自动清理过期备份（默认保留 7 天）。

## 输入参数
```yaml
input:
  project_dir: "/root/openclaw-box"  # 项目根目录
  auto_clean_hour: 3               # 每天凌晨几点清理 (0-23)
  backup_retain_days: 7            # 备份保留天数
```

## 执行机制
1. **Cron 安装**：通过 `scripts/setup_cron.py` 将定时任务挂载到服务器系统的 Crontab。
2. **清理逻辑**：由 `scripts/auto_clean.sh` 执行：
   - 停止 `openclaw-agent` 容器。
   - 备份当前状态至 `data/.backup/auto_YYYYMMDD`。
   - 删除所有 `.jsonl` 和 `main.sqlite`。
   - 执行 `find -mtime` 删除旧备份。
   - 重启容器。

## 部署命令
在服务器上执行：
```bash
python3 /root/openclaw-box/skills/openclaw-memory-cron-skill/scripts/setup_cron.py
```

## 交付物
- 自动清理脚本：`scripts/auto_clean.sh`
- 系统定时条目：`crontab -l` 见 `* * * * * bash ...auto_clean.sh`
