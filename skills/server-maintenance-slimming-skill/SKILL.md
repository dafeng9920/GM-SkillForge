---
name: server-maintenance-slimming-skill
description: 服务器通用瘦身与运维维护技能。用于回收 Docker、系统日志、包管理组件占用的磁盘空间，提升系统稳定性。
---

# server-maintenance-slimming-skill

## 适用场景
- 开发服务器磁盘占用率超过 60%。
- Docker 堆积了大量悬空镜像 (Dangling Images)。
- 系统日志 `/var/log/journal` 占用过大。
- Node.js/Python 依赖包缓存冗余。

## 核心维护操作 (SOP)

### Level 1: 预防性清理 (推荐每两周一次)
执行脚本回收常规冗余：
```bash
bash skills/server-maintenance-slimming-skill/scripts/slim_server.sh
```

### Level 2: 深度瘦身 (当磁盘报警时)
1. **清理未使用的全量镜像**：
   ```bash
   docker image prune -a -f
   ```
2. **分析大头目录**：
   ```bash
   du -ah / | sort -rh | head -15
   ```
3. **定位大型应用组件**：
   例如：清理 OpenClaw 的不常用扩展（qqbot, wecom）。

## 关键命令参考
- **日志回收**：`journalctl --vacuum-size=100M`
- **Docker 瘦身**：`docker system prune -f`
- **Node 缓存**：`pnpm store prune`

## 交付物
- 自动化瘦身脚本：`scripts/slim_server.sh`
- 空间占位清单：见 `du -ah` 指令集

## 依赖
- Docker 环境
- Linux `journald` 服务
