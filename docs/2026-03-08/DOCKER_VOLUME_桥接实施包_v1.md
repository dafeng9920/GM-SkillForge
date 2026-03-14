# DOCKER_VOLUME 桥接实施包 v1

## 实施目标：建立从云端到宿主机的资产自动流转链

### 1. 宿主机准备 (云服务器终端执行)

```bash
cd /root/openclaw-box
# 创建 Dropzone 及其子结构
mkdir -p dropzone/audit_logs
mkdir -p dropzone/evidence
chmod -R 777 dropzone  # 确保 Docker 内部用户可写
```

### 2. 挂载配置更新 (docker-compose.yaml)

请将 `openclaw_core` 的 `volumes` 部分更新为以下结构：

```yaml
services:
  openclaw_core:
    # ... 其他配置 ...
    volumes:
      # 权限降级挂载：主仓只读
      - ./skillforge:/home/node/app:ro
      - ./docs:/home/node/docs:ro
      - ./skills:/home/node/skills:ro
      # 交付专用通道：Dropzone 可写
      - ./dropzone:/home/node/dropzone:rw
      # 状态记忆保持
      - ./data/memory:/home/node/.openclaw:rw
```

### 3. 宿主机吸收链

当前主仓已正式提供以下脚本：

- `scripts/verify_governance_env.sh`
- `scripts/pre_absorb_check.sh`
- `scripts/absorb.sh`

默认变量：

- `APP_ROOT=/root/openclaw-box/skillforge`
- `DROPZONE_ROOT=/root/openclaw-box/dropzone`
- `DOCS_ROOT=/root/openclaw-box/docs`

推荐顺序：

```bash
./scripts/verify_governance_env.sh
./scripts/pre_absorb_check.sh <TASK_ID>
./scripts/absorb.sh <TASK_ID>
```

### 4. 履约判定指令 (给 Gemini 的 Prompt)

```text
治理升级通知：
当前云端环境已采用【受控桥接方案】。

你的工作边界：
1. 主仓库 /home/node/app 已被挂载为 READ-ONLY。你不允许直接修改源码。
2. 你的所有产出（Receipt, Report, Handoff）必须写入 /home/node/dropzone/<task_id>/。
3. 任何代码级别的 Fix 必须通过独立补丁文件（.diff 或 .patch）形式交付至 dropzone，由宿主机 absorb 脚本进行合并。

确认接收此治理约束。
```

---
*实施人: Antigravity*
