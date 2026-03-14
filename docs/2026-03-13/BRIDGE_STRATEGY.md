# GM-SkillForge Cloud Bridge Setup Strategy

## 1. 隧道层 (Cloudflare Tunnel)
使用 Cloudflare Tunnel 替代传统的 SSH 代理。
- **优点**：隧道建立在 HTTPS/443 之上，对腾讯云安全组极其友好。
- **配置**：在云端容器内运行 `cloudflared tunnel run <TUNNEL_ID>`。

## 2. 同步层 (Git Sync)
利用本地已有的 Git 环境。
- **逻辑**：
  1. 本地脚本执行 `git commit -m "Skill Update" && git push`。
  2. 云端小龙虾通过定时任务（Cron）或 Webhook 触发 `git pull`。
  3. 执行 `openclaw reload`。

## 3. 本地辅助脚本 (cloud_bridge_sync.ps1)
```powershell
# 伪代码：本地一键同步并请求云端重载
git add .
git commit -m "Auto-sync for cloud execution"
git push origin main
# 通过 Discord 发送指令（需配合小龙虾 Skill）
./send_discord_cmd.ps1 "!system reload-skills"
```

## 4. 当前推荐操作流（云端-本地协作）

当本地 Skill / profile / orchestration 契约改好后，采用下面这条最小闭环：

1. 本地提交改动
   - `git add`
   - `git commit -m "<change summary>"`
   - `git push`

2. 云端同步并重载
   - 云端小龙虾 / OpenClaw 拉取最新代码
   - 执行 reload
   - 保持 tunnel 存活

3. 本地进入云端管理后台验收
   - 浏览器打开 tunnel 域名
   - 进入管理后台
   - 检查 skill 是否已生效
   - 检查 audit / permit / orchestration 路径是否正常

4. 次日或稍后回看结果
   - 查看夜间 / 长时任务执行结果
   - 再做审查、放行或回退

一句话：
**本地定义与提交，云端执行与重载，本地负责验收与裁决。**

## 5. 脚本目标（建议保留）

`scripts/cloud_bridge_sync.ps1` 后续应承担下面这条标准化闭环：

```powershell
./scripts/cloud_bridge_sync.ps1 "这里写本次 Skill / Flow 修改描述"
```

推荐职责：

1. 执行 `git add / commit / push`
2. 提示或触发云端 reload
3. 打开云端管理后台
4. 提醒操作者进入验收

也就是：
**Git Add -> Commit -> Push -> 云端重载 -> 打开后台 -> 验收**

## 6. 安全约束（必须遵守）

下面这些做法可以作为临时调试手段存在，但**不应写成正式长期方案**：

- 不要把真实长期令牌硬编码进脚本
- 不要把永久生效 token 直接写入仓库文档
- 不要把浏览器自动登录依赖在固定明文 token 上

正式方案应当改成：

- 令牌从本地安全存储读取（环境变量 / 本机 secret store）
- tunnel 域名允许更新，不把临时域名当永久契约
- 脚本负责“打开后台并引导登录”，而不是把明文凭证焊死

## 7. 与后续主架构的关系

这条桥接策略后续不是独立小技巧，而是会直接服务于：

- 统一输入
- 状态机裁决
- orchestration API
- 云端长时执行
- 次日验收与 Permit / Audit 回看

也就是说，后面当主骨架继续收口时，这条桥接策略会成为：

**本地提交 -> 云端执行 -> 画布承接 -> 次日验收**

的基础设施之一。
